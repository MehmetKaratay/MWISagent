# Pyproject Spec

This specification defines the project structure and Python dependencies configuration in a PEP 621 compliant `pyproject.toml` file.

```yaml
name: pyproject_spec
summary: Define Python packaging metadata, dependencies, and tool settings in pyproject.toml.
components:
  - name: project_metadata
    description: "Standard metadata including name, version, authors, description, and readme path."
  - name: runtime_dependencies
    description: "Dependencies required for production execution."
  - name: dev_dependencies
    description: "Development tools like pytest."
dependencies:
  - python >= 3.10
  - pyproj >= 3.7.1
  - parsedatetime >= 2.6
  - beautifulsoup4 >= 4.12.3
  - requests >= 2.31.0
  - pydantic >= 2.0.0
```

## Behavior & Technical Requirements

### 1. Project Metadata
The `pyproject.toml` must declare the following metadata fields under `[project]`:
* `name = "mwisagent"`
* `version = "0.1.0"`
* `description = "Mountain Weather Information Service agent MVP"`
* `readme = "README.md"`
* `requires-python = ">=3.10"`
* `authors` block specifying Mehmet Rahmi Karatay.

### 2. Runtime Dependencies
Define runtime dependencies in the `dependencies` list under `[project]`:
* `pyproj >= 3.7.1`
* `parsedatetime >= 2.6`
* `beautifulsoup4 >= 4.12.3`
* `requests >= 2.31.0`
* `pydantic >= 2.0.0`

### 3. Development Dependencies
Define dev dependencies under `[dependency-groups]` or `[project.optional-dependencies]` (using PEP 621 optional dependencies or standard PEP 735 dependency groups). Since `uv` supports dependency groups:
```toml
[dependency-groups]
dev = [
    "pytest>=7.0.0",
]
```

### 4. Build System Configuration
Declare standard build-backend for compatibility:
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Examples

Expected TOML structure:
```toml
[project]
name = "mwisagent"
version = "0.1.0"
dependencies = [
    "pyproj>=3.7.1",
    "parsedatetime>=2.6",
    "beautifulsoup4>=4.12.3",
    "requests>=2.31.0",
    "pydantic>=2.0.0"
]
```
