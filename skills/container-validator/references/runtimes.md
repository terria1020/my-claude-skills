# Container Runtimes Reference

핵심 명령어만 발췌. 빌드/실행/상태확인에 필요한 명령어 중심.

## Table of Contents

- [Apple Container](#apple-container)
- [Docker](#docker)
- [Podman](#podman)
- [nerdctl](#nerdctl)
- [crictl](#crictl)
- [containerd (ctr)](#containerd-ctr)

---

## Apple Container

[apple/container](https://github.com/apple/container)은 Apple silicon Mac용 OCI 컨테이너 런타임이다. Dockerfile 또는 Containerfile 빌드는 BuildKit에서 수행하며, 컨테이너는 경량 VM으로 실행된다. 사용 전 시스템 서비스를 시작한다.

명령과 옵션은 설치된 Apple Container 릴리스 및 macOS 버전에 따라 달라질 수 있다. 이 문서의 예시는 출발점으로만 사용하고, 실제 검증 전에는 `container --version`, `container <subcommand> --help` 및 사용 중인 릴리스의 공식 문서를 확인한다.

```bash
container --version
container system start
container list --all
```

### Build

```bash
container build --tag myapp:latest --file Dockerfile .
container build --no-cache --tag myapp:latest .
container build --build-arg VERSION=1.0 --tag myapp .
```

### Run

```bash
container run --rm myapp:latest echo container-ok
container run --name myapp --detach --rm -p 8080:80 myapp:latest
container run --env-file .env --volume ${PWD}:/app myapp:latest
```

### Status, logs, cleanup

```bash
container list --all
container logs <container>
container inspect <container-or-image>
container stop <container>
container image list
container image delete myapp:latest
container system stop
```

Apple Container is macOS/Apple-silicon specific. Do not use it as the default in Linux CI; choose Docker, Podman, or nerdctl there. `container k8s`는 로컬 단일 노드 클러스터용 실험 기능이며, 하위 명령과 옵션이 릴리스마다 변경될 수 있다. Kubernetes 검증에는 설치된 버전의 `container k8s --help`와 릴리스 문서를 우선 확인한다.

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

| 기능 | Apple Container | Docker | Podman | nerdctl | crictl |
|------|-----------------|--------|--------|---------|--------|
| Dockerfile 빌드 | O (BuildKit) | O | O | O (BuildKit) | X |
| Docker Compose | X | O | podman-compose | nerdctl compose | X |
| Rootless | X | O | O (기본) | O | - |
| Kubernetes 호환 | △ (experimental, 로컬 단일 노드) | - | O (Pod) | - | O |
| 데몬 필요 | system service | O | X | X (containerd) | X |
