#!/usr/bin/env python3

import argparse
import functools
import glob
import hashlib
import json
import os
import subprocess
import sys

DEVC_HOME = os.environ.get('DEVC_HOME')
PROJECT_DIR = os.environ.get('PROJECT_DIR')
DEVC_CACHE_DIR = os.path.join(DEVC_HOME, 'cache')
DEVC_PROJECT_CACHE_DIR = os.path.join(DEVC_CACHE_DIR, 'project')
VERBOSE = os.environ.get('DEVC_VERBOSE', 'false').lower() == 'true'

def verbose_log(message):
    if VERBOSE:
        print(f"VERBOSE: {message}", file=sys.stderr)

def unreachable():
    raise Exception('Unreachable code reached')

# Just subprocess.run with the command also logged
def run_subprocess(cmd, *args, **kwargs):
    verbose_log(f"Running command: {cmd}")
    return subprocess.run(cmd, *args, **kwargs)

@functools.cache # Memoize return value
def get_project_cache_dir():
    real_project_dir = os.path.realpath(PROJECT_DIR)
    dir_hash = hashlib.md5(real_project_dir.encode()).hexdigest()[:8]
    
    verbose_log(f"Searching for project directory with hash: {dir_hash}")
    
    matching_dirs = glob.glob(os.path.join(DEVC_PROJECT_CACHE_DIR, f"*-{dir_hash}"))
    
    for cache_dir in matching_dirs:
        project_dir_file = os.path.join(cache_dir, 'project_dir')
        if os.path.exists(project_dir_file):
            with open(project_dir_file, 'r') as f:
                if f.read().strip() == real_project_dir:
                    verbose_log(f"Found existing project directory: {cache_dir}")
                    return cache_dir

    base_name = os.path.basename(real_project_dir) # TODO: convert name into clean identifier; truncated
    project_cache_dir = os.path.join(DEVC_PROJECT_CACHE_DIR, f"{base_name}-{dir_hash}")
    os.makedirs(project_cache_dir, exist_ok=True)
    with open(os.path.join(project_cache_dir, 'project_dir'), 'w') as f:
        f.write(project_dir_file)
    
    verbose_log(f"Created new project cache directory: {project_cache_dir}")
    return project_cache_dir

def get_cached_containerid_file_path():
    project_cache_dir = get_project_cache_dir()
    container_id_file = os.path.join(project_cache_dir, 'container_id')
    return container_id_file

def put_cached_containerid(container_id):
    container_id_file = get_cached_containerid_file_path()
    with open(container_id_file, 'w') as f:
        f.write(container_id)

def get_cached_containerid():
    container_id_file = get_cached_containerid_file_path()
    if os.path.exists(container_id_file):
        with open(container_id_file, 'r') as f:
            return f.read().strip()
    return None

def remove_cached_containerid():
    container_id_file = get_cached_containerid_file_path()
    if os.path.exists(container_id_file):
          os.remove(container_id_file)

def get_container_status():
    container_id = get_cached_containerid()
    if not container_id:
        verbose_log("No cached container ID found")
        return {'status': 'down'}
    
    result = run_subprocess(['docker', 'ps', '-a', '-f', f'id={container_id}', '--format', 'json'], 
                            stdout=subprocess.PIPE, stderr=sys.stderr, check=True)

    if not result.stdout.strip():
        verbose_log(f'Docker no longer running container')
        remove_cached_containerid() # Clean up since it no longer exists
        return {'status': 'down'}
    
    result_json = json.loads(result.stdout)
    verbose_log(f'Got result: {result_json}')

    docker_state = result_json['State']
    verbose_log(f'Docker container state: {docker_state}')
    if docker_state == 'running':
        status = 'up'
    elif docker_state == 'exited':
        status = 'stopped'
    else:
        unreachable()

    return {'status': status, 'container_id': container_id}

def ensure_container_up():
    container_status = get_container_status()
    status_value = container_status['status']
    container_id = container_status.get('container_id')
    verbose_log(f'Checking if up, got status: {container_status}')
    if status_value == 'up':
        verbose_log(f"Container is already running, don't need to start")
    elif status_value == 'stopped':
        verbose_log('Container exists but is stopped, starting again')
        run_subprocess(['docker', 'start', container_id], check=True)
    elif status_value == 'down':
        verbose_log('Container is down, creating new container')
        result = run_subprocess(['devcontainer', 'up', '--workspace-folder', PROJECT_DIR], check=True, stdout=subprocess.PIPE, stderr=sys.stderr)
        result_json = json.loads(result.stdout)
        if result_json['outcome'] != 'success':
            print(f"Error running devcontainer up: {result_json}", file=sys.stderr)
            sys.exit(1)
        container_id = result_json['containerId']
        put_cached_containerid(container_id)
        verbose_log(f"Dev container started: {container_id}")
    else:
        unreachable()

