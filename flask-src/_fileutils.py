import contextlib
import io
import json
import os
import pathlib
import shutil
import sys
import uuid

filepath = str | pathlib.Path


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
