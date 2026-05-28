---
name: commit-creator
description: Create a Git commit from current repository changes. Use when the agent needs to inspect local changes, verify the diff is appropriate for a feature or bug fix, stage only intended files, infer the repository's commit convention from recent history, run reasonable validation when available, and write a concise Korean commit message that follows the existing tone.
---

# Commit Creator

## Overview

Create a commit only after grounding the message and staged files in the repository state. Match the repository's existing commit convention and tone; use Korean for the commit message unless the repository history clearly requires another language.

## Workflow

1. Confirm the repository state:
   - Run `git status --short --branch`.
   - Run `git branch --show-current`.
   - Inspect recent commit convention with `git log --oneline -n 10`.
   - Inspect changed files with `git diff --stat` and `git diff --cached --stat`.
   - Inspect the actual diff with `git diff` and, when staged changes already exist, `git diff --cached`.

2. Determine commit scope:
   - Identify whether the changes form one coherent commit.
   - If unrelated changes are mixed, stage only the files or hunks that match the requested change.
   - Do not stage unrelated user changes.
   - If the intended scope is ambiguous and staging could include unrelated work, stop and report the ambiguity instead of guessing.

3. Run reasonable validation:
   - Prefer commands already established by the repository, such as test, lint, typecheck, or build scripts.
   - Keep validation proportional to the change size.
   - If validation is unavailable, too expensive, or unnecessary for a tiny documentation-only change, continue and mention that in the final response.

4. Stage intended changes:
   - Use `git add <path>` for clearly scoped files.
   - Use `git add -p` only when hunk-level selection is needed and interaction is practical.
   - Recheck with `git diff --cached --stat` and `git diff --cached` before committing.

5. Draft the commit message:
   - Match recent commit tone and convention. If commits use prefixes such as `feat:`, `fix:`, `chore:`, `docs:`, or ticket IDs, follow that style.
   - Write the subject in Korean unless the repository convention strongly indicates English.
   - Keep the subject concise and specific.
   - Add a body only when it materially clarifies a non-trivial change. For ordinary small changes, use a single subject line.

6. Create the commit:
   - Prefer non-interactive commands: `git commit -m "<Korean subject>"`.
   - For a needed body, use repeated `-m`: `git commit -m "<Korean subject>" -m "<Korean body>"`.
   - After committing, run `git status --short --branch` and `git log --oneline -1`.
   - Report the commit hash, message, and validation evidence.

## Korean Writing Rules

Use direct, repository-appropriate Korean. Avoid vague messages such as "수정", "작업", or "업데이트" unless the repository history consistently uses them.

Examples:

```text
feat: 알림 설정 저장 로직 추가
fix: 대시보드 필터 초기화 오류 수정
chore: 의존성 잠금 파일 갱신
docs: 배포 절차 설명 보강
refactor: 사용자 조회 조건 구성 정리
```

For a non-trivial commit body:

```text
fix: 로그인 실패 응답 처리 보강

인증 API가 예외 응답을 반환할 때도 사용자에게 동일한 오류 메시지를 보여주도록 정리했습니다.
기존 성공 흐름에는 영향을 주지 않도록 실패 분기만 수정했습니다.
```

## Stop Conditions

Stop before committing when:

- There are no changes to commit.
- The change scope is unclear or mixes unrelated work that cannot be safely separated.
- The only available action would stage unrelated user changes.
- Required validation fails and the failure is relevant to the commit.
- The requested commit would require destructive Git operations.
