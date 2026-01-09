# Orchestration Tools Reference

Kubernetes 및 경량 오케스트레이션 도구의 핵심 명령어.

## Table of Contents

- [kubectl](#kubectl)
- [k3s](#k3s)
- [minikube](#minikube)
- [kind](#kind)
- [Lima + k3s](#lima--k3s)

---

## kubectl

### 클러스터 정보

```bash
kubectl cluster-info
kubectl get nodes
kubectl config current-context
kubectl config get-contexts
```

### Pod 관리

```bash
kubectl get pods -A
kubectl describe pod <pod-name>
kubectl logs -f <pod-name>
kubectl exec -it <pod-name> -- /bin/sh
```

### Deployment

```bash
kubectl apply -f deployment.yaml
kubectl get deployments
kubectl rollout status deployment/<name>
kubectl rollout restart deployment/<name>
```

### 이미지 배포 테스트

```bash
kubectl run test --image=<image> --rm -it -- /bin/sh
kubectl create deployment test --image=<image>
kubectl expose deployment test --port=80 --type=NodePort
```

### 디버깅

```bash
kubectl get events --sort-by='.lastTimestamp'
kubectl describe pod <pod-name> | grep -A 10 Events
kubectl top pods
```

---

## k3s

경량 Kubernetes. 단일 바이너리, 빠른 설치.

### 설치 및 시작

```bash
# 서버 설치
curl -sfL https://get.k3s.io | sh -

# 상태 확인
sudo systemctl status k3s
sudo k3s kubectl get nodes
```

### kubectl 설정

```bash
# kubeconfig 복사
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER ~/.kube/config

# 또는 환경변수
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

### 로컬 이미지 사용

```bash
# k3s는 containerd 사용
sudo k3s ctr images import myapp.tar
```

### 제거

```bash
/usr/local/bin/k3s-uninstall.sh
```

---

## minikube

로컬 Kubernetes 클러스터. 다양한 드라이버 지원.

### 클러스터 관리

```bash
minikube start
minikube start --driver=docker
minikube start --driver=podman
minikube start --memory=4096 --cpus=2

minikube status
minikube stop
minikube delete
```

### 로컬 이미지 빌드

```bash
# minikube Docker 데몬 사용
eval $(minikube docker-env)
docker build -t myapp:local .

# 이미지 로드
minikube image load myapp:local
```

### 서비스 접근

```bash
minikube service <service-name>
minikube tunnel  # LoadBalancer 타입용
minikube dashboard
```

### 애드온

```bash
minikube addons list
minikube addons enable ingress
minikube addons enable metrics-server
```

---

## kind

Kubernetes in Docker. CI/CD 환경에 적합.

### 클러스터 관리

```bash
kind create cluster
kind create cluster --name my-cluster
kind create cluster --config kind-config.yaml

kind get clusters
kind delete cluster
```

### 이미지 로드

```bash
kind load docker-image myapp:latest
kind load docker-image myapp:latest --name my-cluster
```

### 설정 예시

```yaml
# kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30000
    hostPort: 30000
- role: worker
```

---

## Lima + k3s

macOS에서 Lima VM으로 k3s 실행.

### Lima k3s 인스턴스 생성

```bash
limactl start --name=k3s template://k3s

# 또는 커스텀 설정
limactl start k3s.yaml
```

### kubectl 설정

```bash
export KUBECONFIG=$(limactl list k3s -f '{{.Dir}}/copied-from-guest/kubeconfig.yaml')
kubectl get nodes
```

### Lima shell에서 직접 실행

```bash
limactl shell k3s sudo k3s kubectl get pods -A
lima sudo k3s kubectl apply -f deployment.yaml
```

### k3s.yaml 예시

```yaml
images:
- location: "https://cloud-images.ubuntu.com/releases/22.04/release/ubuntu-22.04-server-cloudimg-amd64.img"
  arch: "x86_64"
- location: "https://cloud-images.ubuntu.com/releases/22.04/release/ubuntu-22.04-server-cloudimg-arm64.img"
  arch: "aarch64"

mounts:
- location: "~"
  writable: true

provision:
- mode: system
  script: |
    curl -sfL https://get.k3s.io | sh -
```

---

## 환경별 이미지 배포 방법

| 환경 | 로컬 이미지 사용 방법 |
|------|----------------------|
| k3s | `sudo k3s ctr images import image.tar` |
| minikube | `eval $(minikube docker-env)` 후 빌드 또는 `minikube image load` |
| kind | `kind load docker-image image:tag` |
| Lima k3s | Lima 내에서 빌드하거나 `limactl copy` 후 import |
