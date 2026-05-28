---
name: gws-sheets
description: Read and write Google Sheets via the local gws CLI. Use when the agent needs to read cell values, write data or formulas, apply formatting (bold, background color, font color, borders, column auto-resize), inspect sheet metadata, or answer questions about spreadsheet content. Requires gws CLI installed and authenticated locally.
---

# GWS Sheets

## Core Rule

Use the local `gws` CLI for all Google Sheets operations. Never read credential files or expose authentication tokens. Default to the minimum required scope: read-only unless the task explicitly requires writing.

## Required CLI

```bash
gws sheets spreadsheets ...
gws drive files get ...
```

`gws` must be installed and authenticated locally. If a command returns an auth error, stop and report it rather than retrying with different credentials.

## Workflow

### 1. Extract spreadsheetId

URL pattern: `https://docs.google.com/spreadsheets/d/{spreadsheetId}/...`

Parse the spreadsheetId from the URL the user provides. Never guess or construct spreadsheet URLs.

### 2. Confirm file type

```bash
gws drive files get --params '{"fileId": "{spreadsheetId}", "fields": "id,name,mimeType"}' 2>&1
```

| mimeType | Action |
|---|---|
| `application/vnd.google-apps.spreadsheet` | Native Sheets — use `gws sheets` directly |
| `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | xlsx export — download and parse with openpyxl |

### 3. Get sheet list (when sheet name is unknown)

```bash
gws sheets spreadsheets get \
  --params '{"spreadsheetId": "{spreadsheetId}", "fields": "sheets.properties"}' 2>&1
```

Use `sheetId` (integer) for formatting requests and `title` for value range references.

### 4. Read values

```bash
# Full sheet
gws sheets spreadsheets values get \
  --params '{"spreadsheetId": "{spreadsheetId}", "range": "{시트명}"}' \
  --format table 2>&1

# Specific range
gws sheets spreadsheets values get \
  --params '{"spreadsheetId": "{spreadsheetId}", "range": "{시트명}!A1:G20"}' 2>&1
```

### 5. Write values and formulas

```bash
gws sheets spreadsheets values update \
  --params '{
    "spreadsheetId": "{spreadsheetId}",
    "range": "{시트명}!A1",
    "valueInputOption": "USER_ENTERED"
  }' \
  --json '{
    "range": "{시트명}!A1",
    "majorDimension": "ROWS",
    "values": [
      ["헤더1", "헤더2", "헤더3"],
      ["값1",   "값2",   "=SUM(A2:B2)"]
    ]
  }' 2>&1
```

- `USER_ENTERED`: formulas (`=SUM(...)`, `=AVERAGE(...)`, etc.) are evaluated.
- `RAW`: values stored as-is without formula parsing.

### 6. Apply formatting (bold, color, borders, auto-resize)

Use `batchUpdate` with one or more request objects. All range coordinates are zero-indexed.

```bash
gws sheets spreadsheets batchUpdate \
  --params '{"spreadsheetId": "{spreadsheetId}"}' \
  --json '{
    "requests": [ ...request objects... ]
  }' 2>&1
```

#### Request types

**Bold + background color + text color (repeatCell)**
```json
{
  "repeatCell": {
    "range": {
      "sheetId": 0,
      "startRowIndex": 0, "endRowIndex": 1,
      "startColumnIndex": 0, "endColumnIndex": 7
    },
    "cell": {
      "userEnteredFormat": {
        "backgroundColor": {"red": 0.2, "green": 0.4, "blue": 0.8},
        "textFormat": {
          "bold": true,
          "foregroundColor": {"red": 1, "green": 1, "blue": 1},
          "fontSize": 11
        },
        "horizontalAlignment": "CENTER",
        "verticalAlignment": "MIDDLE"
      }
    },
    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment,verticalAlignment)"
  }
}
```

**Borders (updateBorders)**
```json
{
  "updateBorders": {
    "range": {
      "sheetId": 0,
      "startRowIndex": 0, "endRowIndex": 10,
      "startColumnIndex": 0, "endColumnIndex": 7
    },
    "top":             {"style": "SOLID_MEDIUM", "color": {"red": 0.2, "green": 0.4, "blue": 0.8}},
    "bottom":          {"style": "SOLID_MEDIUM", "color": {"red": 0.2, "green": 0.4, "blue": 0.8}},
    "left":            {"style": "SOLID_MEDIUM", "color": {"red": 0.2, "green": 0.4, "blue": 0.8}},
    "right":           {"style": "SOLID_MEDIUM", "color": {"red": 0.2, "green": 0.4, "blue": 0.8}},
    "innerHorizontal": {"style": "SOLID",        "color": {"red": 0.7, "green": 0.7, "blue": 0.7}},
    "innerVertical":   {"style": "SOLID",        "color": {"red": 0.7, "green": 0.7, "blue": 0.7}}
  }
}
```

Border styles: `SOLID`, `SOLID_MEDIUM`, `SOLID_THICK`, `DASHED`, `DOTTED`, `DOUBLE`, `NONE`

**Column auto-resize (autoResizeDimensions)**
```json
{
  "autoResizeDimensions": {
    "dimensions": {
      "sheetId": 0,
      "dimension": "COLUMNS",
      "startIndex": 0,
      "endIndex": 7
    }
  }
}
```

### 7. Read xlsx (Office format fallback)

```bash
# Download
gws drive files get \
  --params '{"fileId": "{spreadsheetId}", "alt": "media"}' \
  --output sheet_{spreadsheetId}.xlsx 2>&1

# List sheets
uv run --with openpyxl python3 -c "
import openpyxl
wb = openpyxl.load_workbook('sheet_{spreadsheetId}.xlsx', read_only=True, data_only=True)
print('시트 목록:', wb.sheetnames)
"

# Read sheet
uv run --with openpyxl python3 -c "
import openpyxl
wb = openpyxl.load_workbook('sheet_{spreadsheetId}.xlsx', read_only=True, data_only=True)
ws = wb['{시트명}']
for i, row in enumerate(ws.iter_rows(values_only=True)):
    if any(v is not None for v in row):
        print(f'행{i+1}:', list(row))
"
```

## Final Answer

Report:
- Spreadsheet name and ID inspected.
- Sheets and ranges accessed or written.
- Summary of data read or changes applied.
- Any errors or limitations encountered.
