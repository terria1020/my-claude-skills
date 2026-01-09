# Container Troubleshooting Guide

일반적인 컨테이너 문제와 해결 방법.

## Table of Contents

- [빌드 실패](#빌드-실패)
- [실행 실패](#실행-실패)
- [네트워크 문제](#네트워크-문제)
- [권한 문제](#권한-문제)
- [리소스 문제](#리소스-문제)
- [런타임별 이슈](#런타임별-이슈)

---

## 빌드 실패

### Base 이미지를 찾을 수 없음

```
Error: pull access denied, repository does not exist
```

**원인**: 이미지 이름 오타, 프라이빗 레지스트리 인증 필요

**해결**:

```bash
# 이미지 이름 확인
docker search <image-name>

# 레지스트리 로그인
docker login <registry-url>
```

### 빌드 컨텍스트가 너무 큼

```
Sending build context to Docker daemon  2.5GB
```

**해결**: `.dockerignore` 파일 생성

```
# .dockerignore
node_modules
.git
*.log
dist
build
```

### 패키지 설치 실패

```
E: Unable to locate package xxx
```

**해결**: 패키지 목록 업데이트

```dockerfile
RUN apt-get update && apt-get install -y package-name
```

### 멀티 스테이지 빌드 참조 오류

```
COPY --from=builder failed: not found
```

**원인**: 빌더 스테이지 이름 불일치

**해결**:

```dockerfile
FROM node:18 AS builder
# ...

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

---

## 실행 실패

### 컨테이너가 즉시 종료됨

**진단**:

```bash
docker logs <container>
docker inspect <container> --format='{{.State.ExitCode}}'
```

**일반적인 원인**:
- 포그라운드 프로세스 없음
- 시작 스크립트 오류
- 설정 파일 누락

**해결**: CMD/ENTRYPOINT 확인

```dockerfile
# 잘못된 예 - 즉시 종료됨
CMD ["echo", "hello"]

# 올바른 예 - 포그라운드 실행
CMD ["nginx", "-g", "daemon off;"]
```

### Port already in use

```
Bind for 0.0.0.0:8080 failed: port is already allocated
```

**해결**:

```bash
# 사용 중인 포트 확인
lsof -i :8080

# 다른 포트 사용
docker run -p 8081:80 <image>
```

### 파일/디렉토리를 찾을 수 없음

```
exec: "/app/start.sh": not found
```

**원인**: 파일이 없거나 실행 권한 없음

**해결**:

```dockerfile
COPY start.sh /app/
RUN chmod +x /app/start.sh
```

---

## 네트워크 문제

### 컨테이너 간 통신 불가

**Docker Compose 환경**:

```yaml
services:
  app:
    networks:
      - backend
  db:
    networks:
      - backend

networks:
  backend:
```

**수동 네트워크 생성**:

```bash
docker network create mynet
docker run --network=mynet --name=db postgres
docker run --network=mynet --name=app myapp
```

### DNS 해석 실패

```
Could not resolve host: registry.example.com
```

**해결**:

```bash
# DNS 설정
docker run --dns=8.8.8.8 <image>

# 또는 /etc/docker/daemon.json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

---

## 권한 문제

### Permission denied

```
permission denied while trying to connect to the Docker daemon socket
```

**해결**:

```bash
# Docker 그룹에 사용자 추가
sudo usermod -aG docker $USER
newgrp docker

# 또는 소켓 권한 확인
sudo chmod 666 /var/run/docker.sock
```

### Rootless 모드에서 볼륨 마운트 문제

**Podman**:

```bash
podman run --userns=keep-id -v $(pwd):/app:Z <image>
```

**Docker rootless**:

```bash
# UID 매핑 확인
cat /etc/subuid
cat /etc/subgid
```

### SELinux 문제 (RHEL/Fedora)

```bash
# :Z 옵션으로 레이블 지정
docker run -v /host/path:/container/path:Z <image>

# 또는 SELinux 비활성화 (권장하지 않음)
sudo setenforce 0
```

---

## 리소스 문제

### Out of memory

```
Killed
Exit code: 137
```

**해결**:

```bash
# 메모리 제한 늘리기
docker run -m 2g <image>

# 스왑 포함
docker run -m 2g --memory-swap 4g <image>
```

### Disk space 부족

```
no space left on device
```

**정리**:

```bash
# 미사용 리소스 정리
docker system prune -af

# 볼륨 포함 정리
docker system prune -af --volumes

# 빌드 캐시 정리
docker builder prune -af
```

---

## 런타임별 이슈

### Docker Desktop (macOS)

**VM 리소스 부족**:
Settings > Resources에서 CPU/Memory 증가

**파일 공유 느림**:

```yaml
# docker-compose.yml
volumes:
  - type: bind
    source: ./src
    target: /app/src
    consistency: cached
```

### Podman

**네트워크 모드 차이**:

```bash
# Docker 호환 네트워크
podman network create --driver bridge mynet
```

**docker-compose 호환**:

```bash
pip install podman-compose
podman-compose up -d
```

### Lima + nerdctl

**BuildKit 필요**:

```bash
# buildkitd 실행 확인
lima sudo systemctl status buildkit

# 빌드
lima nerdctl build -t myapp .
```

**볼륨 마운트 경로**:

```bash
# Lima는 홈 디렉토리만 기본 마운트
# ~/.lima/<instance>/lima.yaml 에서 mounts 설정 확인
```

---

## 빠른 진단 체크리스트

1. **런타임 상태 확인**

   ```bash
   docker info  # 또는 podman info
   ```

2. **컨테이너 로그 확인**

   ```bash
   docker logs --tail 100 <container>
   ```

3. **리소스 사용량 확인**

   ```bash
   docker stats
   docker system df
   ```

4. **이벤트 확인**

   ```bash
   docker events --since 1h
   ```

5. **컨테이너 내부 진입**

   ```bash
   docker exec -it <container> /bin/sh
   ```
