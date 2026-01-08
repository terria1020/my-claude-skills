# My Claude Skills

Claude Code 커스텀 스킬 모음

## 스킬 목록

| 스킬 | 설명 |
|------|------|
| [compile-test](./compile-test/) | 다중 언어 컴파일/문법 검증 (Python, Java, JS/TS, Dockerfile, K8s) |

## Claude Code에 스킬 추가하기

### 방법 1: 설정 파일에 직접 추가

`~/.claude/settings.json` 파일에 추가:

```json
{
  "skills": [
    "https://github.com/terria1020/my-claude-skills/tree/main/compile-test"
  ]
}
```

### 방법 2: Claude Code CLI로 추가

```bash
claude settings add skills "https://github.com/terria1020/my-claude-skills/tree/main/compile-test"
```

### 방법 3: 대화 중 추가

Claude Code 실행 후:

```
/add-skill https://github.com/terria1020/my-claude-skills/tree/main/compile-test
```

## 스킬 사용법

스킬이 추가되면 다음과 같이 사용:

```
/compile-test
```

또는 자연어로:

```
컴파일 테스트 해줘
이 프로젝트 빌드 검증해줘
```

## 스킬 구조

```
<skill-name>/
├── SKILL.md              # 스킬 메인 파일 (필수)
└── references/           # 참조 문서 (선택)
    └── *.md
```
