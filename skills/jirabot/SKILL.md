---
name: jirabot
description: Use the local Jira CLI at ~/Github/local-jira-cli/local-jira-cli.js to inspect Jira boards, projects, sprints, tickets, comments, ticket context, issue trees, and transitions; create or update tickets; add or delete comments; move tickets between sprints/backlog; or perform other safe Jira Cloud work through the allowlisted local wrapper. Use when the user asks to check Jira state, summarize Jira issues, create Jira tasks/subtasks, comment on a ticket, edit ticket fields, transition ticket status, or manage sprint placement.
---

# Jirabot

Use the local Jira wrapper rather than raw `acli`, direct Jira REST calls, or browser automation:

```bash
node ~/Github/local-jira-cli/local-jira-cli.js --help
```

### Setup Check

Before running any CLI command, verify the CLI is available:

```bash
[ -f ~/Github/local-jira-cli/local-jira-cli.js ] || echo "CLI not found"
```

If the file is missing, **stop** and instruct the user to clone it:

```bash
git clone https://github.com/terria1020/local-jira-cli ~/Github/local-jira-cli
```

After cloning, follow the CLI's own README to configure credentials and environment variables. If credentials or `.env` are not set up, **stop** and direct the user to the CLI's setup guide — do not attempt to read credential files or work around missing auth.

The wrapper loads its own environment, allowlists commands, returns JSON-shaped output where possible, and requires `--yes` or `--dry-run` for writes.

## Workflow

1. Start with read-only discovery unless the user supplied an exact ticket key and operation.
2. Use `ticket-context --key <KEY> --comments <N>` before making non-trivial edits or comments, so the response reflects current Jira state.
3. For board, sprint, command option, and write examples, read `references/local-jira-cli.md`.
4. For every write, run the same command with `--dry-run` first, inspect the resolved action, then run with `--yes` only when it matches the user request.
5. Report the important Jira result to the user: ticket keys, URLs when present, status changes, created/updated fields, comment result, and any error code/message.

## Common Commands

Set a short local variable in the shell command when it improves readability:

```bash
JIRA=~/Github/local-jira-cli/local-jira-cli.js
node "$JIRA" ticket-context --key SD-123 --comments 10
```

Use these as the default read path:

```bash
node ~/Github/local-jira-cli/local-jira-cli.js project-overview --project SD --limit 20 --board-limit 5
node ~/Github/local-jira-cli/local-jira-cli.js ticket-list --project SD --limit 20
node ~/Github/local-jira-cli/local-jira-cli.js ticket-list --jql "assignee = currentUser() AND statusCategory != Done" --limit 20
node ~/Github/local-jira-cli/local-jira-cli.js ticket-context --key SD-123 --comments 10
```

Use files for long descriptions or comments to avoid shell quoting problems. Create temporary files under the current workspace or `/private/tmp`, then pass `--description-file` or `--body-file`.

## Safety Rules

- Never expose `.env`, API tokens, authorization headers, or raw credential files in the response.
- Never bypass the wrapper with direct Jira REST or raw `acli` unless the user explicitly asks and accepts the risk.
- Never run a write command without first running `--dry-run`, except when the user only asked for a dry run.
- Never invent transition names, sprint IDs, board IDs, issue keys, or project keys. Query them.
- Prefer `transition-list` before `transition`; only use a status that appears in the available transition candidates.
- Prefer `sprint-resolve` before sprint moves when the target is an alias such as `current`, `next`, or `backlog`.
- Treat delete operations, bulk changes, and status transitions as high-impact writes; verify the target ticket keys from Jira output before executing with `--yes`.

## Output Handling

Parse the wrapper response as JSON when possible. Successful responses usually include `ok: true` and `result`; dry runs include `dryRun: true` and `steps`; failures include `ok: false`, `code`, and `message`.

If output is wrapped stdout text, summarize the actionable lines rather than pasting the whole command output. Preserve ticket keys, statuses, assignees, sprint names, and comment IDs when they matter.
