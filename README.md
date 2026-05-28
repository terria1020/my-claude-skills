# My Claude Skills

AI 에이전트용 커스텀 스킬 모음

## 스킬 목록

| 스킬 | 설명 | 외부 의존성 |
|------|------|------------|
| [commit-creator](./skills/commit-creator/) | 로컬 변경사항을 분석해 한국어 커밋 메시지로 Git 커밋 생성 | |
| [compile-test](./skills/compile-test/) | Python, Java, JS/TS, Dockerfile, K8s 등 다중 언어 컴파일/문법 검증 | |
| [confluence-inspector](./skills/confluence-inspector/) | Confluence 페이지·공간·메타데이터 안전 조회 | [local-confluence-api-cli](https://github.com/terria1020/local-confluence-api-cli) |
| [container-validator](./skills/container-validator/) | 컨테이너 런타임 환경 감지 및 Dockerfile 빌드·실행 검증 | |
| [database-inspector](./skills/database-inspector/) | MariaDB·MySQL·PostgreSQL·Elasticsearch 스키마/데이터 안전 조회 | [local-rdbms-connect-cli](https://github.com/terria1020/local-rdbms-connect-cli) |
| [design-socratic-review](./skills/design-socratic-review/) | 구현 전 소프트웨어 설계·아키텍처·기술 선택 소크라테스식 리뷰 | |
| [experiment-builder](./skills/experiment-builder/) | 불확실한 아이디어를 최소 실행 가능한 실험으로 변환 | |
| [gws-sheets](./skills/gws-sheets/) | Google Sheets 셀 읽기·쓰기·서식 적용 | `gws` CLI |
| [jirabot](./skills/jirabot/) | Jira 보드·스프린트·티켓 조회 및 생성·수정·전환 | [local-jira-cli](https://github.com/terria1020/local-jira-cli) |
| [mr-creator](./skills/mr-creator/) | GitLab MR 또는 GitHub PR 생성 — remote URL로 호스팅 자동 감지, 한국어 제목·본문 작성 | |
| [notion-inspector](./skills/notion-inspector/) | Notion 페이지·데이터베이스·블록 안전 조회 | [notion-api-cli](https://github.com/terria1020/notion-api-cli) |
| [ssh-inspector](./skills/ssh-inspector/) | SSH 크레덴셜 wrapper CLI를 통해 원격 서버에 명령 실행 — 상태·로그 조회부터 서비스 재시작·배포 스크립트 실행까지 (쓰기 작업은 명시적 확인 후 실행) | [local-ssh-connect-cli](https://github.com/terria1020/local-ssh-connect-cli) |

> 외부 의존성이 있는 스킬은 각 CLI를 `~/Github/<repo-name>`에 클론하고 README에 따라 크레덴셜을 설정해야 합니다.

## 스킬 설치 방법

스킬은 `SKILL.md`가 있는 폴더를 에이전트가 읽는 skills 경로에 배치하면 됩니다.

### 전역 설정 (모든 프로젝트에 적용)

```bash
# 저장소를 원하는 위치에 클론
git clone https://github.com/terria1020/my-claude-skills ~/Github/my-claude-skills

# 원하는 스킬을 ~/.claude/skills/ 에 복사
cp -r ~/Github/my-claude-skills/skills/commit-creator ~/.claude/skills/
cp -r ~/Github/my-claude-skills/skills/jirabot ~/.claude/skills/
# ... 필요한 스킬만 선택
```

결과 구조:

```
~/.claude/skills/
├── commit-creator/
│   └── SKILL.md
├── jirabot/
│   ├── SKILL.md
│   └── references/
└── ...
```

### 프로젝트별 설정 (특정 프로젝트에만 적용)

```bash
cp -r ~/Github/my-claude-skills/skills/compile-test /your/project/.claude/skills/
```

결과 구조:

```
your-project/
├── .claude/
│   └── skills/
│       └── compile-test/
│           ├── SKILL.md
│           └── references/
└── src/
```

## 프로젝트 구조

```
my-claude-skills/
├── skills/                        # 스킬 소스
│   ├── commit-creator/
│   ├── compile-test/
│   ├── confluence-inspector/
│   ├── container-validator/
│   ├── database-inspector/
│   ├── design-socratic-review/
│   ├── experiment-builder/
│   ├── gws-sheets/
│   ├── jirabot/
│   ├── mr-creator/
│   ├── notion-inspector/
│   └── ssh-inspector/
└── docs/plans/                    # 개발 계획 문서
```