def handle_up_command(common_args, subcommand_args):
    verbose_log("Handling 'up' command")
    ensure_container_up()

def handle_stop_command(common_args, subcommand_args):
    verbose_log("Handling 'stop' command")
    container_status = get_container_status()
    status_value = container_status['status']
    container_id = container_status.get('container_id')
    if status_value == 'up':
        verbose_log(f"Container is running, stop it")
        run_subprocess(['docker', 'stop', container_id], check=True)
    elif status_value == 'stopped':
        verbose_log('Container already stopped')
    elif status_value == 'down':
        verbose_log('Container is down, nothing to stop')
    else:
        unreachable()

def handle_down_command(common_args, subcommand_args):
    verbose_log("Handling 'down' command")
    container_status = get_container_status()
    status_value = container_status['status']
    if status_value == 'down':
        verbose_log('Container is down, nothing to do')
        return

    container_id = container_status.get('container_id')
    if status_value == 'up':
        verbose_log(f"Container is running, stop it")
        run_subprocess(['docker', 'stop', container_id], check=True, stdout=sys.stdout, stderr=sys.stderr)
    elif status_value == 'stopped':
        verbose_log('Container is already stopped')

    run_subprocess(['docker', 'rm', container_id], check=True, stdout=sys.stdout, stderr=sys.stderr)
    remove_cached_containerid()

def handle_exec_command(common_args, subcommand_args):
    verbose_log(f"Handling 'exec' command with args: {subcommand_args}")
    ensure_container_up()
    
    # Pass through stdin, stdout, stderr and return with return code
    completed = run_subprocess(['devcontainer', 'exec', '--workspace-folder', PROJECT_DIR] + subcommand_args, check=False, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    sys.exit(completed.returncode)

def handle_inspect_command(common_args, subcommand_args):
    verbose_log("Handling 'inspect' command")
    container_status = get_container_status()
    status_value = container_status['status']
    if status_value == 'down':
        print('No running dev container found.', out=sys.stderr)
        sys.exit(1)
    container_id = container_status['container_id']
    run_subprocess(['docker', 'inspect', container_id], check=True, stdout=sys.stdout, stderr=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Dev Container CLI wrapper")
    parser.add_argument('-v', '--verbose', action='store_true', help="Enable verbose logging")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=False)

    up_parser = subparsers.add_parser("up", help="Create and start the dev container")
    up_parser.set_defaults(command_func=handle_up_command)

    down_parser = subparsers.add_parser("down", help="Stop and remove the dev container and its image")
    down_parser.set_defaults(command_func=handle_down_command)

    stop_parser = subparsers.add_parser("stop", help="Stop and remove the dev container")
    stop_parser.add_argument("stop_args", nargs=argparse.REMAINDER, help="Additional arguments for 'stop' command")
    stop_parser.set_defaults(command_func=handle_stop_command)

    exec_parser = subparsers.add_parser("exec", help="Execute a command in the dev container")
    exec_parser.add_argument("exec_args", nargs=argparse.REMAINDER, help="Command to execute")
    exec_parser.set_defaults(command_func=handle_exec_command)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect the dev container")
    inspect_parser.add_argument("inspect_args", nargs=argparse.REMAINDER, help="Additional arguments for 'inspect' command")
    inspect_parser.set_defaults(command_func=handle_inspect_command)

    args, remaining = parser.parse_known_args()

    global VERBOSE
    VERBOSE = VERBOSE or args.verbose

    if hasattr(args, 'command_func'):
        common_args = argparse.Namespace(**{k: v for k, v in vars(args).items() if k not in ['command_func', 'command']})
        subcommand_args = getattr(args, f"{args.command}_args", [])
        exit_code = args.command_func(common_args, subcommand_args)
        sys.exit(exit_code if isinstance(exit_code, int) else 0)
    else:
        verbose_log("No command provided, starting bash shell")
        exit_code = handle_exec_command(args, ["bash"])
        sys.exit(exit_code)

if __name__ == "__main__":
    main()