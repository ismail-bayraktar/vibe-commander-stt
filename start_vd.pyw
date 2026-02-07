"""VD Speech-to-Text - terminal penceresi olmadan baslat."""
import runpy
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))
runpy.run_path("speech_to_text.py", run_name="__main__")
