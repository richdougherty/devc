import argparse
import sys
from utils import logging, container, subprocess_utils

def add_parser(subparsers):
    parser = subparsers.add_parser("exec", help="Execute a command in the dev container")
    parser.add_argument("exec_args", nargs=argparse.REMAINDER, help="Command to execute")
    parser.set_defaults(func=handle_exec_command)

def handle_exec_command(args):
    logging.verbose_log(f"Handling 'exec' command with args: {args.exec_args}")
    container.ensure_container_up()
    
    completed = subprocess_utils.run_subprocess(['devcontainer', 'exec', '--workspace-folder', container.PROJECT_DIR] + args.exec_args, 
                                          check=False, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    return completed.returncode