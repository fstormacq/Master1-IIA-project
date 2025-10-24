# Using uv on macOS and Windows

An extremely fast Python package and project manager, written in Rust. uv replaces tools like `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, and `virtualenv`, and supports macOS, Windows, and Linux.

- Official site and docs: https://docs.astral.sh/uv
- Benchmarks: [BENCHMARKS.md](https://github.com/astral-sh/uv/blob/main/BENCHMARKS.md)
- Project repo: https://github.com/astral-sh/uv

## Installation

Choose one method.

### macOS
```bash
# Standalone installer (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```bash
# Via PyPI (alternative)
pip install uv
# Or with pipx
pipx install uv
```

```bash
# Via Homebrew
brew install uv
```

### Windows
```powershell
# Standalone installer (recommended)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```powershell
# Via PyPI (alternative)
pip install uv
# Or with pipx
pipx install uv
```

After installing, restart your terminal if `uv` is not found.

### Verify installation
```bash
uv --version
```

### Update uv
If you used the standalone installer:
```bash
uv self update
```

For `pip`/`pipx` installs, update with the same tool you used.

## Quick start: Projects

Create and manage a project with lockfiles and isolated environments.

```bash
# Create a new project (creates a folder and pyproject.toml)
uv init example
cd example

# Add a dependency (will create .venv if needed)
uv add ruff

# Run a tool within the project environment
uv run ruff check

# Produce or refresh the lockfile
uv lock

# Sync your environment to the lockfile (fast installs)
uv sync
```

- More: https://docs.astral.sh/uv/guides/projects/

## Remove or uninstall packages

Choose the method that fits your workflow.

- Project dependency (remove from pyproject and lock, then apply):
  ```bash
  uv remove <package>
  uv sync
  ```
- Script dependency (remove inline dep from a script):
  ```bash
  uv remove --script example.py <package>
  ```
- Uninstall from the current environment only (pip-compatible):
  ```bash
  uv pip uninstall <package>
  ```
- Uninstall a tool installed via `uv tool install`:
  ```bash
  uv tool uninstall <package>
  ```

## Suppress or avoid the project environment

If you want to run something without using or modifying the project’s virtual environment:

- Run tools ephemerally (no changes to your project):
  ```bash
  uvx <tool> [args]          # alias for: uv tool run <tool> [args]
  ```
- Run commands outside the project directory to avoid project detection.
- Deactivate the venv to use your system interpreter:
  - macOS/Linux (bash/zsh): `deactivate`
  - Windows (PowerShell/CMD): `deactivate`
- If you no longer need the environment, you can remove it by deleting the `.venv` directory in your project. You can recreate it later with `uv sync`.

Tip: You can also run specific interpreters on-demand without activating a venv:
```bash
uv run --python 3.12 -- python --version
```

## Scripts (single-file workflows)

Let uv manage dependencies and an isolated env for a script.

```bash
# Create a script
echo 'import requests; print(requests.get("https://astral.sh"))' > example.py

# Declare script dependency inline
uv add --script example.py requests

# Run the script in an isolated virtual environment
uv run example.py
```

- More: https://docs.astral.sh/uv/guides/scripts/

## Tools (like pipx, but faster)

Run tools ephemerally or install them once to your PATH.

```bash
# Run a tool ephemerally
uvx pycowsay 'hello world!'

# Install a tool
uv tool install ruff

# Use it from your shell
ruff --version
```

- More: https://docs.astral.sh/uv/guides/tools/

## Manage Python versions

Install and select Python versions per project or command.

```bash
# Install multiple Python versions
uv python install 3.10 3.11 3.12

# Create a virtual environment with a specific version
uv venv --python 3.12.0

# Temporarily run with a specific interpreter
uv run --python pypy@3.8 -- python --version

# Pin a version for the current directory
uv python pin 3.11
```

- More: https://docs.astral.sh/uv/guides/install-python/

## Pip-compatible interface

Migrate existing workflows without changing commands much—uv provides drop-in replacements for common `pip`, `pip-tools`, and `virtualenv` operations, with 10–100x speedups.

```bash
# Compile a universal requirements file from an .in file
uv pip compile docs/requirements.in --universal --output-file docs/requirements.txt

# Create a virtual environment
uv venv

# Install from a locked requirements file
uv pip sync docs/requirements.txt
```

- More: https://docs.astral.sh/uv/pip/

## Virtual environment activation

uv prints an activation hint when creating a venv. If you need to activate manually:

- macOS (bash/zsh/fish):
  - Bash/Zsh: `source .venv/bin/activate`
  - Fish: `source .venv/bin/activate.fish`
- Windows:
  - PowerShell: `.venv\Scripts\Activate.ps1`
  - CMD: `.venv\Scripts\activate.bat`

You can also avoid manual activation by prefacing commands with `uv run ...`.

## Simple example 

This is a simple example of creating a project, adding a popular depandency and running a script inside the project environment.

1. Using uv

```bash
# Create a new project folder with pyproject.toml
uv init myproj
cd myproj

# Add numpy (auto-creates .venv if needed, updates pyproject.toml + uv.lock)
uv add numpy

# Run Python using the project environment (no manual activation needed)
uv run python -c "import numpy as np; print(np.__version__)"
```

2. Using pip (for comparison)

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# (optional) Upgrade pip
pip install --upgrade pip

# Install numpy
pip install numpy

# Pin current environment to requirements.txt (for sharing/reinstalling)
pip freeze > requirements.txt

# Later or elsewhere: recreate the environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run Python
python -c "import numpy as np; print(np.__version__)"
```

3. Using uv in a pip-compatible way with requirements.txt

```bash
# Create a requirements.txt
echo "numpy" > requirements.txt

# Create a venv (uv can also work with an existing .venv)
uv venv

# Install exactly what’s in requirements.txt (fast, parallel)
uv pip sync requirements.txt

# Run without manual activation
uv run python -c "import numpy as np; print(np.__version__)"
```

## Platform notes

- macOS: Works on Apple Silicon and Intel. If you used the standalone installer and `uv` isn’t found, open a new terminal so PATH changes take effect.
- Windows: Use PowerShell for the installer command. If `uv` isn’t found after install, open a new PowerShell or log out/in so PATH updates apply.

## Links

- Installation guide: https://docs.astral.sh/uv/getting-started/installation/
- Projects: https://docs.astral.sh/uv/guides/projects/
- Scripts: https://docs.astral.sh/uv/guides/scripts/
- Tools: https://docs.astral.sh/uv/guides/tools/
- Python versions: https://docs.astral.sh/uv/guides/install-python/
- Pip interface: https://docs.astral.sh/uv/pip/
- Platform support: https://docs.astral.sh/uv/reference/platforms/
- Versioning policy: https://docs.astral.sh/uv/reference/versioning/