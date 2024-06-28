import subprocess
from . import logging

def run_subprocess(cmd, *args, **kwargs):
    logging.verbose_log(f"Running command: {cmd}")
    return subprocess.run(cmd, *args, **kwargs)
