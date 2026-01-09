#!/usr/bin/env python3
"""
Container Build Validation Script

Validates Dockerfile builds and container execution.
Supports multiple container runtimes: docker, podman, nerdctl.
"""

import subprocess
import sys
import os
import tempfile
import time
import argparse
import json
import shutil
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path


@dataclass
class ValidationResult:
    step: str
    success: bool
    message: str
    duration_seconds: float = 0.0
    output: str = ""
    error: str = ""


@dataclass
class BuildReport:
    dockerfile_path: str
    runtime: str
    image_tag: str
    results: list = field(default_factory=list)
    overall_success: bool = False
    total_duration: float = 0.0


def run_command(
    cmd: list,
    timeout: int = 300,
    cwd: str = None
) -> tuple[bool, str, str, float]:
    """Run command and return (success, stdout, stderr, duration)."""
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        duration = time.time() - start
        return (
            result.returncode == 0,
            result.stdout,
            result.stderr,
            duration
        )
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout}s", time.time() - start
    except FileNotFoundError as e:
        return False, "", str(e), time.time() - start


def detect_runtime() -> Optional[str]:
    """Detect available container runtime."""
    for runtime in ["docker", "podman", "nerdctl"]:
        if shutil.which(runtime):
            return runtime
    return None


def validate_dockerfile_syntax(dockerfile_path: str) -> ValidationResult:
    """Validate Dockerfile syntax (basic check)."""
    start = time.time()

    if not os.path.exists(dockerfile_path):
        return ValidationResult(
            step="dockerfile_syntax",
            success=False,
            message=f"Dockerfile not found: {dockerfile_path}",
            duration_seconds=time.time() - start
        )

    with open(dockerfile_path, 'r') as f:
        content = f.read()

    # Basic syntax checks
    lines = content.strip().split('\n')
    if not lines:
        return ValidationResult(
            step="dockerfile_syntax",
            success=False,
            message="Dockerfile is empty",
            duration_seconds=time.time() - start
        )

    # Check for FROM instruction
    has_from = any(
        line.strip().upper().startswith('FROM ')
        for line in lines
        if not line.strip().startswith('#')
    )

    if not has_from:
        return ValidationResult(
            step="dockerfile_syntax",
            success=False,
            message="Dockerfile must have at least one FROM instruction",
            duration_seconds=time.time() - start
        )

    return ValidationResult(
        step="dockerfile_syntax",
        success=True,
        message="Dockerfile syntax is valid",
        duration_seconds=time.time() - start
    )


def build_image(
    runtime: str,
    dockerfile_path: str,
    image_tag: str,
    build_context: str = None,
    build_args: dict = None,
    no_cache: bool = False
) -> ValidationResult:
    """Build container image."""
    dockerfile_dir = os.path.dirname(os.path.abspath(dockerfile_path))
    context = build_context or dockerfile_dir

    cmd = [runtime, "build", "-t", image_tag, "-f", dockerfile_path]

    if no_cache:
        cmd.append("--no-cache")

    if build_args:
        for key, value in build_args.items():
            cmd.extend(["--build-arg", f"{key}={value}"])

    cmd.append(context)

    success, stdout, stderr, duration = run_command(cmd, timeout=600, cwd=context)

    return ValidationResult(
        step="build_image",
        success=success,
        message="Image built successfully" if success else "Image build failed",
        duration_seconds=duration,
        output=stdout,
        error=stderr
    )


def run_container(
    runtime: str,
    image_tag: str,
    test_command: list = None,
    timeout: int = 30
) -> ValidationResult:
    """Run container and verify it starts."""
    container_name = f"validate-{int(time.time())}"

    # Run container with test command or just check if it can start
    if test_command:
        cmd = [runtime, "run", "--rm", "--name", container_name, image_tag] + test_command
    else:
        # Just try to run with echo to verify container can start
        cmd = [runtime, "run", "--rm", "--name", container_name, image_tag, "echo", "container-ok"]

    success, stdout, stderr, duration = run_command(cmd, timeout=timeout)

    if success and ("container-ok" in stdout or test_command):
        return ValidationResult(
            step="run_container",
            success=True,
            message="Container runs successfully",
            duration_seconds=duration,
            output=stdout
        )

    return ValidationResult(
        step="run_container",
        success=False,
        message="Container failed to run",
        duration_seconds=duration,
        output=stdout,
        error=stderr
    )


