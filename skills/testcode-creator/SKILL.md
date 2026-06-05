---
name: testcode-creator
description: |
  테스트 코드를 설계, 작성, 실행하는 스킬. 사용자가 테스트 추가, 테스트 코드 작성, 회귀 테스트 보강, 특정 변경사항/피처/버그픽스의 동작 보장, 해피케이스/언해피케이스/엣지케이스 도출과 구현, 또는 변경 후 테스트 실행을 요청할 때 사용한다. 언어를 선제적으로 지정하지 말고 현재 디렉토리와 변경 컨텍스트에서 언어, 프레임워크, 테스트 러너, 모듈 경계를 먼저 파악한 뒤 진행한다.
---

# Testcode Creator

변경사항이나 기능의 보장 포인트를 테스트 케이스로 분해하고, 프로젝트의 기존 테스트 스타일에 맞춰 테스트 코드를 작성한 뒤, 관련 테스트를 실제로 실행한다.

## Workflow

```
1. Context Detection     -> 변경사항, 언어, 모듈, 테스트 러너 파악
2. Test Environment     -> 기존 테스트 구조와 실행 명령 확인
3. Guarantee Mapping    -> 보장해야 할 동작과 리스크 정리
4. Case Briefing        -> 해피/언해피 기본/엣지 케이스 선정 브리핑
5. Test Implementation  -> 기존 패턴에 맞춰 테스트 코드 작성
6. Test Execution       -> 가장 좁은 관련 테스트부터 실행
7. Result Report        -> 결과, 커버 범위, 남은 리스크 보고
```

## Step 1: Context Detection

먼저 사용자가 준 컨텍스트와 현재 저장소 상태를 합쳐 테스트 대상을 좁힌다.

- 사용자가 특정 파일, 함수, 피처, 티켓, 버그, 커밋, diff를 지정했으면 그것을 우선한다.
- 지정이 없으면 `git status --short`, `git diff --stat`, `git diff`로 현재 변경사항을 확인한다.
- 코드 발견은 프로젝트 지침이 있으면 그 지침을 우선한다. 예: codebase-memory MCP가 활성화된 프로젝트는 `search_graph`, `trace_path`, `get_code_snippet`을 먼저 사용한다.
- 문자열, 설정, 비코드 파일, 테스트 명령 탐지는 `rg`, `rg --files`, 패키지 매니페스트 확인으로 보완한다.
- 사용자 변경사항을 되돌리지 말고, 테스트 작성에 필요한 최소 파일만 수정한다.

언어와 테스트 러너는 파일과 매니페스트로 감지한다.

| Indicator | Likely Test Command |
|-----------|---------------------|
| `package.json` | `npm test`, `npm run test`, `pnpm test`, `yarn test`, `npx vitest`, `npx jest` |
| `pyproject.toml`, `pytest.ini`, `requirements.txt` | `pytest`, `python -m pytest`, `uv run pytest` |
| `pom.xml` | `mvn test`, `./mvnw test` |
| `build.gradle`, `build.gradle.kts` | `./gradlew test`, `gradle test` |
| `go.mod` | `go test ./...` or package-scoped `go test ./path` |
| `Cargo.toml` | `cargo test` |
| `.csproj`, `.sln` | `dotnet test` |
| `mix.exs` | `mix test` |
| `Gemfile`, `.rspec` | `bundle exec rspec`, `rails test` |

## Step 2: Test Environment

기존 테스트 환경을 확인한 뒤 같은 관례를 따른다.

- 테스트 디렉토리, 파일명, fixture/factory/mock 스타일, assertion 라이브러리, helper 사용 방식을 확인한다.
- 가장 가까운 기존 테스트 파일을 우선 읽고, shared helper나 setup 파일은 필요한 만큼만 읽는다.
- 테스트 러너가 여러 개면 변경 대상 모듈과 가장 가까운 러너를 선택한다.
- 의존성이 설치되어 있지 않으면 프로젝트의 기존 설치 방식만 사용한다. 새 패키지 추가는 테스트를 작성할 수 없을 때만 하고, 그 이유를 명확히 남긴다.
- 외부 네트워크, 실제 결제, 운영 DB, 운영 API 호출은 테스트에서 직접 사용하지 않는다. 기존 mock, fake, fixture, local test container 패턴을 우선한다.

