import contextlib
import os
import pathlib
import shutil
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
