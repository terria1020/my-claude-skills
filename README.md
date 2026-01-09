# My Claude Skills

Claude Code 커스텀 스킬 모음

## 스킬 목록

| 스킬 | 설명 |
|------|------|
| [compile-test](./skills/compile-test/) | 다중 언어 컴파일/문법 검증 (Python, Java, JS/TS, Dockerfile, K8s) |
| [container-validator](./skills/container-validator/) | 컨테이너 환경 검증 및 Dockerfile 빌드 테스트 |

## Claude Code에 스킬 추가하기

스킬은 파일 시스템 경로에 직접 배치해야 합니다.

### 전역 설정 (모든 프로젝트에 적용)

`~/.claude/skills/` 디렉토리에 스킬 폴더 배치:

```bash
# 방법 1: 저장소 전체 클론
cd ~/.claude/skills
git clone https://github.com/terria1020/my-claude-skills.git

# 방법 2: 특정 스킬만 복사
mkdir -p ~/.claude/skills/compile-test
cp -r /path/to/my-claude-skills/skills/compile-test/* ~/.claude/skills/compile-test/
```

결과 구조:

```
~/.claude/skills/
└── compile-test/
    ├── SKILL.md
    └── references/
```

### 프로젝트별 설정 (특정 프로젝트에만 적용)

프로젝트 루트의 `.claude/skills/` 디렉토리에 스킬 폴더 배치:

```bash
cd /your/project
mkdir -p .claude/skills/compile-test
cp -r /path/to/my-claude-skills/skills/compile-test/* .claude/skills/compile-test/
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

## 스킬 사용법

스킬 추가 후 Claude Code 재시작, 이후:

```
/compile-test
/container-validator
```

또는 자연어로:

```
컴파일 테스트 해줘
컨테이너 환경 확인해줘
이 프로젝트 빌드 검증해줘
```

## 프로젝트 구조

```
my-claude-skills/
├── skills/                   # 스킬 소스
│   ├── compile-test/
│   │   ├── SKILL.md
│   │   └── references/
│   └── container-validator/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
├── dist/                     # 패키징된 .skill 파일
└── docs/plans/               # 개발 계획 문서
```
