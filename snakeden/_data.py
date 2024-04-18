from _runner import run_commands
from _commit import Commit

import json
import pathlib
import typing

class RunMetadata(typing.TypedDict):
    cpu_freq : str
    cpu_temp : str
    date : str
    duration : float
    load_avg_1min : float
    mem_max_rss : int
    uptime : float

WarmupList: typing.TypeAlias = list[tuple[int, float]]

class BenchmarkRun(typing.TypedDict):
    metatada: RunMetadata
    warmups: WarmupList
    values: typing.NotRequired[list[float]]

class BenchmarkInnerDict(typing.TypedDict):
    runs: list[BenchmarkRun]

class FileMetadata(typing.TypedDict):
    aslr : str
    boot_time : str
    command: typing.NotRequired[str]
    cpu_config : str
    cpu_count : int
    cpu_model_name : str
    description : str
    hostname : str
    loops : int
    name : str
    perf_version : str
    performance_version : str
    platform : str
    python_cflags : typing.NotRequired[str]
    python_compiler : typing.NotRequired[str]
    python_executable : typing.NotRequired[str]
    python_implementation : typing.NotRequired[str]
    python_version : typing.NotRequired[str]
    runnable_threads : typing.NotRequired[int]
    tags : list
    timer : typing.NotRequired[str]
    unit : str    

class BenchmarkFile(typing.TypedDict):
    benchmarks: list[BenchmarkInnerDict]
    metadata: FileMetadata
    version: str

class BuildOptions(typing.NamedTuple):
    commit: Commit
    jit: bool
    pgo: bool

def get_benchmark_build_options(data : BenchmarkFile) -> BuildOptions:
    commit = Commit(data['metadata']['python_version'].split(' ')[-1])
    flags = data['metadata']['python_cflags']
    jit = 'enable-experimental-jit' in flags
    pgo = '--enable-optimizations' in flags or '--with-lto=yes' in flags

    return BuildOptions(commit=commit, jit=jit, pgo=pgo)

def get_python_build_options(path: str | pathlib.Path) -> BuildOptions:
    path = pathlib.Path(path)
    python = (path / "python").resolve()

    out, err = run_commands([
                f'{python} -c $"import sysconfig\\nprint(sysconfig.get_config_vars())" '
            ],
        need_output=True)
    
    data: dict = json.loads(out.strip())
    commit = Commit(data['projectbase'].split("/")[-1])
    flags = data['CONFIG_ARGS']
    jit = '--enable-experimental-jit' in flags
    pgo = '--enable-optimizations' in flags and '--with-lto=yes' in flags

    return BuildOptions(commit=commit, jit=jit, pgo=pgo)





