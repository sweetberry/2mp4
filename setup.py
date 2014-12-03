import sys

from cx_Freeze import setup, Executable


includes = []

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="2mp4",
      version="0.9.0",
      options={"build_exe": {"packages": ["os"],
                             "includes": includes,
                             "include_files": ["libs/app.ico"],
                             'compressed': True}},
      executables=[Executable("2mp4.py", base=base, icon="libs/app.ico")])