# Metadata Query Recipes

Use these SQL snippets through `/Users/jaehan1346/Github/local-rdbms-connect-cli/local-rdbms-connect-cli.js` after identifying the database engine and credential. Prefer the CLI's built-in options such as `--show-tables`, `--show-views`, `--describe`, `--show-indexes`, and `--count-rows` when they answer the question directly.

## PostgreSQL

List base tables:

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;
```

List views:

```sql
SELECT table_schema, table_name
FROM information_schema.views
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;
```

List columns:

```sql
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'table_name'
ORDER BY ordinal_position;
```

List indexes:

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'table_name'
ORDER BY indexname;
```

Get view definition:

```sql
SELECT pg_get_viewdef('public.view_name'::regclass, true);
```

## MySQL / MariaDB

List tables and views:

```sql
SHOW FULL TABLES;
```

List columns:

```sql
SELECT column_name, column_type, is_nullable, column_default, column_key
FROM information_schema.columns
WHERE table_schema = DATABASE()
  AND table_name = 'table_name'
ORDER BY ordinal_position;
```

Get view definition:

```sql
SHOW CREATE VIEW view_name;
```

## SQLite

List tables and views:

```sql
SELECT type, name
FROM sqlite_master
WHERE type IN ('table', 'view')
ORDER BY type, name;
```

List columns:

```sql
PRAGMA table_info('table_name');
```

List indexes:

```sql
PRAGMA index_list('table_name');
```

Get view definition:

```sql
SELECT sql
FROM sqlite_master
WHERE type = 'view'
  AND name = 'view_name';
```

## Data Checks

Use bounded, column-specific checks:

```sql
SELECT COUNT(*) AS row_count FROM table_name;
```

```sql
SELECT COUNT(*) AS null_count
FROM table_name
WHERE important_column IS NULL;
```

```sql
SELECT important_status, COUNT(*) AS count
FROM table_name
GROUP BY important_status
ORDER BY count DESC;
```

```sql
SELECT id, created_at, status
FROM table_name
ORDER BY created_at DESC
LIMIT 20;
```
