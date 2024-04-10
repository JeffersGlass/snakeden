import pathlib
import subprocess

from _fileutils import filepath
from _runner import run_commands


def clone_commit(dir: filepath, repo: str, commit: str | None) -> tuple[str, str]:
    if not commit:
        commit = "HEAD"
    return run_commands(
        [
            f"cd {pathlib.Path(dir).resolve()}",
            "git init",
            f"git remote add origin https://github.com/{repo}.git",
            f"git fetch origin {commit} --depth 1",
            "git reset --hard FETCH_HEAD",
        ]
    )


def get_git_revision_hash(dir: filepath) -> str:
    result = run_commands([
        f'cd {dir}',
        'git rev-parse HEAD',
        ],
        need_output=True)
    print(f"Git hash = {result}")
    return result[0]