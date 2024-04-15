import json
import os
import pathlib

from flask import jsonify

from _fileutils import LongTemporaryDirectory, outfile_hash_name
from _runner import run_commands
from _gitutils import clone_commit, get_git_revision_hash


DATA = (pathlib.Path(os.getcwd()).parent / "data").resolve()

def _benchmark(
    commit: str | None = None,
    fork: str | None = None,
    benchmarks: str | None = None,
    pgo: bool | None = None,
    tier2: bool | None = None,
    jit: bool | None = None,
    jsonify: bool = True
):
    args = {
        "fork" : fork,
        "benchmarks" : benchmarks,
        "pgo" : pgo,
        "tier2" : tier2,
        "jit" : jit
    }
    if commit:
        outfile = (
            DATA
            / outfile_hash_name(commit, args)
        )
    if not commit or not pathlib.Path(outfile).exists():
        with LongTemporaryDirectory() as tempdir:
            clone_commit(
                tempdir, repo=fork if fork else "python/cpython", commit=commit
            )
            if not commit:
                commit = get_git_revision_hash(tempdir)
                print(commit)
                outfile = DATA / outfile_hash_name(commit, args)
            run_commands(
                [
                    f"cd {tempdir}",
                    f"""./configure {'--enable-optimizations --with-lto=yes' if pgo else ''} {'--enable-experimental-jit' if jit else ''}""",
                    f'make -j4'#{str(os.cpu_count()) if os.cpu_count() else "4"}',
                    f"./python -m pip install pyperformance",
                    # f'./python -m pyperf system tune' #requires passwordless sudo
                ]
            )

            env = os.environ.copy()
            if tier2:
                env["PYTHON_UOPS"] = 1

            benchmarks = f"-b {benchmarks}" if benchmarks else ""

            run_commands(
                [
                    f"cd {tempdir}",
                    f"./python -m pyperformance run --inherit-environ PYTHON_UOPS {benchmarks} -o {outfile}",
                ],
                env=env,
                verbose = True
            )
    with open(outfile, "r") as f:
        if jsonify: return jsonify(f.read())
        else: return f.read()
