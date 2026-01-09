#!/usr/bin/env python3
"""
Container Environment Detection Script

Detects available container runtimes, orchestration tools, and environment type.
Supports Linux, macOS, and Windows.
"""

import subprocess
import platform
import shutil
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class RuntimeInfo:
    name: str
    available: bool
    version: Optional[str] = None
    path: Optional[str] = None
    context: Optional[str] = None  # For Lima/Docker Desktop context


@dataclass
class EnvironmentReport:
    os_type: str
    os_version: str
    architecture: str
    runtimes: list = field(default_factory=list)
    orchestration: list = field(default_factory=list)
    lima_instances: list = field(default_factory=list)
    environment_type: str = "unknown"  # native, lima, docker-desktop, etc.
    recommended_runtime: Optional[str] = None


def run_command(cmd: list, timeout: int = 10) -> tuple[bool, str]:
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
        return False, ""


def get_version(cmd: list) -> Optional[str]:
    """Get version string from a command."""
    success, output = run_command(cmd)
    if success and output:
        # Extract first line, common version format
        first_line = output.split('\n')[0]
        return first_line
    return None


def check_runtime(name: str, cmd: str, version_args: list = None) -> RuntimeInfo:
    """Check if a container runtime is available."""
    path = shutil.which(cmd)
    if not path:
        return RuntimeInfo(name=name, available=False)

    version_args = version_args or ["--version"]
    version = get_version([cmd] + version_args)

    return RuntimeInfo(
        name=name,
        available=True,
        version=version,
        path=path
    )


def detect_lima_instances() -> list[dict]:
    """Detect Lima VM instances."""
    if not shutil.which("limactl"):
        return []

    success, output = run_command(["limactl", "list", "--json"])
    if not success:
        return []

    try:
        instances = json.loads(output) if output else []
        return [
            {
                "name": inst.get("name", ""),
                "status": inst.get("status", ""),
                "arch": inst.get("arch", ""),
                "cpus": inst.get("cpus", 0),
                "memory": inst.get("memory", 0),
            }
            for inst in instances
        ]
    except json.JSONDecodeError:
        return []


def detect_docker_context() -> Optional[str]:
    """Detect current Docker context (desktop, colima, etc.)."""
    success, output = run_command(["docker", "context", "show"])
    if success:
        return output
    return None


def determine_environment_type(runtimes: list[RuntimeInfo], lima_instances: list) -> str:
    """Determine the environment type based on detected tools."""
    docker_context = detect_docker_context()

    if docker_context:
        if "desktop" in docker_context.lower():
            return "docker-desktop"
        elif "colima" in docker_context.lower():
            return "colima"
        elif "rancher" in docker_context.lower():
            return "rancher-desktop"

    if lima_instances:
        running = [i for i in lima_instances if i.get("status") == "Running"]
        if running:
            return "lima"

    # Check for native runtimes
    native_runtimes = ["podman", "nerdctl", "docker", "crictl"]
    for rt in runtimes:
        if rt.available and rt.name.lower() in native_runtimes:
            return "native"

    return "unknown"


def recommend_runtime(runtimes: list[RuntimeInfo], env_type: str) -> Optional[str]:
    """Recommend the best available runtime."""
    priority = ["docker", "nerdctl", "podman", "crictl"]

    available = {rt.name.lower(): rt for rt in runtimes if rt.available}

    for name in priority:
        if name in available:
            return name

    return None


def detect_environment() -> EnvironmentReport:
    """Detect full container environment."""
    report = EnvironmentReport(
        os_type=platform.system(),
        os_version=platform.release(),
        architecture=platform.machine()
    )

    # Container runtimes
    runtime_checks = [
        ("docker", "docker", ["--version"]),
        ("podman", "podman", ["--version"]),
        ("nerdctl", "nerdctl", ["--version"]),
        ("crictl", "crictl", ["--version"]),
        ("ctr", "ctr", ["--version"]),  # containerd CLI
    ]

    for name, cmd, version_args in runtime_checks:
        rt = check_runtime(name, cmd, version_args)
        report.runtimes.append(rt)

    # Orchestration tools
    orch_checks = [
        ("kubectl", "kubectl", ["version", "--client", "--short"]),
        ("k3s", "k3s", ["--version"]),
        ("minikube", "minikube", ["version", "--short"]),
        ("kind", "kind", ["version"]),
    ]

    for name, cmd, version_args in orch_checks:
        rt = check_runtime(name, cmd, version_args)
        report.orchestration.append(rt)

    # Lima instances
    report.lima_instances = detect_lima_instances()

    # Determine environment type
    report.environment_type = determine_environment_type(
        report.runtimes,
        report.lima_instances
    )

    # Recommend runtime
    report.recommended_runtime = recommend_runtime(
        report.runtimes,
        report.environment_type
    )

    return report


def format_report(report: EnvironmentReport, output_format: str = "text") -> str:
    """Format the environment report."""
    if output_format == "json":
        return json.dumps(asdict(report), indent=2, default=str)

    lines = [
        "=" * 60,
        "Container Environment Report",
        "=" * 60,
        "",
        f"OS: {report.os_type} {report.os_version} ({report.architecture})",
        f"Environment Type: {report.environment_type}",
        f"Recommended Runtime: {report.recommended_runtime or 'None detected'}",
        "",
        "Container Runtimes:",
        "-" * 40,
    ]

    for rt in report.runtimes:
        status = "[OK]" if rt.available else "[--]"
        version = f" - {rt.version}" if rt.version else ""
        lines.append(f"  {status} {rt.name}{version}")

    lines.extend([
        "",
        "Orchestration Tools:",
        "-" * 40,
    ])

    for orch in report.orchestration:
        status = "[OK]" if orch.available else "[--]"
        version = f" - {orch.version}" if orch.version else ""
        lines.append(f"  {status} {orch.name}{version}")

    if report.lima_instances:
        lines.extend([
            "",
            "Lima Instances:",
            "-" * 40,
        ])
        for inst in report.lima_instances:
            status = "[Running]" if inst["status"] == "Running" else f"[{inst['status']}]"
            lines.append(f"  {status} {inst['name']} ({inst['arch']})")

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Detect container environment and available runtimes"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Only output recommended runtime"
    )

    args = parser.parse_args()

    report = detect_environment()

    if args.quiet:
        print(report.recommended_runtime or "none")
    else:
        print(format_report(report, args.format))

    # Exit with error if no runtime found
    sys.exit(0 if report.recommended_runtime else 1)


if __name__ == "__main__":
    main()
