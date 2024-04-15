import contextlib
import json
import os
import pathlib
import shutil
import uuid

filepath = str | pathlib.Path
DATA = (pathlib.Path(os.getcwd()).parent / "data").resolve()


@contextlib.contextmanager
def LongTemporaryDirectory():
    tempdir = (pathlib.Path("/tmp") / str(uuid.uuid4())).resolve()
    os.mkdir(tempdir)
    try:
        yield tempdir
    finally:
        shutil.rmtree(tempdir)

def outfile_hash_name(commit, args):
    return f"{commit[:12]}_{str(hash(json.dumps(args, sort_keys=True)))[12:]}.json"

def get_outfile_path(commit, args):
    return DATA / outfile_hash_name(commit, args)

def get_python_version(dir: str | pathlib.Path):
    workdir = pathlib.Path(dir)
    maybe_python = workdir / "python"
    if (workdir / "python").exists() and True:
        #TODO Finish This
        pass