## Step 3: Guarantee Mapping

테스트를 쓰기 전에 보장할 동작을 짧게 정리한다.

- 입력과 출력, 상태 변경, 예외, 부수효과, 권한, 검증 규칙을 분리한다.
- 버그픽스라면 재발 조건을 테스트 이름과 fixture에 드러낸다.
- 피처라면 사용자 관점의 정상 흐름과 모듈 경계의 계약을 우선한다.
- 리팩터링이라면 기존 외부 동작이 유지되는지 검증한다.
- 경합, 시간, 정렬, null/empty, 경계값, 중복, 권한 없음, 네트워크 실패 같은 위험 요소를 후보로 둔다.

## Step 4: Case Briefing

테스트 코드 작성 전에 선정한 케이스를 간결히 브리핑한다. 허락을 기다리지 말고 바로 구현으로 이어간다.

브리핑 형식:

```
Test Plan
- Target: <module/function/feature>
- Runner: <command or inferred runner>
- Happy basic: <normal expected behavior>
- Happy edge: <valid boundary or variant>
- Unhappy basic: <invalid input/error path>
- Unhappy edge: <rare failure, boundary, race, permission, empty/null, duplicate, timeout>
- Scope choice: <why these tests are enough for this change>
```

작은 변경이면 모든 칸을 억지로 채우지 말고, 실제 가치가 있는 케이스만 작성한다. 다만 해피케이스와 언해피케이스를 최소 한 번씩 검토했는지는 보고한다.

## Step 5: Test Implementation

기존 코드베이스의 테스트 스타일을 따른다.

- 변경 대상과 가장 가까운 테스트 파일에 추가한다. 기존 패턴이 없으면 해당 언어의 표준 위치에 새 파일을 만든다.
- 테스트 이름은 보장하는 동작을 드러내게 작성한다.
- fixture는 작고 명시적으로 유지하고, 광범위한 snapshot이나 golden file은 기존 관례가 있을 때만 사용한다.
- mock은 외부 경계에만 둔다. 순수 로직은 실제 값을 넣어 검증한다.
- brittle한 구현 세부사항보다 공개 API, 출력, 상태, 관찰 가능한 부수효과를 검증한다.
- 시간/랜덤/환경변수는 고정하거나 주입 가능한 형태를 사용한다.
- 테스트를 위해 production code를 바꿔야 하면 최소한으로 변경하고 이유를 보고한다.

## Step 6: Test Execution

가장 좁은 테스트부터 실행하고, 필요할 때만 범위를 넓힌다.

1. 새로 작성하거나 수정한 테스트 파일만 실행한다.
2. 관련 모듈 테스트를 실행한다.
3. 변경 범위가 넓거나 shared behavior를 건드렸으면 전체 테스트 또는 표준 CI 테스트 명령을 실행한다.

실행 전 도구 존재 여부를 확인한다. 도구가 없거나 환경이 불완전하면 가능한 대체 명령을 시도하고, 그래도 불가하면 정확한 차단 사유를 보고한다.

실패하면 원인을 분류한다.

- 테스트 기대값이 틀렸으면 테스트를 수정한다.
- 코드 버그가 드러났고 요청 범위 안이면 production code를 수정하고 테스트를 다시 실행한다.
- 요청 범위 밖의 기존 실패면 새 테스트와 무관함을 근거와 함께 보고한다.
- flaky 가능성이 있으면 재실행으로 확인하고, 안정화 방법을 적용한다.

## Step 7: Result Report

마지막 보고는 짧고 검증 증거 중심으로 작성한다.

포함할 항목:

- 작성/수정한 테스트 파일
- 커버한 해피케이스와 언해피케이스
- 실행한 명령과 결과
- 실행하지 못한 테스트와 이유
- 남은 리스크나 후속 테스트 필요성이 있으면 한 줄로 명시

성공 예:

```
Testcode Creator: PASSED
- Added: tests/order_service_test.py
- Covered: valid order creation, duplicate id rejection, empty item rejection
- Ran: python -m pytest tests/order_service_test.py -q
```

부분 성공 예:

```
Testcode Creator: PARTIAL
- Added: src/foo/foo.test.ts
- Ran: npm test -- foo.test.ts
- Blocked: project dependencies are not installed and no lockfile install was requested
```
