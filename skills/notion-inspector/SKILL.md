---
name: notion-inspector
description: Inspect Notion workspace content safely through a local Notion API CLI. Use when the agent needs to check Notion pages, databases, database rows, properties, page blocks, tables, child pages, comments, or workspace search results for debugging, implementation, validation, documentation review, project tracking, or content investigation.
---

# Notion Inspector

## Core Rule

Treat Notion access as read-only unless the user explicitly asks for a write operation. Prefer search, metadata, bounded page/database reads, and block inspection before content changes. Never expose secrets or unnecessary private workspace content in the final answer.

Never read, open, print, search, summarize, or infer from credential-bearing files such as `credentials.json`, `*credentials*.json`, `.env`, `.env.*`, or any file that appears to contain secrets. This rule applies even when the CLI fails, credentials are missing, or reading the file would seem to unblock the task. Use only safe CLI behavior, public command help, and sanitized user-provided context.

## Required CLI

Use this local CLI as the default Notion access path:

```bash
node ~/Github/notion-api-cli/notion-api-cli.js
```

### Setup Check

Before running any CLI command, verify the CLI is available:

```bash
[ -f ~/Github/notion-api-cli/notion-api-cli.js ] || echo "CLI not found"
```

If the file is missing, **stop** and instruct the user to clone it:

```bash
git clone https://github.com/terria1020/notion-api-cli ~/Github/notion-api-cli
```

After cloning, follow the CLI's own README to configure credentials (`NOTION_API_TOKEN`). If credentials or `.env` are not set up, **stop** and direct the user to the CLI's setup guide — do not attempt to read credential files or work around missing auth.

This CLI uses `NOTION_API_TOKEN` from its configured environment. Do not inspect `.env` files or credential files to debug authentication. Use direct Notion API calls only when this CLI is missing, fails for an environmental reason, or does not support the required operation.

## Keeping Reads Small

The CLI emits compact JSON with empty fields stripped. Narrow the read further rather than
fetching broadly and filtering in your own head:

- `--filter '<JSON>'` and `--sorts '<JSON>'` on `--query-database` push selection to Notion.
- `--properties Name,Status` fetches only the columns you need.
- `--no-ids` drops ids and urls. Use it only when you will not act on the results — ids are
  required for `--get-table`, `--update-block`, and any follow-up write.
- `--max-depth <n>` bounds `--find-child-pages`; `--deep` (descend into child pages) is off
  by default and should stay off unless the task is about a whole subtree.
- `--verbose-fields` and `--pretty` restore full/indented output when a value looks wrong
  and you need to see the raw Notion shape.

## Workflow

1. Discover the target:
   - Use the user-provided page/database URL or ID when available.
   - If the target is described by keyword, search roots first:
     ```bash
     node ~/Github/notion-api-cli/notion-api-cli.js --search-roots --query "<keyword>" --type all --limit 20
     ```
   - Narrow by page title, database name, parent page, project name, or repository context.

2. Inspect structure before content:
   - Page metadata:
     ```bash
     node ~/Github/notion-api-cli/notion-api-cli.js --get-page <page-id-or-url>
     ```
   - Page blocks:
     ```bash
     node ~/Github/notion-api-cli/notion-api-cli.js --get-page-blocks <page-id-or-url> --limit 100
     ```
   - Database schema:
     ```bash
     node ~/Github/notion-api-cli/notion-api-cli.js --get-database <db-id-or-url>
     ```
   - Database rows — read the schema first, then request only the columns you need:
     ```bash
     node ~/Github/notion-api-cli/notion-api-cli.js --query-database <db-id-or-url> --limit 20 \
       --properties "<col1>,<col2>" --filter '{"property":"Status","select":{"equals":"Done"}}'
     ```

3. Inspect related content carefully:
   - Child pages: `--find-child-pages <page-id-or-url> --limit 100`
   - Database page rows: `--list-database-pages <db-id-or-url> --limit 50`
   - Comments: `--list-comments <target-id-or-url> --limit 50`
   - Tables: first get block IDs with `--get-page-blocks`, then inspect table blocks with `--get-table <block-id>`.
   - Use `--auto-expand` only when row content is necessary and keep limits bounded.

4. Validate findings:
   - Re-run a targeted read when a result is surprising.
   - Compare page/database IDs exactly when multiple search results look similar.
   - Include the exact page, database, property, block, or comment scope checked in the final answer.

## Write Safety

- Do not run `--update-page`, `--append-blocks`, `--update-block`, `--delete-block`, `--create-table`, `--update-table-row`, `--append-table-row`, `--create-comment`, or `--reply-comment` unless explicitly requested.
- Before writes, read the current page/block/database state and describe the intended change.
- Avoid reading or reporting sensitive content unrelated to the task.
- Do not persist Notion content into repo files unless the user asks and the output is sanitized.

## Helpful Commands

```bash
# Search workspace roots
node ~/Github/notion-api-cli/notion-api-cli.js --search-roots --query "<keyword>" --type all --limit 20
```

```bash
# Inspect page and blocks
node ~/Github/notion-api-cli/notion-api-cli.js --get-page <page-id-or-url>
node ~/Github/notion-api-cli/notion-api-cli.js --get-page-blocks <page-id-or-url> --limit 100
```

```bash
# Inspect database
node ~/Github/notion-api-cli/notion-api-cli.js --get-database <db-id-or-url>
node ~/Github/notion-api-cli/notion-api-cli.js --query-database <db-id-or-url> --limit 20
```

## Final Answer

Report:

- Which Notion page, database, block, table, or comments were inspected.
- Which properties, rows, or blocks were checked.
- The result, with unrelated private content omitted or redacted.
- Any limits or uncertainty, such as search ambiguity, token access limits, or sampled rows only.
