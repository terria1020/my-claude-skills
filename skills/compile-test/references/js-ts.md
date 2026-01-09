# JavaScript / TypeScript Compile Test

## TypeScript

### Type Check (without emit)

```bash
# Check all files per tsconfig.json
npx tsc --noEmit

# Specific file
npx tsc --noEmit path/to/file.ts

# With specific config
npx tsc --noEmit -p tsconfig.json

# Strict mode
npx tsc --noEmit --strict
```

**Success**: No output, exit code 0

**Failure**: Shows file, line, and type error

### Build (with emit)

```bash
# Full build
npx tsc

# Watch mode (for development)
npx tsc --watch
```

## JavaScript

JavaScript has no compile step, but can validate with:

### ESLint Syntax Check

```bash
# Check file
npx eslint path/to/file.js

# Check directory
npx eslint src/

# Only errors (no warnings)
npx eslint --quiet src/
```

### Node Syntax Check

```bash
# Check syntax only (no execution)
node --check path/to/file.js
```

## Project Detection

| File | Project Type |
|------|--------------|
| `tsconfig.json` | TypeScript |
| `jsconfig.json` | JavaScript with tooling |
| `package.json` + `*.ts` | TypeScript (npm) |
| `package.json` + `*.js` | JavaScript (npm) |

**Framework detection:**

| Indicator | Framework |
|-----------|-----------|
| `next.config.js` | Next.js |
| `vite.config.ts` | Vite |
| `angular.json` | Angular |
| `vue.config.js` | Vue CLI |

## Package Manager Detection

```bash
[ -f package-lock.json ] && echo "npm"
[ -f yarn.lock ] && echo "yarn"
[ -f pnpm-lock.yaml ] && echo "pnpm"
[ -f bun.lockb ] && echo "bun"
```

## Pre-requisites

Before running compile test:

```bash
# Check node_modules
[ -d node_modules ] || echo "Run: npm install"

# Check TypeScript installation
[ -f node_modules/.bin/tsc ] || echo "Run: npm install typescript"
```

## Common tsconfig.json Options

Key options affecting compile behavior:

| Option | Description |
|--------|-------------|
| `strict` | Enable all strict checks |
| `noEmit` | Type check only |
| `skipLibCheck` | Skip .d.ts checking (faster) |
| `esModuleInterop` | CommonJS/ES module compatibility |
| `target` | Output JavaScript version |

## Lint (Optional)

### ESLint

```bash
# Check
npx eslint src/

# With TypeScript support
npx eslint --ext .ts,.tsx src/

# Fix auto-fixable issues (only if requested)
npx eslint --fix src/
```

### Config detection

- `.eslintrc.js` / `.eslintrc.json` / `.eslintrc.yml`
- `eslint.config.js` (flat config)
- `package.json` (`eslintConfig` field)

## Example Output

**TypeScript error:**

```
src/index.ts:15:7 - error TS2322: Type 'string' is not assignable to type 'number'.

15   const count: number = "hello";
         ~~~~~

Found 1 error in src/index.ts:15
```

**ESLint error:**

```
/src/index.js
  15:7  error  'unusedVar' is assigned a value but never used  no-unused-vars

1 problem (1 error, 0 warnings)
```

**Node syntax check:**

```
/src/index.js:15
    const x =
            ^
SyntaxError: Unexpected end of input
```
