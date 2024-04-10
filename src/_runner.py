import os
import pathlib
import requests
import subprocess
import sys
import typing

from _fileutils import filepath

VENV_PYTHON = "./venv/bin/python"


def make_virtual_env(dir: filepath) -> tuple[str, str]:
    return run_commands([f"cd {dir}", "python -m venv venv"])


def get_github_file(url) -> str:
    page = requests.get(url)
    return page.text


def install_reqs(
    dir: filepath, *, url: str | None = None, text: str | None = None
) -> tuple[str, str]:
    if bool(url) == bool(text):
        raise ValueError("Exactly one parameter of url and text must be supplied")
    return run_commands(
        [f"cd {dir}", f'{VENV_PYTHON} -m pip install {f"-r {url}" if url else text}']
    )


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


def run_commands(
    commands: typing.Iterable[str], *, envvars: dict = None, env=None
) -> tuple[str, str]:
    print(f"Running commands {commands}")
    if not env:
        env = os.environ.copy()
    if envvars:
        for k, v in envvars.items():
            env[k] = v
    with subprocess.Popen(
        "/bin/bash",
        text=True,
        stdin=subprocess.PIPE,
        stdout=sys.stdout,
        stderr=sys.stdout,
        bufsize=1,
        universal_newlines=True,
        env=env,
    ) as p:
        return p.communicate("\n".join(commands))
