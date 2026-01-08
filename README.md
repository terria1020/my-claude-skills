# My Claude Skills

Claude Code 커스텀 스킬 모음

## 스킬 목록

| 스킬 | 설명 |
|------|------|
| [compile-test](./compile-test/) | 다중 언어 컴파일/문법 검증 (Python, Java, JS/TS, Dockerfile, K8s) |

## Claude Code에 스킬 추가하기

### 전역 설정 (모든 프로젝트에 적용)

`~/.claude/settings.json` 파일 편집:

```json
{
  "skills": [
    "https://github.com/terria1020/my-claude-skills/tree/main/compile-test"
  ]
}
```

### 프로젝트별 설정 (특정 프로젝트에만 적용)

프로젝트 루트의 `.claude/settings.json` 파일 편집:

```json
{
  "skills": [
    "https://github.com/terria1020/my-claude-skills/tree/main/compile-test"
  ]
}
```

### 기존 설정이 있는 경우

이미 다른 설정이 있다면 `skills` 배열만 추가:

```json
{
  "existingKey": "existingValue",
  "skills": [
    "https://github.com/terria1020/my-claude-skills/tree/main/compile-test"
  ]
}
```

## 스킬 사용법

스킬 추가 후 Claude Code 재시작, 이후:

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
