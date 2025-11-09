import sys
import click
import importlib.util
from toolbelt.utils import log, sh


@click.group(help="Developer helpers")
def dev():
    pass


@dev.command(help="Run linters (ruff recommended).")
@click.option("--path", default=".", show_default=True)
@click.option("--fix", is_flag=True, help="Automatically fix issues.")
def lint(path: str, fix: bool):
    try:
        # Check if ruff is installed in the same environment
        if importlib.util.find_spec("ruff") is not None:
            log.info("Running ruff …")
            cmd = [sys.executable, "-m", "ruff", "check", path]
            if fix:
                cmd.append("--fix")
            sh.run(cmd)

        # Fallback: flake8 (if installed)
        elif importlib.util.find_spec("flake8") is not None:
            log.info("ruff not found; falling back to flake8 …")
            sh.run([sys.executable, "-m", "flake8", path])

        else:
            log.warn("No linter found (ruff/flake8). Make sure toolbelt is installed with its dependencies.")
            return

        log.ok("Lint completed")

    except sh.ShellError as e:
        # Print captured stdout/stderr if available
        if e.out:
            print(e.out, end="")
        if e.err:
            print(e.err, end="", file=sys.stderr)
        log.err(f"Command failed ({e.code}): {' '.join(e.cmd)}")
        raise SystemExit(1)


@dev.command(help="Auto-format code (black + isort if available).")
@click.option("--path", default=".", show_default=True)
@click.option("--check", is_flag=True,
help="Don’t modify files, just report which ones would be reformatted.",
)
@click.option("--verbose", is_flag=True,
    help="Show all files being processed.",
)
def format(path: str, check: bool, verbose: bool):
    """Format code using the built-in Black (and isort if installed)."""
    try:
        ran_any = False

        # --- Run Black (always available since it's a dependency) ---
        log.info("Running black …")
        cmd = [sys.executable, "-m", "black", path]
        if check:
            cmd.extend(["--check", "--diff"])
        if verbose:
            cmd.append("--verbose")
        sh.run(cmd)
        ran_any = True

        # --- Run isort if available (optional dependency) ---
        if importlib.util.find_spec("isort") is not None:
            log.info("Running isort …")
            cmd = [sys.executable, "-m", "isort", path]
            if check:
                cmd.extend(["--check-only", "--diff"])
            if verbose:
                cmd.append("--verbose")
            sh.run(cmd)
            ran_any = True

        if not ran_any:
            log.warn("No formatters found. Try installing optional dependency: isort")
            return

        log.ok("Formatting completed")

    except sh.ShellError as e:
        # Print captured output if formatting fails
        if e.out:
            print(e.out, end="")
        if e.err:
            print(e.err, end="", file=sys.stderr)
        log.err(f"Command failed ({e.code}): {' '.join(e.cmd)}")
        raise SystemExit(1)


@dev.command(help="Run tests (pytest if available, else unittest).")
@click.option("--path", default=".", show_default=True,
              help="Path to tests or project root.")
@click.option("--verbose", "-v", is_flag=True,
              help="Verbose pytest output (show all tests).")
@click.option("--fail-fast", "-x", is_flag=True,
              help="Stop after first failure (pytest --maxfail=1).")
@click.option("--nocapture", "-s", is_flag=True,
              help="Show print() output during tests (pytest -s).")
@click.option("--ci", is_flag=True,
    help="CI mode: fail fast, disable warnings, no color, short tracebacks.",
)
def test(path: str, verbose: bool, fail_fast: bool, nocapture: bool, ci: bool):
    """
    Run tests using pytest if available, otherwise fall back to unittest.
    """
    try:
        if sh.which("pytest"):
            log.info("Running pytest …")

            cmd = ["pytest", path]

            # Base traceback + color behavior
            if ci:
                # CI-friendly: minimal noise, deterministic output
                cmd.extend(["--maxfail=1", "--disable-warnings", "--color=no", "--tb=short"])
            else:
                cmd.extend(["--tb=short", "--color=yes"])

            # Verbosity: default quiet, unless verbose explicitly set
            if verbose:
                cmd.append("-v")
            else:
                cmd.append("-q")

            # Fail-fast flag (add if not already set by --ci)
            if fail_fast and "--maxfail=1" not in cmd:
                cmd.append("--maxfail=1")

            # Show print() output during tests
            if nocapture:
                cmd.append("-s")

            sh.run(cmd)

        else:
            log.info("pytest not found; running Python unittest discovery …")
            # Use the same interpreter for unittest
            sh.run([sys.executable, "-m", "unittest", "discover", "-s", path])

        log.ok("Tests completed")

    except sh.ShellError as e:
        # Show captured output from the failed test run
        if e.out:
            print(e.out, end="")
        if e.err:
            print(e.err, end="", file=sys.stderr)
        log.err(f"Command failed ({e.code}): {' '.join(e.cmd)}")
        raise SystemExit(1)
