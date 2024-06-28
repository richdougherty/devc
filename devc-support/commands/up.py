from utils import logging, container, devcontainer_config

def add_parser(subparsers):
    parser = subparsers.add_parser("up", help="Create and start the dev container")
    parser.set_defaults(func=handle_up_command)

def handle_up_command(args):
    logging.verbose_log("Handling 'up' command")
    container.ensure_container_up()