---
name: database-inspector
description: Inspect database structure and contents safely. Use when the agent needs to check database fields, table definitions, view definitions, indexes, constraints, sample rows, counts, data quality, or any other database state for debugging, implementation, validation, migration review, or incident investigation.
---

# Database Inspector

## Core Rule

Treat database access as read-only unless the user explicitly asks for a write operation. Prefer metadata queries and bounded samples before reading data. Never expose secrets in the final answer.

Never read, open, print, search, summarize, or infer from credential-bearing files such as `credentials.json`, `*credentials*.json`, `.env`, `.env.*`, or any file that appears to contain secrets. This rule applies even when the CLI fails, credentials are missing, or reading the file would seem to unblock the task. Use only safe CLI metadata, environment-independent repository configuration, migrations, entities, and sanitized user-provided context.

## Required CLI

Use this local CLI as the default database access path:

```bash
node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js
```

### Setup Check

Before running any CLI command, verify the CLI is available:

```bash
[ -f ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js ] || echo "CLI not found"
```

If the file is missing, **stop** and instruct the user to clone it:

```bash
git clone https://github.com/terria1020/local-rdbms-connect-cli ~/Github/local-rdbms-connect-cli
```

After cloning, follow the CLI's own README to configure credentials and connection settings. If credentials or `.env` are not set up, **stop** and direct the user to the CLI's setup guide — do not attempt to read credential files or work around missing auth.

This CLI manages credentials outside the model context and supports MariaDB, MySQL, PostgreSQL, and Elasticsearch. Use direct database clients only when this CLI is missing, fails for an environmental reason, or does not support the required database type.

## Workflow

1. Discover the database access path from the repository or environment:
   - Start by listing available configured credentials:
     ```bash
     node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js --get-credential-list
     ```
   - Select the credential whose `type`, `database`, `host`, `allowedTables`, and `note` match the task.
   - Search for non-secret connection hints in docker compose files, Kubernetes manifests, application config, ORM config, migration tools, and README-like setup docs. Do not read `.env*` files.
   - Use repository configuration to identify the intended database, then map it to a configured CLI credential when possible.
   - If a matching CLI credential is missing, report the missing credential context and continue with static schema inspection from migrations/entities when possible.

2. Identify the database engine and schema source:
   - PostgreSQL: use CLI type `postgresql` with the selected credential.
   - MySQL/MariaDB: use CLI type `mysql` or `mariadb` with the selected credential.
   - Elasticsearch: use CLI type `elasticsearch` with `-p`, `-Q`, `-D`, and `-X` as needed.
   - SQLite: use `sqlite3` against the local database file.
   - Oracle, SQL Server, ClickHouse, BigQuery, Snowflake, Redis, and other stores: use the project's existing CLI, SDK, container, or documented workflow when the required CLI cannot support the store.

3. Inspect structure before content:
   - List schemas/databases, tables, views, columns, data types, nullability, defaults, primary keys, foreign keys, indexes, and view definitions relevant to the task.
   - Cross-check runtime schema against migrations or entity definitions if the task concerns drift, bugs, or missing fields.
   - For large systems, narrow by service/module/table name before broad enumeration.

4. Inspect data carefully:
   - Use `COUNT(*)`, grouped counts, min/max timestamps, and null/duplicate checks before row samples.
   - Always bound row reads with `LIMIT`/equivalent and select only needed columns.
   - Redact or avoid sensitive columns such as passwords, tokens, keys, auth headers, personal identifiers, email, phone, address, resident IDs, and payment data.
   - Prefer aggregate evidence over raw rows in the final answer.

5. Validate findings:
   - Re-run a targeted query when a result is surprising.
   - Compare schema names and case sensitivity exactly as the engine stores them.
   - Include the exact table/view/column names checked and the query intent in the final answer.

## Query Safety

- Use read-only transaction/session settings where supported.
- Avoid `SELECT *`; name columns explicitly.
- Avoid unbounded joins and full scans on production-sized tables. Use filters, time windows, keys, or metadata tables.
- Do not run DDL, DML, migrations, truncates, vacuum/analyze, locks, privilege changes, or stored procedures unless explicitly requested and safe to do.
- Do not persist extracted data into repo files unless the user asks and the output is sanitized.

## Helpful Commands

Use these patterns with the required CLI. Replace `<type>`, `<credential-id>`, and names after selecting a credential from `--get-credential-list`.

```bash
# List configured credentials
node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js --get-credential-list
```

```bash
# RDBMS metadata
node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js -t <type> -i <credential-id> --show-databases
node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js -t <type> -i <credential-id> --show-tables
node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js -t <type> -i <credential-id> --show-tables-and-schema
node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js -t <type> -i <credential-id> --show-views
node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js -t <type> -i <credential-id> --describe table_name
node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js -t <type> -i <credential-id> --show-indexes table_name
node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js -t <type> -i <credential-id> --count-rows table_name
```

```bash
# Bounded data query
node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js -t <type> -i <credential-id> -q 'SELECT id, created_at, status FROM table_name ORDER BY created_at DESC LIMIT 20' --output-format json --max-rows 20
```

```bash
# Elasticsearch
node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js -t elasticsearch -i <credential-id> -p '/_cluster/health'
node ~/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js -t elasticsearch -i <credential-id> -X GET -p '/_search' -Q 'size=1'
```

For engine-specific metadata query recipes, read `references/metadata-queries.md`.

## Final Answer

Report:

- Which database/source was inspected.
- Which tables, views, fields, or data checks were verified.
- The result, with sensitive values redacted.
- Any limits or uncertainty, such as missing credentials, stale migrations, or sampled data only.
