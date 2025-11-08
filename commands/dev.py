import click
from utils import log, sh

@click.group(help="Developer helpers")
def dev():
    pass

@dev.command(help="Run linters (ruff recommended).")
@click.option("--path", default=".", show_default=True)
def lint(path: str):
    try:
        if sh.which("ruff"):
            log.info("Running ruff …")
            sh.run(["ruff", "check", path])
        elif sh.which("flake8"):
            log.info("ruff not found; falling back to flake8 …")
            sh.run(["flake8", path])
        else:
            log.warn("No linter found (ruff/flake8). Install ruff with: pipx install ruff")
            return
        log.ok("Lint completed")
    except Exception as e:
        log.err(str(e))
        raise SystemExit(1)

@dev.command(help="Auto-format code (black + isort if available).")
@click.option("--path", default=".", show_default=True)
def format(path: str):
    try:
        ran_any = False
        if sh.which("black"):
            log.info("Running black …")
            sh.run(["black", path])
            ran_any = True
        if sh.which("isort"):
            log.info("Running isort …")
            sh.run(["isort", path])
            ran_any = True
        if not ran_any:
            log.warn("Neither black nor isort found. Try: pipx install black isort")
            return
        log.ok("Formatting completed")
    except Exception as e:
        log.err(str(e))
        raise SystemExit(1)

@dev.command(help="Run tests (pytest if available, else unittest).")
@click.option("--path", default=".", show_default=True)
def test(path: str):
    try:
        if sh.which("pytest"):
            log.info("Running pytest …")
            sh.run(["pytest", "-q", path])
        else:
            log.info("pytest not found; running Python unittest discovery …")
            sh.run(["python", "-m", "unittest", "discover", "-s", path])
        log.ok("Tests completed")
    except Exception as e:
        log.err(str(e))
        raise SystemExit(1)
