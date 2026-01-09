# Container Validator Skill Plan

## 목표

- 컨테이너 환경을 자동으로 감지하고 검증하는 스킬 생성
- Dockerfile 빌드 및 컨테이너 실행 가능 여부 확인
- 다양한 컨테이너 런타임 및 오케스트레이션 환경 지원

## 사용 케이스

| UC | 설명 | 트리거 예시 |
|----|------|------------|
| UC-1 | 기능 개발 후 컨테이너 환경 검증 | "이 프로젝트 컨테이너로 빌드되는지 확인해줘" |
| UC-2 | 명시적 테스트 요청 | "이 Dockerfile을 podman으로 빌드해봐" |
| UC-3 | Sandbox 실험 | "nginx 이미지로 테스트 컨테이너 띄워줘" |

## 지원 환경

### OS

- Linux
- macOS
- Windows

### 컨테이너 런타임

| 카테고리 | 도구 |
|---------|------|
| Native | docker, podman, nerdctl, crictl |
| Lima 환경 | lima + nerdctl/podman/crictl |
| Desktop | Docker Desktop, Podman Desktop, Rancher Desktop |

### 오케스트레이션

- Kubernetes (kubectl)
- k3s
- minikube
- Lima k3s

## 작업 범위

### 스킬 구조

```
container-validator/
├── SKILL.md
├── scripts/
│   ├── detect_env.py          # 환경 감지 스크립트 (크로스 플랫폼)
│   └── validate_build.py      # 빌드 검증 스크립트
└── references/
    ├── runtimes.md            # 런타임별 명령어 레퍼런스
    ├── orchestration.md       # 오케스트레이션 레퍼런스
    └── troubleshooting.md     # 문제 해결 가이드
```

### 설계 원칙

- **레퍼런스 문서**: 각 도구의 전체 문서가 아닌, 빌드/실행/상태확인에 필요한 핵심 명령어만 발췌
- **스크립트**: Python으로 작성하여 크로스 플랫폼 호환성 확보

### 주요 기능

1. **환경 감지**: 현재 시스템에서 사용 가능한 컨테이너 런타임 자동 탐지
2. **빌드 검증**: Dockerfile 빌드 가능 여부 확인
3. **실행 검증**: 컨테이너 init 및 실행 상태 확인
4. **환경 질문**: 사용자 환경이 불명확할 때 질문으로 해소

## 작업 단계

- [ ] Step 1: 스킬 초기화 (init_skill.py 실행)
- [ ] Step 2: 환경 감지 스크립트 작성 (detect_env.sh/ps1)
- [ ] Step 3: 빌드 검증 스크립트 작성 (validate_build.sh)
- [ ] Step 4: 레퍼런스 문서 작성 (runtimes.md, orchestration.md)
- [ ] Step 5: SKILL.md 작성
- [ ] Step 6: 스킬 패키징 및 테스트

## 참고 사항

### 제약 조건

- 스크립트는 POSIX 호환성 고려 (bash/sh)
- Windows는 PowerShell 스크립트 별도 제공
- 권한 문제 (rootless 환경 등) 고려 필요

### 의존성

- 각 런타임 도구의 CLI 명령어
- Lima 환경의 경우 limactl 명령어

### 레퍼런스 문서 출처

- nerdctl: https://github.com/containerd/nerdctl
- containerd: https://containerd.io/docs/
- podman: https://docs.podman.io/
- crictl: https://github.com/kubernetes-sigs/cri-tools
- cri-o: https://cri-o.io/
- docker: https://docs.docker.com/
- kubernetes: https://kubernetes.io/docs/
- k3s: https://docs.k3s.io/
- minikube: https://minikube.sigs.k8s.io/docs/
- lima: https://lima-vm.io/docs/
