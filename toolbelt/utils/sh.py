import os
import shutil
import subprocess
from typing import Sequence, Mapping, Optional, Tuple


class ShellError(RuntimeError):
    def __init__(self, cmd: Sequence[str], code: int, out: str, err: str):
        super().__init__(f"Command failed ({code}): {' '.join(cmd)}\n{err}")
        self.cmd, self.code, self.out, self.err = cmd, code, out, err


def which(bin_name: str) -> Optional[str]:
    return shutil.which(bin_name)


def run(
    cmd: Sequence[str], cwd: Optional[str] = None, env: Optional[Mapping[str, str]] = None, check: bool = True
) -> Tuple[str, str]:
    p = subprocess.run(cmd, cwd=cwd, env=None if env is None else {**os.environ, **env}, text=True, capture_output=True)
    if check and p.returncode != 0:
        raise ShellError(cmd, p.returncode, p.stdout, p.stderr)
    return p.stdout.strip(), p.stderr.strip()


def ensure_bin(name: str):
    if which(name) is None:
        raise RuntimeError(f"Required executable '{name}' not found on PATH.")
