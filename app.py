import contextlib
import json
import logging
import os
import pathlib
import requests
import uuid
import shutil
import subprocess
import sys
import typing

PYTHON = "./venv/bin/python"
REQUIREMENTS_URL = 'https://raw.githubusercontent.com/faster-cpython/benchmarking-public/main/requirements.txt'
DATA = (pathlib.Path(os.getcwd()) / "data").resolve()
filepath = str | pathlib.Path

from flask import request, jsonify, Flask

app = Flask(__name__)

@app.route("/")
def home():
    params = ("target_fork","target_commit","base_commit","benchmarks","pgo","tier2","jit")
    vars = {}
    for p in params:
        vars[p] = request.args.get(p, None)

    if vars['base_commit']:
        return _benchmark(vars['base_commit'], benchmarks=vars['benchmarks'], pgo=vars['pgo'], tier2=vars['tier2'], jit=vars['jit'])
    else:
        return jsonify({"Result": "No commits specified"})
        
    

@app.route("/benchmark")
def benchmark():
    params = ("benchmarks","pgo","tier2","jit") # 'commit' is directly accessed so it 404s on failure
    vars = {}
    for p in params:
        vars[p] = request.args.get(p, None)

    result = _benchmark(request.args['commit'], benchmarks=vars['benchmarks'], pgo=vars['pgo'], tier2=vars['tier2'], jit=vars['jit'])
    
    return result

def _benchmark(commit, fork: str | None = None, benchmarks: str | None = None, pgo: bool | None = None, tier2: bool | None = None, jit: bool | None = None):
    args = {k: locals()[k] if k in locals() else None for k in ('fork', 'benchmarks', 'pgo', 'tier2', 'jit')}
    outfile = DATA / f"{commit[:12]}_{str(hash(json.dumps(args, sort_keys=True)))[12:]}.json"
    if not pathlib.Path(outfile).exists():
        with LongTemporaryDirectory() as tempdir:
            clone_commit(tempdir, repo=fork if fork else 'python/cpython', commit=commit)
            run_commands([
                f'cd {tempdir}',
                f"""./configure {'--enable-optimizations --with-lto=yes' if pgo else ''} {'--enable-experimental-jit' if jit else ''}""", 
                f'make -j{str(os.cpu_count()) if os.cpu_count() else "4"}',
                f'./python -m pip install pyperformance',
                #f'./python -m pyperf system tune' #requires passwordless sudo
            ])

            env = os.environ.copy()
            if tier2:
                env['PYTHON_UOPS'] = 1

            benchmarks = f"-b {benchmarks}" if benchmarks else ""
            
            run_commands([
                f'cd {tempdir}',
                f'./python -m pyperformance run --inherit-environ PYTHON_UOPS {benchmarks} -o {outfile}'
            ], env=env)
    
    with open(outfile, 'r') as f:
        return jsonify(f.read())

def clone_commit(dir: filepath, repo: str, commit: str) -> tuple[str, str]:
    return run_commands([
        f'cd {pathlib.Path(dir).resolve()}',
        'git init',
        f'git remote add origin https://github.com/{repo}.git',
        f'git fetch origin {commit} --depth 1',
        'git reset --hard FETCH_HEAD'
        ])
    
def make_virtual_env(dir: filepath) -> tuple[str, str]:
    return run_commands([
        f'cd {dir}',
        'python -m venv venv'
    ])

def get_github_file(url) -> str:
    page = requests.get(url)
    return page.text
    
def install_reqs(dir: filepath, *, url: str | None = None, text: str | None = None) -> tuple[str, str]:
    if bool(url) == bool(text):
        raise ValueError("Exactly one parameter of url and text must be supplied")
    return run_commands([
        f'cd {dir}',
        f'{PYTHON} -m pip install {f"-r {url}" if url else text}'
    ])

def run_commands(commands: typing.Iterable[str], *, envvars: dict = None, env = None) -> tuple[str, str]:
    print(f"Running commands {commands}")
    if not env:
        env = os.environ.copy()
    if envvars:
        for k, v in envvars.items():
            env[k] = v
    with subprocess.Popen('/bin/bash', text=True, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=sys.stdout, bufsize=1, universal_newlines=True, env = env) as p:
        return p.communicate('\n'.join(commands))

@contextlib.contextmanager
def LongTemporaryDirectory():
    tempdir = (pathlib.Path('/tmp') / str(uuid.uuid4())).resolve()
    os.mkdir(tempdir)
    try:
        yield tempdir
    finally:
        shutil.rmtree(tempdir)