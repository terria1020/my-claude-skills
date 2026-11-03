# local-ssh-connect-cli reference (v1.1+)

Repository: https://github.com/terria1020/local-ssh-connect-cli — run `--help` for the authoritative, current text.

## Targets

| Option | Meaning |
| --- | --- |
| `-i, --id <id[,id...]>` | Credential id(s); comma-separated and/or repeated |
| `--all` | Every credential in `ssh-credentials.json` |
| `--get-credential-list` | Safe metadata only (id, name, host, port, username, authType, note) |

## What to run (pick one)

| Form | Meaning |
| --- | --- |
| `-c "<command>"` | Remote command passed to ssh as-is |
| `-c -` | Read a script from stdin (heredoc) — avoids local shell quoting |
| `--script-file <path>` | Read a script from a local file; `--shell <name>` selects the interpreter (`<shell> -s`, default `sh`) |
| `--check` | Connect + authenticate only (remote no-op `true`); no command needed |
| `tail --file <p> [-n 50] [--grep t] [--follow --duration s]` | Last N lines, remote grep; `--follow` streams for `--duration` seconds (default 30) and then succeeds |
| `get <remote> <local> [--force]` | Download. Several hosts → `<local>/<id>/<name>` |
| `put <local> <remote> [--force] [--mode 0644]` | Upload, atomic. Existing remote file → exit 17 unless `--force` |

Directories are not supported by `get`/`put`. The subcommand word may appear anywhere among the options.

## Execution options

| Option | Default | Meaning |
| --- | --- | --- |
| `--concurrency <n>` | 4 | Parallel hosts (one connection per host) |
| `--timeout <s>` | 15 | SSH connect timeout |
| `--exec-timeout <s>` | 0 (off) | Kill a target after N seconds in total |
| `--keepalive <s>` | 30 | `ServerAliveInterval`; 0 disables |
| `--retries <n>` / `--retry-delay <s>` | 2 / 2 | Retries (exponential backoff) for transient connection failures only |
| `--port <n>` | credential's | Override port |
| `--accept-new-host-keys` | off | Trust and persist *new* host keys (still fails on changed keys) |
| `--no-strict-host-key-checking` | off | Disables host-key verification — avoid |
| `--ssh-path`, `--sshpass-path`, `--credentials-path` | | Binary / file overrides |

## Output

| Option | Meaning |
| --- | --- |
| `--output text\|json\|ndjson` (`--json`, `--ndjson`) | Output format, default `text` |
| `--dry-run` | Print the planned invocation (secrets masked), run nothing |
| `--verbose` | Also print internal logs to stderr |

### `--json`

```json
{"ok":false,"total":2,"succeeded":1,"failed":1,"results":[
  {"id":"web1","host":"…","ok":true,"exitCode":0,"errorKind":null,"attempts":1,
   "durationMs":120,"stdout":"…","stderr":"","truncated":false,"timedOut":false},
  {"id":"web2","host":"…","ok":false,"exitCode":null,"errorKind":"auth_failed","attempts":1,
   "durationMs":90,"stdout":"","stderr":"Permission denied …","truncated":false,"timedOut":false}]}
```

`get`/`put` results add `"transfer":{"direction","localPath","remotePath","bytes","sha256"}`. Usage/config errors in JSON mode print `{"ok":false,"error":{"kind":"usage|config_error","message":"…"}}`.

### `--ndjson`

One event per line: `start`, `stdout`, `stderr`, `retry`, `exit` (with `ok`, `exitCode`, `errorKind`, `attempts`, `transfer?`), `summary`.

### `text`

Single target: raw passthrough. Several targets: each line prefixed `[id] `. Diagnostics are `[lssh] …` lines on stderr.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | All targets succeeded |
| *N* | Single target: the remote command's own exit code |
| `255` | Single target: SSH-level failure (auth, network, host key …) |
| `124` | Single target: `--exec-timeout` hit |
| `127` | Single target: could not start ssh/sshpass |
| `74` | Single target: local I/O error during `get`/`put` |
| `2` | Usage or configuration error — nothing was executed |
| `1` | Several targets and at least one failed |

v1.0 returned `1` for every failure; scripts must not rely on `== 1` any more.

## errorKind values

`remote_nonzero`, `auth_failed`, `too_many_auth`, `host_key`, `dns`, `connection_refused`, `connect_timeout`*, `connection_reset`*, `connection_lost`, `ssh_error`, `exec_timeout`, `spawn_error`, `io_error`, `config_error` (\* = retried automatically). A remote command that prints "Permission denied" itself is `remote_nonzero`, not `auth_failed`.

## Behavior notes

- Auth options are pinned: key auth offers only the configured key (`IdentitiesOnly`, `BatchMode`); password auth makes a single attempt (`NumberOfPasswordPrompts=1`, no pubkey). Passwords are passed to `sshpass` through the environment, never argv.
- Base64 secrets in `ssh-credentials.json`: a trailing newline (from `echo pw | base64`) is stripped automatically.
- `tail --follow`: after the session ends, the remote `tail -f` may linger until its next write; prefer repeated `-n` reads when that matters.
- Logs go to `logs/` in the CLI's directory (`LSSH_LOG_DIR` to change); executed command text is not logged.
