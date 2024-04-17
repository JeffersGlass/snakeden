import logging
import os
import pathlib
import shutil
import stat

from ._fileutils import LongTemporaryDirectory, get_outfile_path, _need_to_build_python, PYTHON_CACHE_PATH
from ._runner import run_commands
from ._gitutils import clone_commit, get_head_of_remote

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
        output, err = run_commands(['./venv/bin/python -m pyperformance list_groups --no-tags'], need_output=True)
        all = output.split("default")[0].split("\n")

        bmset = BenchmarkSet.fromList(bm.strip("- ") for bm in all if (bm and "all (" not in bm))
        logging.debug(f"{bmset._benchmarks=}")
        return bmset
    
def _benchmark(
    commit: str | None = None,
    fork: str  = "python/cpython",
    benchmarks: str | BenchmarkSet | None = None,
    pgo: bool | None = None,
    tier2: bool | None = None,
    jit: bool | None = None,
    jsonify: bool = True,
    use_cached_python = True,
    generate_cached_python = True,
    log_level = None
):  
    if log_level: logging.basicConfig(level=log_level)
    args = {
        "fork" : fork,
        "benchmarks" : benchmarks,
        "pgo" : pgo,
        "tier2" : tier2,
        "jit" : jit
    }
    
    logging.debug(f"Starting _benchmark with {commit=} and {args=}")
    if not commit:
        with LongTemporaryDirectory() as tempdir:
            out, err = get_head_of_remote(tempdir, repo = fork)
            commit = out.strip()
    
    outfile_path = get_outfile_path(commit, args)
    logging.debug(f"{outfile_path=}")


    if not pathlib.Path(outfile_path).exists():
        logging.debug("Outfile does not exit, will need to benchmark")
        with LongTemporaryDirectory() as tempdir:
            if use_cached_python and pathlib.Path.exists(py := PYTHON_CACHE_PATH / commit / "python"):
                logging.debug(f"Using existing python executable at {py}")
                py_executable = py
            else:
                logging.debug(f"Existing python not found, will have to build")
                _clone_and_build_python(tempdir, fork, commit, pgo, jit)
                py_executable = tempdir / "python"
                
                if generate_cached_python:
                    logging.debug(f"Caching newly-built python executable")
                    if not pathlib.Path(folder := PYTHON_CACHE_PATH / commit).exists():
                        logging.debug(f"Path {folder} does not exist and will be created")
                        os.mkdir(folder)
                    newpy = folder / "python"
                    if not pathlib.Path(folder / "python").exists():
                        shutil.copyfile(tempdir / "python", newpy)
                        st = os.stat(newpy)
                        logging.debug(f"Copied python permissions were {oct(st.st_mode)}")
                        os.chmod(newpy, st.st_mode |stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                        logging.debug(f"   New python permissions are  {oct(st.st_mode)}")
                    py_executable = newpy

            _benchmark_python(py_executable, tier2=tier2, benchmarks=benchmarks, outfile_path=outfile_path)

    with open(outfile_path, "r") as f:
        if jsonify: return jsonify(f.read())
        else: return f.read()

def _clone_and_build_python(dir, fork, commit, pgo, jit):
    clone_commit(
        dir, repo=fork, commit=commit
    )
    run_commands(
        [
            f"cd {dir}",
            f"""./configure {'--enable-optimizations --with-lto=yes' if pgo else ''} {'--enable-experimental-jit' if jit else ''}""",
            f'make -j4'#{str(os.cpu_count()) if os.cpu_count() else "4"}',
        ]
    )

def _benchmark_python(exe, *, tier2, benchmarks, outfile_path):
    env = os.environ.copy()
    if tier2:
        env["PYTHON_UOPS"] = 1

    benchmarks = f"-b {benchmarks}" if benchmarks else ""
    logging.debug(f"Benchmarking python with {outfile_path=}")

    run_commands(
        [
            f"{exe} -m pip install pyperformance",
            # f'./python -m pyperf system tune' #requires passwordless sudo
            f"{exe} -m pyperformance run --inherit-environ PYTHON_UOPS {benchmarks} -o {outfile_path}",
        ],
        env=env,
        verbose = True
    )