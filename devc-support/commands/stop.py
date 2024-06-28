from utils import logging, container, subprocess_utils

def add_parser(subparsers):
    parser = subparsers.add_parser("stop", help="Stop the dev container")
    parser.set_defaults(func=handle_stop_command)

def handle_stop_command(args):
    logging.verbose_log("Handling 'stop' command")
    container_status = container.get_container_status()
    status_value = container_status['status']
    container_id = container_status.get('container_id')
    if status_value == 'up':
        logging.verbose_log(f"Container is running, stop it")
        subprocess_utils.run_subprocess(['docker', 'stop', container_id], check=True)
    elif status_value == 'stopped':
        logging.verbose_log('Container already stopped')
    elif status_value == 'down':
        logging.verbose_log('Container is down, nothing to stop')