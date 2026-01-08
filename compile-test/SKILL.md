---
name: compile-test
description: |
  Compile and syntax validation for multi-language projects. Supports Python, Java (native/Maven/Gradle), JavaScript/TypeScript, Dockerfile, Docker Compose, and Kubernetes manifests. Use this skill when: (1) User requests compile/build test with commands like "/compile-test" or "컴파일 테스트", (2) Before creating commits or PRs to validate code, (3) Checking syntax errors in container configuration files. Includes environment pre-checks for containerized, virtual environments, and air-gapped networks.
allowed-tools:
  # Environment checks
  - Bash(command -v *)
  - Bash(which *)
  - Bash(* --version)
  - Bash(curl -s --connect-timeout * https://google.com *)
  - Bash([ -f * ] && echo *)
  - Bash([ -d * ] && echo *)
  # Python
  - Bash(python3 -m py_compile *)
  - Bash(python -m py_compile *)
  - Bash(mypy *)
  - Bash(ruff check *)
  - Bash(pylint *)
  # Java
  - Bash(javac *)
  - Bash(mvn compile*)
  - Bash(./mvnw compile*)
  - Bash(gradle compile*)
  - Bash(./gradlew compile*)
  # JavaScript/TypeScript
  - Bash(tsc --noEmit*)
  - Bash(npx tsc --noEmit*)
  - Bash(npx eslint *)
  # Container (Docker, nerdctl, Podman)
  - Bash(hadolint *)
  - Bash(docker build --check *)
  - Bash(docker compose config*)
  - Bash(nerdctl build *)
  - Bash(nerdctl compose config*)
  - Bash(lima nerdctl build *)
  - Bash(lima nerdctl compose config*)
  - Bash(podman build *)
  - Bash(podman-compose config*)
  - Bash(podman compose config*)
  # Kubernetes
  - Bash(kubectl apply --dry-run=client *)
  - Bash(kubeval *)
  # File detection
  - Bash(find * -name *)
  - Bash(ls *)
---

# Compile Test

Multi-language compile and syntax validation skill with environment awareness.

## Workflow

```
1. Environment Check    →  Verify execution environment capabilities
2. Detect Project Type  →  Identify language/framework from files
3. Tool Availability    →  Check if required tool exists, SKIP if missing
4. Run Compile Test     →  Execute appropriate validation command
5. (Optional) Lint      →  Run linter if requested
6. Report Results       →  Show errors or success status
```

## Critical Rule: Tool Availability Check

**BEFORE running any compile/validation command, check if the tool exists.**

If tool is NOT available:

1. SKIP the validation for that language/type
2. Report which tool is missing
3. Suggest installation if online, or inform user to install manually

```bash
# Check tool existence pattern
command -v <tool> &>/dev/null || { echo "SKIP: <tool> not installed"; return; }
```

| Type | Required Tool | Check Command |
|------|---------------|---------------|
| Python | `python3` | `command -v python3` |
| Python (type) | `mypy` | `command -v mypy` |
| Java | `javac` | `command -v javac` |
| Maven | `mvn` or `./mvnw` | `command -v mvn \|\| [ -f mvnw ]` |
| Gradle | `gradle` or `./gradlew` | `command -v gradle \|\| [ -f gradlew ]` |
| TypeScript | `tsc` | `[ -f node_modules/.bin/tsc ] \|\| command -v tsc` |
| Dockerfile | `hadolint`, `docker`, `nerdctl`, `podman` | `command -v hadolint \|\| command -v docker \|\| command -v nerdctl \|\| command -v podman` |
| Compose | `docker`, `nerdctl`, `podman` | `command -v docker \|\| command -v nerdctl \|\| command -v podman` |
| Kubernetes | `kubectl` or `kubeval` | `command -v kubectl \|\| command -v kubeval` |

**Example skip output:**

```
Compile Test: PARTIAL
- Python syntax: OK (3 files)
- Kubernetes manifest: SKIPPED (kubectl not installed)
  → Install: brew install kubectl (or use package manager)
```

## Step 1: Environment Check

Before running any compile test, verify the environment. See [environment-check.md](references/environment-check.md) for detailed checklist.

**Quick checks:**

```bash
# Container environment
[ -f /.dockerenv ] && echo "Docker container"
[ -f /run/.containerenv ] && echo "Podman container"

# Network (air-gapped check)
curl -s --connect-timeout 3 https://google.com > /dev/null && echo "Online" || echo "Offline/Air-gapped"

# Python
python3 --version && which python3

# Node
node --version && which node
[ -d node_modules ] && echo "node_modules exists"

# Java
java --version && which java
[ -f pom.xml ] && echo "Maven project"
[ -f build.gradle ] && echo "Gradle project"
```

## Step 2: Detect Project Type

| Indicator | Project Type | Reference |
|-----------|--------------|-----------|
| `*.py`, `pyproject.toml`, `requirements.txt` | Python | [python.md](references/python.md) |
| `*.java` (no build tool) | Java Native | [java.md](references/java.md) |
| `pom.xml` | Maven | [java.md](references/java.md) |
| `build.gradle`, `build.gradle.kts` | Gradle | [java.md](references/java.md) |
| `package.json` + `*.js` | JavaScript | [js-ts.md](references/js-ts.md) |
| `tsconfig.json`, `*.ts` | TypeScript | [js-ts.md](references/js-ts.md) |
| `Dockerfile` | Dockerfile | [container.md](references/container.md) |
| `docker-compose.yml`, `compose.yaml` | Docker Compose | [container.md](references/container.md) |
| `kind: Deployment`, `apiVersion: apps/v1` | Kubernetes | [container.md](references/container.md) |

## Step 3: Compile Test Commands

### Quick Reference

| Type | Compile Command | Success Indicator |
|------|-----------------|-------------------|
| Python | `python -m py_compile <file>` | No output = success |
| Python (type) | `mypy <file>` | Exit code 0 |
| Java | `javac <file>` | No errors |
| Maven | `mvn compile -q` | BUILD SUCCESS |
| Gradle | `./gradlew compileJava` | BUILD SUCCESSFUL |
| TypeScript | `tsc --noEmit` | Exit code 0 |
| Dockerfile | `hadolint <file>` or `docker/nerdctl/podman build --check .` | No errors |
| Compose | `docker/nerdctl/podman compose config -q` | No output = valid |
| Kubernetes | `kubectl apply --dry-run=client -f <file>` | created (dry run) |

For detailed commands and options, refer to the language-specific reference files.

## Step 4: Lint (Optional)

Run only when explicitly requested. Execute after compile test passes.

| Type | Lint Command |
|------|--------------|
| Python | `ruff check <file>` or `pylint <file>` |
| Java | `checkstyle -c /google_checks.xml <file>` |
| JavaScript/TypeScript | `npx eslint <file>` |

## Output Format

Report results concisely:

**Success:**

```
Compile Test: PASSED
- Python syntax: OK (3 files)
- mypy type check: OK
```

**Failure:**

```
Compile Test: FAILED
- File: src/main.py:42
- Error: SyntaxError: unexpected indent
```

Do not attempt auto-fix. Report errors only and let user decide next steps.
