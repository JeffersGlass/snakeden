import os
import pathlib
import stat
import shutil

shutil.copyfile((pathlib.Path(os.getcwd()).parent) / "venv" / "bin" / "python", (newpy:= "./python"))
st = os.stat(newpy)
os.chmod(newpy, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
py_executable = newpy