# local-jira-cli Reference

CLI path:

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js <command> [options]
```

Use `--json` when supported by the underlying command. Write commands require `--dry-run` or `--yes`.

## Commands

| Command | Type | Purpose |
|---|---|---|
| `board-list` | read | Search Jira boards by project, name, or type |
| `ticket-list` | read | Search tickets by JQL or project |
| `ticket-show` | read | Show a single ticket |
| `ticket-context` | read | Show ticket detail, parent, subtasks, links, and recent comments |
| `ticket-tree` | read | Traverse parent/child issue relationships |
| `comment-list` | read | List comments |
| `comment-add` | write | Add a comment |
| `comment-delete` | write | Delete a comment |
| `transition-list` | read | List available status transitions |
| `transition` | write | Transition ticket status |
| `sprint-list` | read | List board sprints |
| `sprint-resolve` | read | Resolve sprint alias, ID, or name |
| `ticket-sprint-move` | write | Move ticket to sprint or backlog |
| `project-overview` | read | Summarize boards, sprints, recent tickets, and status counts |
| `ticket-create` | write | Create a ticket, optionally then move it to sprint/backlog |
| `ticket-update` | write | Update summary, description, labels, assignee, and related supported fields |

## Read Examples

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js board-list --project SD
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js project-overview --project SD --limit 20 --board-limit 5
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-list --project SD --limit 20
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-list --jql "project = SD AND statusCategory != Done ORDER BY updated DESC" --limit 20
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-show --key SD-123
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-context --key SD-123 --comments 10
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-tree --key SD-123 --depth 2 --limit 50
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js comment-list --key SD-123 --limit 20
```

## Comments

Short comment:

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js comment-add --key SD-123 --body "작업 시작" --dry-run
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js comment-add --key SD-123 --body "작업 시작" --yes
```

Long comment:

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js comment-add --key SD-123 --body-file /private/tmp/jira-comment.md --dry-run
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js comment-add --key SD-123 --body-file /private/tmp/jira-comment.md --yes
```

Delete only after confirming comment ID and ticket key:

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js comment-delete --key SD-123 --comment-id 10001 --dry-run
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js comment-delete --key SD-123 --comment-id 10001 --yes
```

## Transitions

List available transitions first:

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js transition-list --key SD-123
```

Then use an available status exactly:

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js transition --key SD-123 --status "진행 중" --dry-run
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js transition --key SD-123 --status "진행 중" --yes
```

## Sprints

Sprints are attached to Scrum boards, not directly to projects. If a project has multiple Scrum boards, specify `--board-id` or `--board-name`.

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js sprint-list --project SD --board-name "SP 보드" --state active,future
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js sprint-resolve --project SD --target current
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js sprint-resolve --project SD --target next
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js sprint-resolve --project SD --target backlog
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js sprint-resolve --project SD --target id:8242
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js sprint-resolve --project SD --target name:05/03주
```

Sprint target aliases:

| Alias | Meaning |
|---|---|
| `current`, `this-week`, `active`, `이번주` | Earliest active sprint by start date |
| `next`, `next-week`, `future`, `다음주` | Earliest future sprint by start date |
| `backlog`, `none`, `no-sprint`, `백로그` | No sprint/backlog |
| `id:<ID>` or numeric ID | Specific sprint ID |
| `name:<NAME>` or exact name | Specific sprint name |

Move tickets:

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-sprint-move --key SD-123 --project SD --target current --dry-run
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-sprint-move --key SD-123 --project SD --target current --yes
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-sprint-move --key SD-123 --target backlog --dry-run
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-sprint-move --key SD-123 --target backlog --yes
```

## Create And Update Tickets

Create:

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-create --project SD --type 작업 --summary "작업 제목" --parent SD-1 --dry-run
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-create --project SD --type 작업 --summary "작업 제목" --parent SD-1 --yes
```

Create with a description file:

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-create --project SD --type 작업 --summary "작업 제목" --description-file /private/tmp/jira-description.md --dry-run
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-create --project SD --type 작업 --summary "작업 제목" --description-file /private/tmp/jira-description.md --yes
```

Create and place in a sprint:

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-create --project SD --type 작업 --summary "작업 제목" --parent SD-1 --sprint current --dry-run
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-create --project SD --type 작업 --summary "작업 제목" --parent SD-1 --sprint current --yes
```

Update:

```bash
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-update --key SD-123 --summary "새 제목" --dry-run
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-update --key SD-123 --summary "새 제목" --yes
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-update --key SD-123 --description-file /private/tmp/jira-description.md --dry-run
node /Users/jaehan1346/Github/local-jira-cli/local-jira-cli.js ticket-update --key SD-123 --description-file /private/tmp/jira-description.md --yes
```

## Output Contract

Success:

```json
{
  "ok": true,
  "result": {}
}
```

Dry run:

```json
{
  "ok": true,
  "dryRun": true,
  "steps": []
}
```

Failure:

```json
{
  "ok": false,
  "code": "VALIDATION_ERROR",
  "message": "...",
  "details": {}
}
```

Some ACLI commands do not support JSON output; the wrapper may return `result.stdout` with the raw output. Summarize the useful lines instead of pasting everything.
