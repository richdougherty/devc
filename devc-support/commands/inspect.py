from utils import logging, container, subprocess_utils
import subprocess
import sys

def add_parser(subparsers):
    parser = subparsers.add_parser("inspect", help="Inspect the dev container")
    parser.set_defaults(func=handle_inspect_command)

def handle_inspect_command(args):
    logging.verbose_log("Handling 'inspect' command")
    container_status = container.get_container_status()
    status_value = container_status['status']
    if status_value == 'down':
        print('No running dev container found.', file=sys.stderr)
        return 1
    container_id = container_status['container_id']
    subprocess_utils.run_subprocess(['docker', 'inspect', container_id], check=True, stdout=sys.stdout, stderr=sys.stderr)