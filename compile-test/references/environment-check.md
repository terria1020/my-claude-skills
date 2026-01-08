# Environment Check Guide

Pre-flight checklist before running compile tests.

## Table of Contents

1. [Container Environment](#container-environment)
2. [Python Environment](#python-environment)
3. [Node Environment](#node-environment)
4. [Java Environment](#java-environment)
5. [Network Connectivity](#network-connectivity)
6. [Tool Installation](#tool-installation)

## Container Environment

Detect if running inside a container:

```bash
# Docker
[ -f /.dockerenv ] && echo "Running in Docker"

# Podman
[ -f /run/.containerenv ] && echo "Running in Podman"

# Generic cgroup check
grep -q 'docker\|kubepods\|containerd' /proc/1/cgroup 2>/dev/null && echo "Containerized"
```

**Implications:**

- Volume mounts may affect file access
- Some system tools may be unavailable
- Network isolation may apply
- Resource limits (memory/CPU) may be restricted

## Python Environment

Check virtual environment status:

```bash
# Check if in virtualenv/venv
[ -n "$VIRTUAL_ENV" ] && echo "venv active: $VIRTUAL_ENV"

# Check if in conda
[ -n "$CONDA_DEFAULT_ENV" ] && echo "conda active: $CONDA_DEFAULT_ENV"

# Check pyenv
command -v pyenv &>/dev/null && echo "pyenv: $(pyenv version-name)"

# List available Python versions
python3 --version
which python3
```

**Before compile test:**

- Activate appropriate virtual environment if needed
- Verify correct Python version for project
- Check if dependencies are installed: `pip list | grep -i <package>`

## Node Environment

Check Node.js environment:

```bash
# Node version manager check
[ -n "$FNM_DIR" ] && echo "fnm active"
[ -n "$NVM_DIR" ] && echo "nvm active"
command -v volta &>/dev/null && echo "volta installed"

# Current versions
node --version
npm --version

# Check node_modules
[ -d node_modules ] && echo "node_modules exists" || echo "Run npm install first"

# Check package manager
[ -f package-lock.json ] && echo "Uses npm"
[ -f yarn.lock ] && echo "Uses yarn"
[ -f pnpm-lock.yaml ] && echo "Uses pnpm"
```

**Before compile test:**

- Ensure correct Node version (check `.nvmrc`, `.node-version`, `package.json#engines`)
- Run `npm install` / `yarn` / `pnpm install` if node_modules missing

## Java Environment

Check Java environment:

```bash
# Java version
java --version
javac --version
echo "JAVA_HOME: $JAVA_HOME"

# Build tool detection
[ -f pom.xml ] && echo "Maven project"
[ -f build.gradle ] && echo "Gradle project (Groovy DSL)"
[ -f build.gradle.kts ] && echo "Gradle project (Kotlin DSL)"

# Maven wrapper
[ -f mvnw ] && echo "Maven wrapper available"

# Gradle wrapper
[ -f gradlew ] && echo "Gradle wrapper available"
```

**Before compile test:**

- Use wrapper scripts (`./mvnw`, `./gradlew`) when available
- Check required Java version in `pom.xml` or `build.gradle`

## Network Connectivity

Check network access:

```bash
# Quick connectivity test
curl -s --connect-timeout 3 https://google.com > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Network: Online"
else
    echo "Network: Offline or Air-gapped"
fi

# Check specific registries
curl -s --connect-timeout 3 https://pypi.org > /dev/null 2>&1 && echo "PyPI: accessible"
curl -s --connect-timeout 3 https://registry.npmjs.org > /dev/null 2>&1 && echo "npm: accessible"
curl -s --connect-timeout 3 https://repo1.maven.org > /dev/null 2>&1 && echo "Maven Central: accessible"
```

**Air-gapped network implications:**

- Cannot download missing dependencies
- Must use pre-installed packages or local mirrors
- Skip dependency resolution steps
- Inform user if dependency installation is needed

## Tool Installation

Verify required tools:

```bash
# Python tools
command -v mypy &>/dev/null && echo "mypy: installed" || echo "mypy: NOT installed"
command -v ruff &>/dev/null && echo "ruff: installed" || echo "ruff: NOT installed"
command -v pylint &>/dev/null && echo "pylint: installed" || echo "pylint: NOT installed"

# Node tools (check local)
[ -f node_modules/.bin/tsc ] && echo "tsc: installed locally"
[ -f node_modules/.bin/eslint ] && echo "eslint: installed locally"

# Container tools
command -v docker &>/dev/null && echo "docker: installed" || echo "docker: NOT installed"
command -v hadolint &>/dev/null && echo "hadolint: installed" || echo "hadolint: NOT installed"
command -v kubectl &>/dev/null && echo "kubectl: installed" || echo "kubectl: NOT installed"
command -v kubeval &>/dev/null && echo "kubeval: installed" || echo "kubeval: NOT installed"
```

**When tool is missing:**

- Report which tool is needed
- Suggest installation command if online
- For air-gapped: inform user to install manually
