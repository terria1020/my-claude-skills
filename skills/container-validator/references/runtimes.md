# Container Runtimes Reference

핵심 명령어만 발췌. 빌드/실행/상태확인에 필요한 명령어 중심.

## Table of Contents

- [Docker](#docker)
- [Podman](#podman)
- [nerdctl](#nerdctl)
- [crictl](#crictl)
- [containerd (ctr)](#containerd-ctr)

---

## Docker

### Build

```bash
docker build -t <tag> -f <Dockerfile> <context>
docker build --no-cache -t myapp:latest .
docker build --build-arg VERSION=1.0 -t myapp .
```

### Run

```bash
docker run -d --name <name> <image>
docker run -it --rm <image> /bin/sh
docker run -p 8080:80 -v $(pwd):/app <image>
docker run --env-file .env <image>
```

### Status & Logs

```bash
docker ps -a
docker logs -f <container>
docker inspect <container|image>
docker stats
```

### Cleanup

```bash
docker stop <container>
docker rm <container>
docker rmi <image>
docker system prune -af
```

---

## Podman

Podman은 Docker CLI와 대부분 호환됨. rootless 실행이 기본.

### Build

```bash
podman build -t <tag> -f <Dockerfile> <context>
podman build --layers=false -t myapp .
```

### Run

```bash
podman run -d --name <name> <image>
podman run -it --rm <image> /bin/sh
podman run --userns=keep-id -v $(pwd):/app <image>
```

### Status & Logs

```bash
podman ps -a
podman logs -f <container>
podman inspect <container|image>
```

### Rootless 관련

```bash
podman unshare cat /proc/self/uid_map
podman system migrate
```

---

## nerdctl

containerd 기반 Docker 호환 CLI. Lima와 함께 자주 사용.

### Build (BuildKit 필요)

```bash
nerdctl build -t <tag> -f <Dockerfile> <context>
nerdctl build --no-cache -t myapp .
```

### Run

```bash
nerdctl run -d --name <name> <image>
nerdctl run -it --rm <image> /bin/sh
nerdctl run --net=host <image>
```

### Status

```bash
nerdctl ps -a
nerdctl logs <container>
nerdctl inspect <container|image>
```

### Lima 환경에서 사용

```bash
limactl shell default nerdctl build -t myapp .
lima nerdctl run -it --rm alpine
```

---

## crictl

CRI (Container Runtime Interface) 디버깅 도구. 주로 Kubernetes 노드에서 사용.

### 이미지

```bash
crictl pull <image>
crictl images
crictl rmi <image-id>
```

### 컨테이너

```bash
crictl ps -a
crictl logs <container-id>
crictl exec -it <container-id> /bin/sh
crictl inspect <container-id>
```

### Pod

```bash
crictl pods
crictl inspectp <pod-id>
crictl stopp <pod-id>
crictl rmp <pod-id>
```

### 설정

```bash
# /etc/crictl.yaml
runtime-endpoint: unix:///run/containerd/containerd.sock
image-endpoint: unix:///run/containerd/containerd.sock
```

---

## containerd (ctr)

containerd 네이티브 CLI. 디버깅 및 로우레벨 작업용.

### 이미지

```bash
ctr images pull docker.io/library/alpine:latest
ctr images list
ctr images rm <image>
```

### 컨테이너

```bash
ctr run -t --rm docker.io/library/alpine:latest test /bin/sh
ctr containers list
ctr containers rm <container>
```

### 네임스페이스

```bash
ctr namespaces list
ctr -n k8s.io containers list  # Kubernetes 네임스페이스
```

---

## 런타임 비교

| 기능 | Docker | Podman | nerdctl | crictl |
|------|--------|--------|---------|--------|
| Dockerfile 빌드 | O | O | O (BuildKit) | X |
| Docker Compose | O | podman-compose | nerdctl compose | X |
| Rootless | O | O (기본) | O | - |
| Kubernetes 호환 | - | O (Pod) | - | O |
| 데몬 필요 | O | X | X (containerd) | X |
