# Python Compile Test

## Syntax Check

Basic syntax validation without execution:

```bash
# Single file
python -m py_compile path/to/file.py

# Multiple files
python -m py_compile file1.py file2.py file3.py

# All Python files in directory
find . -name "*.py" -exec python -m py_compile {} +
```

**Success**: No output, exit code 0

**Failure**: Shows file, line, and SyntaxError message

## Type Check (mypy)

Static type checking:

```bash
# Single file
mypy path/to/file.py

# Directory
mypy src/

# With config
mypy --config-file mypy.ini src/

# Strict mode
mypy --strict src/
```

**Common options:**

| Option | Description |
|--------|-------------|
| `--ignore-missing-imports` | Ignore untyped packages |
| `--no-error-summary` | Hide error count summary |
| `--show-error-codes` | Display error codes |
| `--python-version 3.10` | Target Python version |

**Config file detection:**

- `mypy.ini`
- `pyproject.toml` (under `[tool.mypy]`)
- `setup.cfg` (under `[mypy]`)

## Lint (Optional)

### ruff (recommended, fast)

```bash
# Check
ruff check path/to/file.py

# Check directory
ruff check src/

# Show fixable issues
ruff check --show-fixes src/
```

### pylint

```bash
# Single file
pylint path/to/file.py

# Directory
pylint src/

# Specific checks only
pylint --disable=all --enable=E src/  # Errors only
```

## Project Type Detection

| Indicator | Project Type |
|-----------|--------------|
| `pyproject.toml` | Modern Python (PEP 517/518) |
| `setup.py` | Traditional setuptools |
| `requirements.txt` | Pip-based |
| `Pipfile` | Pipenv |
| `poetry.lock` | Poetry |
| `conda.yaml` / `environment.yml` | Conda |

## Virtual Environment

Ensure correct environment before testing:

```bash
# Activate venv
source .venv/bin/activate  # or venv/bin/activate

# Activate conda
conda activate <env-name>

# Verify
which python
python --version
```

## Example Output

**Syntax error:**

```
  File "src/main.py", line 42
    print("hello"
          ^
SyntaxError: '(' was never closed
```

**Type error (mypy):**

```
src/main.py:42: error: Argument 1 to "process" has incompatible type "str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 3 source files)
```
