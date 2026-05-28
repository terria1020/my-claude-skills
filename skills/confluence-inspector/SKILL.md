---
name: confluence-inspector
description: Inspect Confluence content safely through a local Confluence API CLI. Use when the agent needs to check Confluence pages, page bodies, children, search results, labels, properties, versions, comments, or attachments for debugging, implementation, validation, documentation review, project tracking, or content investigation.
---

# Confluence Inspector

## Core Rule

Treat Confluence access as read-only unless the user explicitly asks for a write operation. Prefer search, metadata, bounded lists, and targeted page reads before content changes. Never expose API tokens, secrets, or unnecessary private workspace content in the final answer.

Never read, open, print, search, summarize, or infer from credential-bearing files such as `credentials.json`, `*credentials*.json`, `.env`, `.env.*`, or any file that appears to contain secrets. This rule applies even when the CLI fails, credentials are missing, or reading the file would seem to unblock the task. Use only safe CLI behavior, public command help, and sanitized user-provided context.

## Required CLI

Use this local CLI as the default Confluence access path:

```bash
node ~/Github/local-confluence-api-cli/confluence-api-cli.js
```

### Setup Check

Before running any CLI command, verify the CLI is available:

```bash
[ -f ~/Github/local-confluence-api-cli/confluence-api-cli.js ] || echo "CLI not found"
```

If the file is missing, **stop** and instruct the user to clone it:

```bash
git clone https://github.com/terria1020/local-confluence-api-cli ~/Github/local-confluence-api-cli
```

After cloning, follow the CLI's own README to configure credentials (`CONFLUENCE_DOMAIN`, `CONFLUENCE_EMAIL`, `CONFLUENCE_API_TOKEN`). If credentials or `.env` are not set up, **stop** and direct the user to the CLI's setup guide — do not attempt to read credential files or work around missing auth.

This CLI uses `CONFLUENCE_DOMAIN`, `CONFLUENCE_EMAIL`, and `CONFLUENCE_API_TOKEN` from its configured environment. Do not inspect `.env` files or credential files to debug authentication. Use direct Confluence API calls only when this CLI is missing, fails for an environmental reason, or does not support the required operation.

## Workflow

1. Discover the target:
   - Use the user-provided page ID, title, space ID, or URL-derived ID when available.
   - If the target is described by keyword, use CQL search:
     ```bash
     node ~/Github/local-confluence-api-cli/confluence-api-cli.js --search --cql "type=page AND text~\"<keyword>\"" --limit 20
     ```
   - If a space is known, narrow with `space=<space-key-or-id>` or list pages:
     ```bash
     node ~/Github/local-confluence-api-cli/confluence-api-cli.js --list-pages --space-id <space-id> --limit 25
     ```

2. Inspect structure before content:
   - Page body:
     ```bash
     node ~/Github/local-confluence-api-cli/confluence-api-cli.js --get-page <page-id>
     ```
   - Child pages:
     ```bash
     node ~/Github/local-confluence-api-cli/confluence-api-cli.js --get-children <page-id> --limit 50
     ```
   - Metadata:
     ```bash
     node ~/Github/local-confluence-api-cli/confluence-api-cli.js --list-labels <page-id>
     node ~/Github/local-confluence-api-cli/confluence-api-cli.js --list-properties <page-id>
     node ~/Github/local-confluence-api-cli/confluence-api-cli.js --list-versions <page-id> --limit 10
     ```

3. Inspect related content carefully:
   - Comments: `--list-comments <page-id> --limit 50`
   - Attachments: `--list-attachments <page-id>`
   - Download attachments only when the user asks or the artifact is necessary for the task.
   - Use narrow CQL queries and bounded limits for broad documentation searches.

4. Validate findings:
   - Re-run a targeted read when a result is surprising.
   - Compare page IDs and titles exactly when multiple search results look similar.
   - Include the exact page, space, label, property, version, comment, or attachment scope checked in the final answer.

## Write Safety

- Do not run `--create-page`, `--update-page`, `--delete-page`, `--add-labels`, `--remove-label`, `--set-property`, `--delete-property`, `--add-comment`, `--upload-attachment`, or `--delete-attachment` unless explicitly requested.
- Before writes, read the current page or metadata state and describe the intended change.
- Avoid reading or reporting sensitive content unrelated to the task.
- Do not persist Confluence content into repo files unless the user asks and the output is sanitized.

## Helpful Commands

```bash
# Search pages
node ~/Github/local-confluence-api-cli/confluence-api-cli.js --search --cql "type=page AND text~\"<keyword>\"" --limit 20
```

```bash
# Inspect page and children
node ~/Github/local-confluence-api-cli/confluence-api-cli.js --get-page <page-id>
node ~/Github/local-confluence-api-cli/confluence-api-cli.js --get-children <page-id> --limit 50
```

```bash
# Inspect metadata
node ~/Github/local-confluence-api-cli/confluence-api-cli.js --list-labels <page-id>
node ~/Github/local-confluence-api-cli/confluence-api-cli.js --list-properties <page-id>
node ~/Github/local-confluence-api-cli/confluence-api-cli.js --list-comments <page-id> --limit 50
node ~/Github/local-confluence-api-cli/confluence-api-cli.js --list-attachments <page-id>
```

## Final Answer

Report:

- Which Confluence page, space, metadata, comments, or attachments were inspected.
- Which CQL query or page IDs were used.
- The result, with unrelated private content omitted or redacted.
- Any limits or uncertainty, such as search ambiguity, token access limits, or sampled lists only.
