import sys
from utils import logging, container, project_state, subprocess_utils

def add_parser(subparsers):
    parser = subparsers.add_parser("down", help="Stop and remove the dev container and its image")
    parser.set_defaults(func=handle_down_command)

def handle_down_command(args):
    logging.verbose_log("Handling 'down' command")
    container_status = container.get_container_status()
    status_value = container_status['status']
    if status_value == 'down':
        logging.verbose_log('Container is down, nothing to do')
        return

    container_id = container_status.get('container_id')
    if status_value == 'up':
        logging.verbose_log(f"Container is running, stop it")
        subprocess_utils.run_subprocess(['docker', 'stop', container_id], check=True, stdout=sys.stdout, stderr=sys.stderr)
    elif status_value == 'stopped':
        logging.verbose_log('Container is already stopped')

    subprocess_utils.run_subprocess(['docker', 'rm', container_id], check=True, stdout=sys.stdout, stderr=sys.stderr)
    project_state.set_state_value('container_id', None)