def cleanup_image(runtime: str, image_tag: str) -> ValidationResult:
    """Remove built image."""
    cmd = [runtime, "rmi", "-f", image_tag]
    success, stdout, stderr, duration = run_command(cmd, timeout=60)

    return ValidationResult(
        step="cleanup",
        success=success,
        message="Image cleaned up" if success else "Cleanup failed (non-critical)",
        duration_seconds=duration
    )


def validate_build(
    dockerfile_path: str,
    runtime: str = None,
    image_tag: str = None,
    build_context: str = None,
    skip_run: bool = False,
    skip_cleanup: bool = False,
    no_cache: bool = False
) -> BuildReport:
    """Full build validation pipeline."""
    # Detect runtime if not specified
    if not runtime:
        runtime = detect_runtime()
        if not runtime:
            report = BuildReport(
                dockerfile_path=dockerfile_path,
                runtime="none",
                image_tag="",
                overall_success=False
            )
            report.results.append(ValidationResult(
                step="runtime_detection",
                success=False,
                message="No container runtime found (docker, podman, nerdctl)"
            ))
            return report

    # Generate image tag if not specified
    if not image_tag:
        image_tag = f"validate-test:{int(time.time())}"

    report = BuildReport(
        dockerfile_path=dockerfile_path,
        runtime=runtime,
        image_tag=image_tag
    )

    start_time = time.time()

    # Step 1: Validate Dockerfile syntax
    syntax_result = validate_dockerfile_syntax(dockerfile_path)
    report.results.append(syntax_result)

    if not syntax_result.success:
        report.total_duration = time.time() - start_time
        return report

    # Step 2: Build image
    build_result = build_image(
        runtime, dockerfile_path, image_tag, build_context, no_cache=no_cache
    )
    report.results.append(build_result)

    if not build_result.success:
        report.total_duration = time.time() - start_time
        return report

    # Step 3: Run container (optional)
    if not skip_run:
        run_result = run_container(runtime, image_tag)
        report.results.append(run_result)

    # Step 4: Cleanup (optional)
    if not skip_cleanup:
        cleanup_result = cleanup_image(runtime, image_tag)
        report.results.append(cleanup_result)

    report.total_duration = time.time() - start_time
    report.overall_success = all(
        r.success for r in report.results
        if r.step != "cleanup"  # Cleanup failure is non-critical
    )

    return report


def format_report(report: BuildReport, output_format: str = "text") -> str:
    """Format validation report."""
    if output_format == "json":
        return json.dumps(asdict(report), indent=2)

    lines = [
        "=" * 60,
        "Container Build Validation Report",
        "=" * 60,
        "",
        f"Dockerfile: {report.dockerfile_path}",
        f"Runtime: {report.runtime}",
        f"Image Tag: {report.image_tag}",
        f"Total Duration: {report.total_duration:.2f}s",
        "",
        "Validation Steps:",
        "-" * 40,
    ]

    for result in report.results:
        status = "[PASS]" if result.success else "[FAIL]"
        lines.append(f"  {status} {result.step} ({result.duration_seconds:.2f}s)")
        lines.append(f"         {result.message}")
        if result.error and not result.success:
            # Show first few lines of error
            error_lines = result.error.strip().split('\n')[:3]
            for err in error_lines:
                lines.append(f"         > {err[:70]}")

    lines.extend([
        "",
        "-" * 40,
        f"Overall: {'SUCCESS' if report.overall_success else 'FAILED'}",
        "=" * 60,
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate Dockerfile build and container execution"
    )
    parser.add_argument(
        "dockerfile",
        nargs="?",
        default="Dockerfile",
        help="Path to Dockerfile (default: ./Dockerfile)"
    )
    parser.add_argument(
        "-r", "--runtime",
        choices=["docker", "podman", "nerdctl"],
        help="Container runtime to use (auto-detect if not specified)"
    )
    parser.add_argument(
        "-t", "--tag",
        help="Image tag for build (auto-generated if not specified)"
    )
    parser.add_argument(
        "-c", "--context",
        help="Build context directory (default: Dockerfile directory)"
    )
    parser.add_argument(
        "--skip-run",
        action="store_true",
        help="Skip container run test"
    )
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Skip image cleanup after test"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Build without cache"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )

    args = parser.parse_args()

    report = validate_build(
        dockerfile_path=args.dockerfile,
        runtime=args.runtime,
        image_tag=args.tag,
        build_context=args.context,
        skip_run=args.skip_run,
        skip_cleanup=args.skip_cleanup,
        no_cache=args.no_cache
    )

    print(format_report(report, args.format))
    sys.exit(0 if report.overall_success else 1)


if __name__ == "__main__":
    main()
