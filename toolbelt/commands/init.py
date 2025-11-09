import os
from pathlib import Path
import venv
import click
from toolbelt.utils import log, sh
from importlib import resources
import shutil


HERE = Path(__file__).resolve()
PROJECT_ROOT = HERE.parents[1]          # .../toolbelt
TEMPLATES_DIR = PROJECT_ROOT / "templates"

def template_path(*parts: str) -> Path:
    return TEMPLATES_DIR.joinpath(*parts)


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_precommit_config(project_root: Path):
    dst = project_root / ".pre-commit-config.yaml"
    src = template_path("python", ".pre-commit-config.yaml")
    copy_file(src, dst)


def copy_and_install_reqs(project_root: Path, venv_dir: Path, empty_reqs: bool):
    dst = project_root / "requirements.txt"
    if empty_reqs:
        dst.touch()
    else:
        src = template_path("python", "requirements.txt")
        copy_file(src, dst)
        log.info("requirements.txt created with common dev tools")

        pip_bin = venv_dir / ("Scripts/pip.exe" if os.name == "nt" else "bin/pip")
        log.info("Installing requirements …")

        sh.run([str(pip_bin), "install", "-r", str(dst)])
        log.ok("Requirements installed")


def copy_gitignore(project_root: Path):
    dst = project_root / ".gitignore"
    src = template_path(".gitignore")
    copy_file(src, dst)
    log.ok("Added .gitignore")


def write_if_absent(path: Path, content: str):
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def write_gitignore(project_root: Path) -> None:
    content = resources.files("toolbelt.templates").joinpath("gitignore-global").read_text()
    (project_root / ".gitignore").write_text(content)
    log.ok("Added .gitignore")


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


@click.group(help="Project bootstrappers")
def init():
    pass


@init.command("python", help="Create a new Python repo with venv, .gitignore, requirements, and initial commit.")
@click.option("--name", default=".", help="Project directory ('.' = current).", show_default=True)
@click.option("--empty-reqs", is_flag=True, help="Create empty requirements.txt (no default dev deps).")
def init_python(name: str, empty_reqs: bool):
    project_root = Path(name).resolve()
    ensure_dir(project_root)
    log.header("Bootstrap: Python project", str(project_root))

    try:
        sh.ensure_bin("git")
        if not (project_root / ".git").exists():
            log.info("Initializing git repo …")
            sh.run(["git", "init"], cwd=str(project_root))
    except Exception as e:
        log.warn(f"Git init skipped: {e}")

    write_gitignore(project_root)
    log.ok("Wrote .gitignore")

    venv_dir = project_root / "venv"
    if not venv_dir.exists():
        log.info("Creating virtual environment (venv) …")
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(venv_dir)
        log.ok("Virtual environment created")

    copy_requirements(project_root, venv_dir, empty_reqs)

    try:
        sh.run(["git", "add", "."], cwd=str(project_root))
        sh.run(["git", "commit", "-m", "Initialize Python project"], cwd=str(project_root), check=False)
        log.ok("Initial commit created")
    except Exception as e:
        log.warn(f"Git commit skipped: {e}")

    log.ok("Done!")

    log.info("Activate your virtual environment with:")
    if os.name == "nt":
        log.info("[dim]venv\\Scripts\\activate[/]")
    else:
        log.info("[dim]source venv/bin/activate[/]")



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

    write_gitignore(root)
    log.ok("Wrote .gitignore")

    try:
        sh.run(["git", "add", "."], cwd=str(root))
        sh.run(["git", "commit", "-m", "Initialize Node project"], cwd=str(root), check=False)
        log.ok("Initial commit created")
    except Exception as e:
        log.warn(f"Git commit skipped: {e}")

    log.ok("Done!")
