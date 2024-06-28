#!/usr/bin/env python3

import argparse
import sys
from commands import up, down, stop, exec, inspect
from utils import logging

def main():
    parser = argparse.ArgumentParser(description="Dev Container CLI wrapper")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose logging")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=False)

    up.add_parser(subparsers)
    down.add_parser(subparsers)
    stop.add_parser(subparsers)
    exec.add_parser(subparsers)
    inspect.add_parser(subparsers)

    args, remaining = parser.parse_known_args()

    logging.VERBOSE = logging.VERBOSE or args.verbose

    if hasattr(args, 'func'):
        exit_code = args.func(args)
        sys.exit(exit_code if isinstance(exit_code, int) else 0)
    else:
        logging.verbose_log("No command provided, starting bash shell")
        args.exec_args = ['bash']
        exit_code = exec.handle_exec_command(args)
        sys.exit(exit_code)

if __name__ == "__main__":
    main()