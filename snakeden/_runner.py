import logging
import os
import requests
import subprocess
import sys
import typing

from ._fileutils import filepath

VENV_PYTHON = "./venv/bin/python"

STDOUT: typing.TypeAlias = str
STDERR: typing.TypeAlias = str
COMMUNICATE_OUTPUT = STDOUT, STDERR

def make_virtual_env(dir: filepath) -> None:
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

def run_commands(
    commands: typing.Iterable[str], *, envvars: dict = None, env=None, need_output=False, verbose=False
) -> tuple[STDOUT, STDERR]:
    newline = "\n\t"
    logging.debug(f"Running commands: {newline}{newline.join(commands)}")
    if not env:
        env = os.environ.copy()
    if envvars:
        for k, v in envvars.items():
            env[k] = v
    with subprocess.Popen(
        "/bin/bash",
        text=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE if need_output else (sys.stdout if verbose else subprocess.DEVNULL),
        stderr=subprocess.PIPE if need_output else (sys.stderr if verbose else subprocess.DEVNULL),
        bufsize=1,
        universal_newlines=True,
        env=env,
    ) as p:
        return p.communicate("\n".join(commands))
