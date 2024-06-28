import sys
from . import env_utils

VERBOSE = env_utils.DEVC_VERBOSE

def verbose_log(message):
    if VERBOSE:
        print(f"VERBOSE: {message}", file=sys.stderr)