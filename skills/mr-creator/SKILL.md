---
name: mr-creator
description: Create a GitLab merge request or GitHub pull request from the current repository changes. Use when the agent needs to publish a feature or bug fix for review, verify the remote hosting provider, inspect branch and commit context, choose glab or gh, push the current branch if needed, and write a concise Korean title and body that follows the repository's commit convention and existing tone.
---

# MR Creator

## Overview

Create an MR/PR only after grounding the request in the repository state. Prefer `glab` for GitLab remotes and `gh` for GitHub remotes; do not guess the hosting provider when the remote URL makes it clear.

## Workflow

1. Confirm the repository state:
   - Run `git status --short --branch`.
   - Run `git remote -v` and identify whether the target remote is GitLab or GitHub.
   - Run `git branch --show-current`.
   - Inspect recent tone and convention with `git log --oneline -n 10`.
   - Inspect the branch diff against the base branch with `git diff --stat <base>...HEAD` and, when needed, `git diff <base>...HEAD`.

2. Determine the base branch:
   - Prefer the remote default branch from `git remote show <remote>`.
   - If unavailable, use the repository's established target branch from existing MR/PR metadata or branch naming.
   - Fall back to `main` or `master` only when the repository context supports it.

3. Check CLI availability and authentication:
   - For GitLab: run `command -v glab` and `glab auth status`.
   - For GitHub: run `command -v gh` and `gh auth status`.
   - If the matching CLI is missing or unauthenticated, report the blocker and the exact command the user should run.

4. Verify branch readiness:
   - If there are uncommitted changes, do not create the MR/PR unless the user explicitly asked to include them and the changes are committed first.
   - If the current branch is the base branch, stop and report that a feature branch is needed.
   - If the branch is not pushed, push it with upstream tracking: `git push -u <remote> <branch>`.
   - If validation commands are obvious from the repo and reasonable to run, run them before creation and mention the result in the final report.

5. Draft Korean title and body:
   - Match the style of recent commits and existing conventions. If commits use prefixes such as `feat:`, `fix:`, `chore:`, use the same style in Korean where natural.
   - Keep the body concise. For ordinary small changes, write 3-5 Korean lines.
   - Summarize what changed and why. Include validation only when there is meaningful evidence.
   - Avoid overclaiming. If tests were not run, say so in the final response, not necessarily in the MR body unless the repository convention expects it.

6. Create the request:
   - GitLab: `glab mr create --target-branch <base> --source-branch <branch> --title "<Korean title>" --description "<Korean body>"`
   - GitHub: `gh pr create --base <base> --head <branch> --title "<Korean title>" --body "<Korean body>"`
   - Prefer non-interactive flags over interactive prompts.
   - Capture and report the created MR/PR URL.

## Korean Writing Rules

Use direct, repository-appropriate Korean. Prefer concise bullets or short lines over long paragraphs.

Example for a simple feature:

```markdown
feat: 알림 설정 저장 로직 추가

- 사용자별 알림 설정을 저장하도록 API 흐름을 추가했습니다.
- 기존 설정 조회 응답과 저장 요청의 필드명을 맞췄습니다.
- 관련 유효성 검사를 보강했습니다.
```

Example for a bug fix:

```markdown
fix: 대시보드 필터 초기화 오류 수정

- 필터 초기화 시 이전 검색 조건이 남는 문제를 수정했습니다.
- 초기 상태 계산을 공통 함수로 정리했습니다.
- 영향 범위를 대시보드 조회 화면으로 제한했습니다.
```

## Stop Conditions

Stop before creating the MR/PR when:

- The repository has no Git remote.
- The hosting provider cannot be determined and both `glab` and `gh` could plausibly apply.
- The current branch is the base branch.
- Required committed changes are missing.
- The matching CLI is unavailable or not authenticated.
- The requested creation would require destructive Git operations.
