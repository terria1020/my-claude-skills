---
name: ssh-inspector
description: Execute commands on remote servers through a local SSH credential CLI. Use when the agent needs to check server identity, OS/runtime state, files, logs, processes, ports, disk usage, or service status — or when the user explicitly requests write operations such as file edits, service restarts, deploy scripts, or package changes on a remote host.
---

# SSH Inspector

## Core Rule

Default to read-only. Treat any command that modifies remote state — file writes, service restarts, package changes, deploy scripts, permission changes — as a **write operation** requiring explicit user confirmation before execution.

Never expose secrets in the final answer. Never read, open, print, search, summarize, or infer from credential-bearing files such as `credentials.json`, `*credentials*.json`, `.env`, `.env.*`, SSH private keys, or any file that appears to contain secrets.

## Required CLI

Use this local CLI as the default SSH access path:

```bash
node ~/Github/local-ssh-connect-cli/local-ssh-connect-cli.js
```

### Setup Check

Before running any CLI command, verify the CLI is available:

```bash
[ -f ~/Github/local-ssh-connect-cli/local-ssh-connect-cli.js ] || echo "CLI not found"
```

If the file is missing, **stop** and instruct the user to clone it:

```bash
git clone https://github.com/terria1020/local-ssh-connect-cli ~/Github/local-ssh-connect-cli
```

After cloning, follow the CLI's own README to configure SSH credentials (host, user, key, or password). If credentials are not set up, **stop** and direct the user to the CLI's setup guide — do not attempt to read credential files or work around missing auth.

This CLI manages host, user, key, and password values outside the model context. Use direct `ssh` only when this CLI is missing, fails for an environmental reason, or does not support the required operation.

## Workflow

1. Discover the target access path:
   - Start by listing configured credentials:
     ```bash
     node ~/Github/local-ssh-connect-cli/local-ssh-connect-cli.js --get-credential-list
     ```
   - Select the credential whose safe metadata matches the task.
   - Search repository deployment config, docker compose files, Kubernetes manifests, CI config, README-like docs, and scripts for host, service, path, or environment hints. Do not read `.env*` or credential files.
   - If a matching credential is missing, report the missing credential context and continue with static repository inspection when useful.

2. Verify identity before deeper inspection:
   ```bash
   node ~/Github/local-ssh-connect-cli/local-ssh-connect-cli.js -i <credential-id> -c "hostname && whoami && uname -a"
   ```
   - Confirm that the host, user, and environment match the requested target.
   - Use `--timeout <seconds>` for slow hosts.
   - Use `--accept-new-host-keys` only when the user has clearly accepted first-time host-key trust.

3. Read operations — inspect state with bounded commands:
   - Runtime and services: `systemctl status <service> --no-pager`, `ps aux | grep <name>`, `journalctl -u <service> -n 100 --no-pager`.
   - Files and deployments: `ls -la <path>`, `stat <path>`, `find <path> -maxdepth 2 -type f | head -100`.
   - Logs: `tail -n 100 <log>`, `grep -n "<pattern>" <log> | tail -50`.
   - Network and resources: `ss -tulpn`, `df -h`, `free -h`, `uptime`.

4. Write operations — proceed only with explicit user instruction:
   - **Before executing**, describe the exact command and its effect, and confirm with the user.
   - Prefer reversible approaches: back up files before overwriting, use `--dry-run` flags where available, restart only the specific service rather than the whole host.
   - For high-impact operations (deploy scripts, package upgrades, permission changes, bulk deletes), state the risk explicitly and require unambiguous user confirmation.
   - Do not chain write commands — run one at a time and verify the result before continuing.

5. Validate findings:
   - Re-run targeted commands when a result is surprising.
   - Cross-check runtime state against repository configuration when debugging deployments.
   - Keep command output redacted and summarized in the final answer.

## Write Safety

The following are **write operations** — never run without explicit user request and confirmation:

- File changes: `rm`, `mv`, `cp`, `tee`, `sed -i`, `awk` with output redirection, `chmod`, `chown`
- Service control: `systemctl start/stop/restart/reload`, `service <name> restart`
- Package management: `apt install/remove`, `yum install/remove`, `pip install`
- Deploy scripts: any script in `deploy/`, `scripts/`, `bin/` that modifies state
- Database commands that mutate data

## Helpful Commands

```bash
# List configured credentials
node ~/Github/local-ssh-connect-cli/local-ssh-connect-cli.js --get-credential-list
```

```bash
# Read: bounded remote inspection
node ~/Github/local-ssh-connect-cli/local-ssh-connect-cli.js -i <credential-id> -c "hostname && uptime"
node ~/Github/local-ssh-connect-cli/local-ssh-connect-cli.js -i <credential-id> -c "tail -n 100 /path/to/app.log"
node ~/Github/local-ssh-connect-cli/local-ssh-connect-cli.js -i <credential-id> -c "systemctl status app --no-pager"
```

```bash
# Write: only after explicit user confirmation
node ~/Github/local-ssh-connect-cli/local-ssh-connect-cli.js -i <credential-id> -c "systemctl restart app"
node ~/Github/local-ssh-connect-cli/local-ssh-connect-cli.js -i <credential-id> -c "bash /path/to/deploy.sh"
```

## Final Answer

Report:

- Which credential/host metadata was used, without secrets.
- Which commands were run and whether they were read or write operations.
- The result, with sensitive values redacted.
- Any limits or uncertainty, such as missing credentials, sampled logs only, or inaccessible paths.
