---
name: container-validator
description: |
  컨테이너 환경 검증 및 Dockerfile 빌드 테스트 스킬. 다음 상황에서 사용:
  (1) 사용자가 기능 개발 후 프로젝트가 컨테이너 환경에서 작동하는지 확인 요청할 때
  (2) Dockerfile 빌드, 컨테이너 실행 테스트를 명시적으로 요청할 때
  (3) 특정 컨테이너 런타임(docker, podman, nerdctl 등)으로 테스트 요청할 때
  (4) 로컬 또는 원격 이미지로 컨테이너 실험을 원할 때
  (5) Kubernetes/k3s/minikube 환경에서 배포 테스트할 때
  지원 런타임: docker, podman, nerdctl, crictl, containerd
  지원 오케스트레이션: kubectl, k3s, minikube, kind, lima
---

# Container Validator

컨테이너 환경을 자동 감지하고 Dockerfile 빌드 및 실행을 검증한다.

## Workflow

```
환경 감지 → 런타임 선택 → 빌드 검증 → 실행 검증 → 결과 보고
```

### Step 1: 환경 감지

사용자 환경의 컨테이너 런타임 및 오케스트레이션 도구를 자동 탐지한다.

```bash
python3 scripts/detect_env.py
```

출력 예시:

```
OS: Darwin 25.2.0 (arm64)
Environment Type: docker-desktop
Recommended Runtime: docker

Container Runtimes:
  [OK] docker - Docker version 28.3.3
  [OK] podman - podman version 5.6.1
  [--] nerdctl
```

JSON 출력이 필요하면:

```bash
python3 scripts/detect_env.py -f json
```

### Step 2: 런타임 선택

환경 타입에 따라 적절한 런타임을 선택한다.

| 환경 타입 | 권장 런타임 | 비고 |
|----------|------------|------|
| docker-desktop | docker | Docker Desktop 사용 |
| native | 감지된 런타임 우선순위 | docker > nerdctl > podman |
| lima | nerdctl | Lima VM 내 containerd 사용 |
| colima | docker | Colima Docker context |
| rancher-desktop | nerdctl 또는 docker | 설정에 따라 다름 |

사용자가 특정 런타임을 지정한 경우 해당 런타임 사용.

### Step 3: 빌드 검증

Dockerfile 빌드가 성공하는지 검증한다.

```bash
python3 scripts/validate_build.py ./Dockerfile
python3 scripts/validate_build.py ./Dockerfile -r podman
python3 scripts/validate_build.py ./Dockerfile -t myapp:test --no-cache
```

옵션:

- `-r, --runtime`: 런타임 지정 (docker, podman, nerdctl)
- `-t, --tag`: 이미지 태그 지정
- `-c, --context`: 빌드 컨텍스트 디렉토리
- `--skip-run`: 컨테이너 실행 테스트 건너뛰기
- `--skip-cleanup`: 빌드된 이미지 유지
- `--no-cache`: 캐시 없이 빌드

### Step 4: 결과 해석

```
============================================================
Container Build Validation Report
============================================================

Dockerfile: ./Dockerfile
Runtime: docker
Image Tag: validate-test:1234567890
Total Duration: 45.23s

Validation Steps:
----------------------------------------
  [PASS] dockerfile_syntax (0.01s)
         Dockerfile syntax is valid
  [PASS] build_image (42.15s)
         Image built successfully
  [PASS] run_container (2.87s)
         Container runs successfully
  [PASS] cleanup (0.20s)
         Image cleaned up

----------------------------------------
Overall: SUCCESS
============================================================
```

실패 시 에러 메시지를 확인하고 [troubleshooting.md](references/troubleshooting.md) 참조.

## Use Cases

### UC-1: 프로젝트 개발 후 컨테이너 검증

프로젝트에 Dockerfile이 있으면 자동으로 빌드 검증 제안:

1. `detect_env.py`로 환경 확인
2. 환경이 불명확하면 사용자에게 질문
3. `validate_build.py`로 빌드 및 실행 검증
4. 실패 시 troubleshooting 가이드 제공

### UC-2: 명시적 테스트 요청

사용자가 경로, 런타임, 이미지를 지정한 경우:

```bash
# 특정 런타임으로 테스트
python3 scripts/validate_build.py ./docker/Dockerfile.prod -r podman

# 원격 이미지 실행 테스트 (스크립트 없이 직접 실행)
docker run --rm nginx:alpine echo "test"
```

### UC-3: Sandbox 실험

임시 컨테이너로 실험:

```bash
# 대화형 쉘
docker run -it --rm alpine /bin/sh

# 특정 명령 테스트
docker run --rm python:3.11 python -c "print('hello')"
```

## 환경별 주의사항

### Lima 환경

```bash
# Lima 인스턴스 확인
limactl list

# Lima 내에서 nerdctl 사용
lima nerdctl build -t myapp .
lima nerdctl run --rm myapp
```

### Rootless Podman

```bash
# UID 매핑 확인
podman unshare cat /proc/self/uid_map

# 볼륨 마운트 시 :Z 옵션
podman run -v $(pwd):/app:Z myapp
```

### Kubernetes 배포 테스트

k8s/k3s/minikube 환경에서 이미지 배포:

```bash
# minikube
eval $(minikube docker-env)
docker build -t myapp:local .
kubectl run test --image=myapp:local --image-pull-policy=Never

# kind
kind load docker-image myapp:local
kubectl apply -f deployment.yaml
```

## References

- [runtimes.md](references/runtimes.md): 런타임별 핵심 명령어
- [orchestration.md](references/orchestration.md): k8s/k3s/minikube 명령어
- [troubleshooting.md](references/troubleshooting.md): 문제 해결 가이드
