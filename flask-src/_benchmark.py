import typing
import json
import os
import pathlib

from flask import jsonify

from _fileutils import LongTemporaryDirectory, outfile_hash_name
from _runner import run_commands
from _gitutils import clone_commit, get_git_revision_hash


DATA = (pathlib.Path(os.getcwd()).parent / "data").resolve()

_sentinel = object()

class BenchmarkSet():
    def __init__(self, benchmarks: list[str], obj: object,):
        if obj != _sentinel:
            raise ValueError("Use BenchmarkSet.fromString() or BenchmarkSet.fromList()")
        self._benchmarks = tuple(benchmarks)

    def __iter__(self):
        return (x for x in self._benchmarks)

    def __str__(self):
        return ','.join(self._benchmarks)

    @classmethod
    def fromString(cls, s):
        return cls([bm.strip() for bm in s.split(',')], _sentinel,)

    @classmethod
    def fromList(cls, l):
        return cls(list(l), _sentinel)

def get_all_benchmarks() -> BenchmarkSet:
        output, err = run_commands(['../venv/bin/python -m pyperformance list_groups --no-tags'], need_output=True)
        all = output.split("\\n\\n")[0].split("\n")

        return BenchmarkSet.fromList(bm.strip("- ") for bm in all)
    

def _benchmark(
    commit: str | None = None,
    fork: str | None = None,
    benchmarks: str | BenchmarkSet | None = None,
    pgo: bool | None = None,
    tier2: bool | None = None,
    jit: bool | None = None,
    jsonify: bool = True
):
    if benchmarks: bencharks = str(benchmarks)
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
