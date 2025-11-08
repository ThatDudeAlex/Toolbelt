import os
from pathlib import Path
import venv
import click
from toolbelt.utils import log, sh

PY_GITIGNORE = """# Byte-compiled / optimized / DLL files
.DS_Store
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Virtual environments
.venv/
venv/
ENV/

# Distribution / packaging
.build/
dist/
build/
.eggs/
*.egg-info/

# Testing / coverage
.coverage*
.pytest_cache/
.tox/

# IDEs/editors
.vscode/
.idea/

# Logs
*.log

# Environment
.env
.env.*
"""

NODE_GITIGNORE = """# dependencies
.DS_Store
node_modules/
.pnpm-store/
.bun/

# build outputs
dist/
build/
coverage/
.cache/
.next/
out/

# env and logs
.env
.env.*
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# editors
.vscode/
.idea/
"""

DEFAULT_REQS = [
    "black>=24.0.0",
    "isort>=5.12.0",
    "ruff>=0.5.0",
    "pytest>=7.0.0",
]

def write_if_absent(path: Path, content: str):
    if not path.exists():
        path.write_text(content, encoding="utf-8")

def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)

@click.group(help="Project bootstrappers")
def init():
    pass

@init.command("python", help="Create a new Python repo with venv, .gitignore, requirements, and initial commit.")
@click.option("--name", default=".", help="Project directory ('.' = current).", show_default=True)
@click.option("--empty-reqs", is_flag=True, help="Create empty requirements.txt (no default dev deps).")
def init_python(name: str, empty_reqs: bool):
    root = Path(name).resolve()
    ensure_dir(root)
    log.header("Bootstrap: Python project", str(root))

    try:
        sh.ensure_bin("git")
        if not (root / ".git").exists():
            log.info("Initializing git repo …")
            sh.run(["git", "init"], cwd=str(root))
    except Exception as e:
        log.warn(f"Git init skipped: {e}")

    write_if_absent(root / ".gitignore", PY_GITIGNORE)
    log.ok("Wrote .gitignore")

    venv_dir = root / ".venv"
    if not venv_dir.exists():
        log.info("Creating virtual environment (.venv) …")
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(venv_dir)
        log.ok("Virtual environment created")

    req_path = root / "requirements.txt"
    if empty_reqs:
        write_if_absent(req_path, "")
        log.info("Created empty requirements.txt")
    else:
        write_if_absent(req_path, "\n".join(DEFAULT_REQS) + "\n")
        log.info("requirements.txt created with common dev tools")
        pip_bin = venv_dir / ("Scripts/pip.exe" if os.name == "nt" else "bin/pip")
        log.info("Installing requirements …")
        sh.run([str(pip_bin), "install", "-r", str(req_path)])
        log.ok("Requirements installed")

    try:
        sh.run(["git", "add", "."], cwd=str(root))
        sh.run(["git", "commit", "-m", "Initialize Python project"], cwd=str(root), check=False)
        log.ok("Initial commit created")
    except Exception as e:
        log.warn(f"Git commit skipped: {e}")

    act = f"{venv_dir}/bin/activate"
    if os.name == "nt":
        act = f"{venv_dir}\\Scripts\\activate"
    log.ok("Done!")
    log.info("Activate your virtualenv with:")
    log.info(f"[dim]source {act}[/]" if os.name != "nt" else f"[dim]{act}[/]")

@init.command("npm", help="Create a new Node repo with npm init, .gitignore, and initial commit.")
@click.option("--name", default=".", help="Project directory ('.' = current).", show_default=True)
def init_npm(name: str):
    root = Path(name).resolve()
    ensure_dir(root)
    log.header("Bootstrap: Node project", str(root))

    try:
        sh.ensure_bin("git")
        if not (root / ".git").exists():
            log.info("Initializing git repo …")
            sh.run(["git", "init"], cwd=str(root))
    except Exception as e:
        log.warn(f"Git init skipped: {e}")

    try:
        if sh.which("npm"):
            log.info("Running npm init -y …")
            sh.run(["npm", "init", "-y"], cwd=str(root))
        elif sh.which("pnpm"):
            log.info("npm not found; using pnpm init …")
            sh.run(["pnpm", "init"], cwd=str(root))
        elif sh.which("yarn"):
            log.info("npm not found; using yarn init -y …")
            sh.run(["yarn", "init", "-y"], cwd=str(root))
        else:
            log.warn("No Node package manager found (npm/pnpm/yarn). Skipping init.")
    except Exception as e:
        log.err(str(e))
        raise SystemExit(1)

    write_if_absent(root / ".gitignore", NODE_GITIGNORE)
    log.ok("Wrote .gitignore")

    try:
        sh.run(["git", "add", "."], cwd=str(root))
        sh.run(["git", "commit", "-m", "Initialize Node project"], cwd=str(root), check=False)
        log.ok("Initial commit created")
    except Exception as e:
        log.warn(f"Git commit skipped: {e}")

    log.ok("Done!")
