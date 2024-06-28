#!/usr/bin/env python3
#
# devc - Dev container helper
# https://github.com/richdougherty/devc
#
# Copyright (c) 2024 Rich Dougherty
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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