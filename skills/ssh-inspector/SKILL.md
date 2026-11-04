---
name: ssh-inspector
description: Execute commands on remote servers through a local SSH credential CLI (local-ssh-connect-cli v1.1+). Use when the agent needs to check server identity, OS/runtime state, files, logs, processes, ports, disk usage, or service status on one or many hosts — tail logs, download files, or, only when the user explicitly requests it, perform write operations such as file uploads, service restarts, deploy scripts, or package changes on a remote host.
---

# SSH Inspector

## Core Rule

Default to read-only. Treat any command that modifies remote state — file writes, **file uploads (`put`)**, service restarts, package changes, deploy scripts, permission changes — as a **write operation** requiring explicit user confirmation before execution.

Never expose secrets in the final answer. Never read, open, print, search, summarize, or infer from credential-bearing files such as `ssh-credentials.json`, `credentials.json`, `*credentials*.json`, `.env`, `.env.*`, SSH private keys, or any file that appears to contain secrets. Never download such files from a remote host either.

## Required CLI

The CLI is [local-ssh-connect-cli](https://github.com/terria1020/local-ssh-connect-cli) **v1.1 or newer**. It keeps host, user, key, and password values outside the model context. Use direct `ssh` only when this CLI is missing, fails for an environmental reason, or does not support the required operation.

### Invocation

Examples in this skill write the CLI as `lssh`. Resolve what is actually available **in the shell your tool runs in** (non-interactive — aliases from `~/.zshrc`/`~/.bashrc` are **not** loaded there, so an alias created with `--print-alias` does not count):

| How it is installed | Works in agent shells? | Use |
| --- | --- | --- |
| `npm link` (a real `lssh` / `local-ssh-connect-cli` executable on `PATH`) | yes | `lssh ...` |
| Shell alias (`--print-alias`) | **no** (interactive shells only) | use the function below |
| Only the repository checkout | yes | `node ~/Github/local-ssh-connect-cli/local-ssh-connect-cli.js ...` |

Every Bash call is a fresh shell, so define the fallback **inside the same command** that uses it:

```bash
command -v lssh >/dev/null 2>&1 || lssh() { node "$HOME/Github/local-ssh-connect-cli/local-ssh-connect-cli.js" "$@"; }
lssh -i <id> --check --json
```

**Do not store the command in a string variable** (`L="node …/cli.js"; $L -i …`). zsh — the default shell on macOS — does not word-split unquoted variables, so it looks for a command literally named `node /…/cli.js` and fails with `command not found`; any `2>&1 | python3 -c 'json.load…'` after it then dies with a misleading `JSONDecodeError … line 1 column 1`. Use the function above (or `lssh`) instead, and do not append `2>&1` before a JSON parser — in `--json` mode the result is on stdout only.

If no short command is installed and the user wants one, suggest `npm link` in the CLI directory (works everywhere), or `lssh --print-alias` / `node …/local-ssh-connect-cli.js --print-alias` for an alias line they can add to their profile (interactive shells only). Do not edit shell profiles yourself.

### Setup Check

Run this once before any CLI command. It resolves the invocation, then checks the CLI exists and is new enough:

```bash
if command -v lssh >/dev/null 2>&1; then
  echo "invocation: lssh (on PATH)"
elif [ -f "$HOME/Github/local-ssh-connect-cli/local-ssh-connect-cli.js" ]; then
  lssh() { node "$HOME/Github/local-ssh-connect-cli/local-ssh-connect-cli.js" "$@"; }
  echo "invocation: node ~/Github/local-ssh-connect-cli/local-ssh-connect-cli.js (define the lssh() function above in each command)"
else
  echo "CLI not found"; exit 1
fi
lssh --help | grep -q -- '--ndjson' && echo "CLI v1.1+ ok" || echo "CLI too old (need v1.1+)"
```

- Missing → **stop** and instruct the user:
  ```bash
  git clone https://github.com/terria1020/local-ssh-connect-cli ~/Github/local-ssh-connect-cli
  cd ~/Github/local-ssh-connect-cli && npm install
  ```
  Optionally `npm link` there to get a real `lssh` command.
- Too old → ask the user to `git -C ~/Github/local-ssh-connect-cli pull && npm install`. The v1.0 flags (`-i`, `-c`, `--get-credential-list`) still work, but without JSON output, multi-host, `--check`, or `tail`/`get`/`put`; fall back to single-host `-i/-c` usage and say so.
- Credentials not configured → **stop** and direct the user to the CLI's README (`ssh-credentials.json`). Do not read credential files or work around missing auth.

Read the CLI's own `--help` once per session — it is written for agents and lists the current options, exit codes, and `errorKind` values. Details also in `references/local-ssh-connect-cli.md`.

## Workflow

1. **Discover the target access path**
   - List credentials (safe metadata only):
     ```bash
     lssh --get-credential-list
     ```
   - Pick the credential(s) whose metadata matches the task. Search repository deployment config, docker compose files, Kubernetes manifests, CI config, README-like docs, and scripts for host/service/path hints. Do not read `.env*` or credential files.
   - If a matching credential is missing, report the missing credential context and continue with static repository inspection when useful.

2. **Check connectivity first** (connect + authentication only; runs the no-op `true`):
   ```bash
   lssh -i <id>[,<id>...] --check --json      # or --all --check --json
   ```
   Handle failures by `errorKind` (see table below) before attempting real work.

3. **Verify identity**
   ```bash
   lssh -i <id> --json -c "hostname && whoami && uname -a"
   ```
   Confirm host, user, and environment match the requested target before deeper inspection.

4. **Read operations** — bounded commands, machine-readable output:
   - Prefer `--json` (single result document) for short commands and `--ndjson` for long-running or streaming ones. Parse `results[].errorKind` / `exitCode` instead of scraping stderr.
   - Several hosts: `-i web1,web2,db1` (or `--all`) runs in parallel (`--concurrency`, default 4). Compare per-host results rather than looping in the shell.
   - Logs: `lssh -i <id> tail --file <log> -n 100 --grep <text>`; bounded live view: `tail --file <log> --follow --duration 30` (ends by itself and counts as success).
   - Files: `lssh -i <id> get <remote-path> <local-path>` downloads binary-safe and reports `bytes`/`sha256`. Download only non-sensitive files, into a scratch/temp directory, and never overwrite local files without the user's say-so (`--force`).
   - Services/resources: `systemctl status <svc> --no-pager`, `journalctl -u <svc> -n 100 --no-pager`, `ss -tulpn`, `df -h`, `free -h`, `uptime`, `ps aux | grep <name>`.
   - Slow hosts: `--timeout <s>` (connect) and `--exec-timeout <s>` (whole command). Long commands survive idle drops via the default keepalive (`--keepalive`).

5. **Write operations** — only with explicit user instruction:
   - **Dry-run first**, show the user the plan, then confirm:
     ```bash
     lssh -i <id> --dry-run -c "systemctl restart app"
     ```
     `--dry-run` prints the exact invocation with secrets masked and executes nothing. For `put`, it also shows the local file and size.
   - Describe the exact command and its effect and wait for confirmation. Prefer reversible approaches: back up before overwriting, restart only the specific service, avoid whole-host operations.
   - `put <local> <remote>` refuses to overwrite existing remote files unless `--force`; only add `--force` when the user explicitly agreed to overwrite that file. Use `--mode` when permissions matter.
   - Multi-host writes (`-i a,b,c` / `--all`) multiply the blast radius: confirm the host list explicitly, and consider one canary host first.
   - Do not chain write commands — run one at a time and verify the result (re-read file/status, compare `sha256`) before continuing.

6. **Validate findings**
   - Re-run targeted commands when a result is surprising.
   - Cross-check runtime state against repository configuration when debugging deployments.
   - Keep command output redacted and summarized in the final answer.

## Quoting and Multi-line Commands (zsh/bash safe)

Quote-heavy or multi-line commands get mangled by the local shell (`$vars`, backticks, `!`). Send the script on stdin through a quoted heredoc so it reaches the remote shell untouched:

```bash
lssh -i <id> --json -c - <<'SCRIPT'
for f in /var/log/app/*.log; do echo "$f: $(wc -l < "$f")"; done
SCRIPT
```

Use `--script-file <path>` for an existing script and `--shell bash` when the script needs bash. Scripts that modify state are write operations like any other command.

## Failure Handling (`errorKind`)

| errorKind | Meaning | What to do |
| --- | --- | --- |
| `remote_nonzero` | The command ran and exited non-zero (`exitCode` is the remote code) | Normal command failure — read `stderr`; not a connection problem |
| `auth_failed` | Wrong/rejected credentials | Stop. Do not retry in a loop (can lock accounts). Tell the user which credential id failed |
| `too_many_auth` | Server rejected after too many key offers | Report; usually a server-side `MaxAuthTries` or key mismatch |
| `host_key` | Unknown/changed host key | Stop. Use `--accept-new-host-keys` only if the user clearly accepts first-time trust; never for a *changed* key. Never use `--no-strict-host-key-checking` unless the user asks |
| `dns` / `connection_refused` | Wrong host/port or service down | Report; check credential metadata and the port |
| `connect_timeout` / `connection_reset` | Transient network or server rate limiting | Already retried automatically (`--retries`, default 2). If it persists, lower `--concurrency` or retry later |
| `connection_lost` / `ssh_error` | Connection dropped / unclassified SSH failure | Report stderr (redacted); retry once at most |
| `exec_timeout` | `--exec-timeout` hit | Report; raise the limit only if the command is legitimately slow |
| `config_error` / `io_error` | Local problem (missing key file, bad id, local file) | Fix locally; nothing ran remotely |
| *(no JSON at all, `command not found`)* | The shell could not run the CLI — often a `$VAR` command in zsh, or `lssh` being an alias | See **Invocation**; nothing reached the CLI |

Process exit codes: `0` ok; single host → remote exit code, `255` SSH-level failure, `124` exec timeout, `127` cannot start ssh, `74` local I/O error; `2` usage/config error; `1` several hosts and at least one failed. Prefer `--json` and inspect each result.

## Write Safety

The following are **write operations** — never run without explicit user request and confirmation:

- File changes: `rm`, `mv`, `cp`, `tee`, `sed -i`, `awk` with output redirection, `chmod`, `chown`, and **`lssh put`**
- Service control: `systemctl start/stop/restart/reload`, `service <name> restart`
- Package management: `apt install/remove`, `yum install/remove`, `pip install`
- Deploy scripts: any script in `deploy/`, `scripts/`, `bin/` that modifies state
- Database commands that mutate data
- Anything combined with `--force`, `--all`, or a multi-host list

Read-only subcommands: `--check`, `tail`, `get`, `--get-credential-list`, `--dry-run`.

## Helpful Commands

```bash
# Credentials and connectivity
lssh --get-credential-list
lssh --all --check --json

# Read
lssh -i <id> --json -c "hostname && uptime"
lssh -i web1,web2 --json -c "df -h /"
lssh -i <id> tail --file /var/log/app.log -n 200 --grep ERROR
lssh -i <id> tail --file /var/log/app.log --follow --duration 30 --ndjson
lssh -i <id> get /var/log/app.log /tmp/inspect/app.log

# Write: dry-run, then only after explicit user confirmation
lssh -i <id> --dry-run -c "systemctl restart app"
lssh -i <id> -c "systemctl restart app"
lssh -i <id> put ./app.conf /etc/app/app.conf          # add --force only if overwrite was approved
```

## Final Answer

Report:

- Which credential/host metadata was used, without secrets.
- Which commands were run and whether they were read or write operations (including any `put`/`get`, with paths and `sha256`).
- Per-host results; for failures, the `errorKind` and whether retries happened (`attempts`).
- The result, with sensitive values redacted.
- Any limits or uncertainty, such as missing credentials, sampled logs only, truncated output (`truncated: true`), or inaccessible paths.
