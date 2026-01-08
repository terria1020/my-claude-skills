# Container Configuration Validation

## Dockerfile

### hadolint (recommended)

Dockerfile linter with best practice checks:

```bash
# Single file
hadolint Dockerfile

# With config
hadolint --config .hadolint.yaml Dockerfile

# Ignore specific rules
hadolint --ignore DL3008 --ignore DL3009 Dockerfile

# Output format
hadolint --format json Dockerfile
```

**Common rules:**

| Rule | Description |
|------|-------------|
| DL3008 | Pin apt package versions |
| DL3009 | Delete apt cache |
| DL3015 | Avoid additional packages |
| DL3025 | Use JSON for CMD |

### docker build --check (Docker 25+)

Validates Dockerfile without building:

```bash
docker build --check .
docker build --check -f Dockerfile.dev .
```

### Basic Syntax Validation

If no linter available:

```bash
# Parse Dockerfile (basic validation)
docker build --no-cache --progress=plain -f Dockerfile . 2>&1 | head -20
```

### nerdctl (containerd)

Docker-compatible CLI for containerd:

```bash
# Build with syntax check
nerdctl build .
nerdctl build -f Dockerfile.dev .

# With lima (macOS)
lima nerdctl build .
lima nerdctl build -f Dockerfile.dev .
```

### Podman

Daemonless container engine:

```bash
# Build Dockerfile
podman build .
podman build -f Dockerfile.dev .

# Validate Dockerfile syntax (parse only)
podman build --no-cache -f Dockerfile . 2>&1 | head -20
```

## Container Runtime Detection

Detect which container runtime is available:

```bash
# Priority order: docker > nerdctl > podman
if command -v docker &>/dev/null; then
    RUNTIME="docker"
elif command -v nerdctl &>/dev/null; then
    RUNTIME="nerdctl"
elif command -v lima &>/dev/null && lima nerdctl version &>/dev/null; then
    RUNTIME="lima nerdctl"
elif command -v podman &>/dev/null; then
    RUNTIME="podman"
else
    echo "No container runtime found"
fi
```

## Docker Compose

### Validate Configuration

```bash
# Validate and show config
docker compose config

# Quiet validation (errors only)
docker compose config -q

# Specific file
docker compose -f docker-compose.yml config -q

# Multiple files
docker compose -f docker-compose.yml -f docker-compose.override.yml config -q
```

**Success**: No output (quiet mode) or shows resolved config

**Failure**: Shows parsing errors or invalid syntax

### File Detection

| Filename | Version |
|----------|---------|
| `docker-compose.yml` | Standard |
| `docker-compose.yaml` | Standard |
| `compose.yml` | Compose V2 |
| `compose.yaml` | Compose V2 |

### nerdctl compose

```bash
# Validate config
nerdctl compose config
nerdctl compose config -q

# With lima (macOS)
lima nerdctl compose config
lima nerdctl compose -f docker-compose.yml config -q
```

### Podman Compose

```bash
# podman-compose (Python-based, separate install)
podman-compose config
podman-compose -f docker-compose.yml config

# podman compose (built-in, Podman 3.0+)
podman compose config
podman compose -f docker-compose.yml config
```

## Kubernetes Manifests

### kubectl dry-run

Validates against Kubernetes API schemas:

```bash
# Client-side validation only
kubectl apply --dry-run=client -f manifest.yaml

# Server-side validation (requires cluster access)
kubectl apply --dry-run=server -f manifest.yaml

# All files in directory
kubectl apply --dry-run=client -f ./k8s/

# Recursive
kubectl apply --dry-run=client -R -f ./k8s/
```

**Success**: Shows `<resource> created (dry run)`

**Failure**: Shows validation errors

### kubeval (offline validation)

Validates without cluster access:

```bash
# Single file
kubeval manifest.yaml

# Directory
kubeval ./k8s/*.yaml

# Specific Kubernetes version
kubeval --kubernetes-version 1.28.0 manifest.yaml

# Strict mode
kubeval --strict manifest.yaml
```

### kubeconform (kubeval successor)

```bash
# Single file
kubeconform manifest.yaml

# With strict mode
kubeconform -strict manifest.yaml

# Specific version
kubeconform -kubernetes-version 1.28.0 manifest.yaml
```

### YAML Syntax Only

Basic YAML validation without K8s schema:

```bash
# Python yaml module
python3 -c "import yaml; yaml.safe_load(open('manifest.yaml'))"

# yq
yq eval '.' manifest.yaml > /dev/null
```

## K8s Resource Detection

Identify Kubernetes manifests by content:

```yaml
# Deployment
apiVersion: apps/v1
kind: Deployment

# Service
apiVersion: v1
kind: Service

# ConfigMap
apiVersion: v1
kind: ConfigMap

# Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
```

**Detection command:**

```bash
grep -l "kind: Deployment\|kind: Service\|kind: Pod" *.yaml
```

## Tool Installation Check

```bash
# Docker
command -v docker && docker --version

# nerdctl
command -v nerdctl && nerdctl --version

# lima (macOS)
command -v lima && lima --version
lima nerdctl version 2>/dev/null

# Podman
command -v podman && podman --version

# podman-compose
command -v podman-compose && podman-compose --version

# hadolint
command -v hadolint && hadolint --version

# kubectl
command -v kubectl && kubectl version --client

# kubeval
command -v kubeval && kubeval --version

# kubeconform
command -v kubeconform && kubeconform -v
```

## Example Output

**hadolint error:**

```
Dockerfile:15 DL3008 warning: Pin versions in apt get install
Dockerfile:20 DL3025 warning: Use arguments JSON notation for CMD
```

**docker compose error:**

```
validating compose.yaml: services.web.ports.0 must be a string
```

**kubectl dry-run error:**

```
error: error validating "deployment.yaml": error validating data:
ValidationError(Deployment.spec.template.spec.containers[0]):
unknown field "imagePullpolicy" in io.k8s.api.core.v1.Container
```

**kubeval error:**

```
WARN - deployment.yaml contains an invalid Deployment -
spec.replicas: Invalid type. Expected: integer, given: string
```
