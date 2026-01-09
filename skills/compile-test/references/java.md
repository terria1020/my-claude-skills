# Java Compile Test

## Java Native (javac)

Direct compilation without build tools:

```bash
# Single file
javac path/to/File.java

# Multiple files
javac src/*.java

# With classpath
javac -cp lib/*:. src/Main.java

# With output directory
javac -d out/ src/Main.java

# Specific Java version
javac --release 17 src/Main.java
```

**Success**: No output, creates `.class` files

**Failure**: Shows file, line, and error message

## Maven Project

### Compile Only

```bash
# Standard compile
mvn compile

# Quiet mode (less output)
mvn compile -q

# Skip tests compilation
mvn compile -DskipTests

# Offline mode (air-gapped)
mvn compile -o
```

### Full Validation

```bash
# Compile + test compile
mvn test-compile

# Validate POM
mvn validate
```

**Success indicator**: `BUILD SUCCESS`

**Failure indicator**: `BUILD FAILURE` with error details

### Maven Wrapper

Prefer wrapper when available:

```bash
./mvnw compile
./mvnw compile -q
```

## Gradle Project

### Compile Only

```bash
# Java compile
./gradlew compileJava

# All compilation (includes test sources)
./gradlew classes

# Quiet mode
./gradlew compileJava -q

# Offline mode (air-gapped)
./gradlew compileJava --offline
```

### Kotlin DSL

Same commands work for `build.gradle.kts`:

```bash
./gradlew compileKotlin  # If Kotlin project
./gradlew compileJava    # Java sources
```

**Success indicator**: `BUILD SUCCESSFUL`

**Failure indicator**: Shows compilation errors with line numbers

### Gradle Wrapper

Always use wrapper when present:

```bash
# Unix/Linux/macOS
./gradlew compileJava

# Windows
gradlew.bat compileJava
```

## Project Type Detection

| File | Project Type |
|------|--------------|
| `pom.xml` | Maven |
| `build.gradle` | Gradle (Groovy DSL) |
| `build.gradle.kts` | Gradle (Kotlin DSL) |
| `*.java` only | Java Native |

**Check Java version requirement:**

```bash
# Maven (in pom.xml)
grep -A2 '<maven.compiler.source>' pom.xml

# Gradle (in build.gradle)
grep 'sourceCompatibility' build.gradle
```

## Common Options

### Maven

| Option | Description |
|--------|-------------|
| `-q` | Quiet, minimal output |
| `-o` | Offline mode |
| `-DskipTests` | Skip test compilation |
| `-pl <module>` | Compile specific module |
| `-am` | Also make dependencies |

### Gradle

| Option | Description |
|--------|-------------|
| `-q` | Quiet mode |
| `--offline` | Offline mode |
| `-x test` | Exclude test task |
| `-p <dir>` | Specify project dir |
| `--parallel` | Parallel execution |

## Example Output

**javac error:**

```
src/Main.java:15: error: ';' expected
    int x = 10
              ^
1 error
```

**Maven error:**

```
[ERROR] /src/main/java/App.java:[23,15] cannot find symbol
  symbol:   variable unknownVar
  location: class App
[INFO] BUILD FAILURE
```

**Gradle error:**

```
> Task :compileJava FAILED
/src/main/java/App.java:23: error: cannot find symbol
    System.out.println(unknownVar);
                       ^
  symbol:   variable unknownVar
BUILD FAILED
```
