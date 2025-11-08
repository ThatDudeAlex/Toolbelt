import sys
import click
from toolbelt.utils import log, sh


@click.group(help="Developer helpers")
def dev():
    pass


@dev.command(help="Run linters (ruff recommended).")
@click.option("--path", default=".", show_default=True)
@click.option("--fix", is_flag=True, help="Automatically fix issues.")
def lint(path: str, fix: bool):
    try:
        if sh.which("ruff"):
            log.info("Running ruff …")
            cmd = ["ruff", "check", path]
            if fix:
                cmd.append("--fix")
            sh.run(cmd)
        elif sh.which("flake8"):
            log.info("ruff not found; falling back to flake8 …")
            sh.run(["flake8", path])
        else:
            log.warn("No linter found (ruff/flake8). Install ruff with: pipx install ruff")
            return
        log.ok("Lint completed")
    except sh.ShellError as e:
        # You can print the captured out/err from the exception too:
        if e.out:
            print(e.out, end="")
        if e.err:
            print(e.err, end="", file=sys.stderr)
        log.err(f"Command failed ({e.code}): {' '.join(e.cmd)}")
        raise SystemExit(1)


@dev.command(help="Auto-format code (black + isort if available).")
@click.option("--path", default=".", show_default=True)
@click.option("--check", is_flag=True, help="Don’t modify files, just report which ones would be reformatted")
@click.option("--verbose", is_flag=True, help="Show all files being processed")
def format(path: str, check: bool, verbose: bool):
    try:
        ran_any = False

        if sh.which("black"):
            log.info("Running black …")
            cmd = ["black", path]
            if check:
                cmd.extend(["--check", "--diff"])
            if verbose:
                cmd.append("--verbose")
            sh.run(cmd)
            ran_any = True

        if sh.which("isort"):
            log.info("Running isort …")
            cmd = ["isort", path]
            if check:
                cmd.extend(["--check-only", "--diff"])
            if verbose:
                cmd.append("--verbose")
            sh.run(cmd)
            ran_any = True

        if not ran_any:
            log.warn("Neither black nor isort found. Try: pipx install black isort")
            return

        log.ok("Formatting completed")

    except sh.ShellError as e:
        # Same pattern you used in lint
        if e.out:
            print(e.out, end="")
        if e.err:
            print(e.err, end="", file=sys.stderr)
        log.err(f"Command failed ({e.code}): {' '.join(e.cmd)}")
        raise SystemExit(1)


@dev.command(help="Run tests (pytest if available, else unittest).")
@click.option("--path", default=".", show_default=True)
def test(path: str):
    try:
        if sh.which("pytest"):
            log.info("Running pytest …")
            sh.run([
                "pytest",
                "-q",           # quiet summary
                "--tb=short",   # compact tracebacks
                "--color=yes",  # always color
                path,
            ])
        else:
            log.info("pytest not found; running Python unittest discovery …")
            sh.run(["python", "-m", "unittest", "discover", "-s", path])

        log.ok("Tests completed")

    except sh.ShellError as e:
        # Show captured output from the failed test run
        if e.out:
            print(e.out, end="")
        if e.err:
            print(e.err, end="", file=sys.stderr)
        log.err(f"Command failed ({e.code}): {' '.join(e.cmd)}")
        raise SystemExit(1)
