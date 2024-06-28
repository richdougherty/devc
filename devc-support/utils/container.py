import os
import functools
import hashlib
import glob
import json
import subprocess
import sys
from . import assertions, logging, subprocess_utils, devcontainer, env_utils

DEVC_HOME = env_utils.DEVC_HOME
PROJECT_DIR = env_utils.PROJECT_DIR

@functools.cache # Memoize return value
def get_project_cache_dir():
    real_project_dir = os.path.realpath(PROJECT_DIR)
    dir_hash = hashlib.md5(real_project_dir.encode()).hexdigest()[:8]
    
    logging.verbose_log(f"Searching for project directory with hash: {dir_hash}")
    
    devc_projects_cache_dir = os.path.join(DEVC_HOME, 'cache', 'project')
    matching_dirs = glob.glob(os.path.join(devc_projects_cache_dir, f"*-{dir_hash}"))
    
    for cache_dir in matching_dirs:
        project_dir_file = os.path.join(cache_dir, 'project_dir')
        if os.path.exists(project_dir_file):
            with open(project_dir_file, 'r') as f:
                if f.read().strip() == real_project_dir:
                    logging.verbose_log(f"Found existing project directory: {cache_dir}")
                    return cache_dir

    base_name = os.path.basename(real_project_dir) # TODO: convert name into clean identifier; truncated
    project_cache_dir = os.path.join(devc_projects_cache_dir, f"{base_name}-{dir_hash}")
    os.makedirs(project_cache_dir, exist_ok=True)
    with open(os.path.join(project_cache_dir, 'project_dir'), 'w') as f:
        f.write(project_dir_file)
    
    logging.verbose_log(f"Created new project cache directory: {project_cache_dir}")
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
        logging.verbose_log("No cached container ID found")
        return {'status': 'down'}
    
    result = subprocess_utils.run_subprocess(['docker', 'ps', '-a', '-f', f'id={container_id}', '--format', 'json'], 
                            stdout=subprocess.PIPE, stderr=sys.stderr, check=True)

    logging.verbose_log(f'Got result from docker ps: {result.stdout.strip()}')
    if not result.stdout.strip():
        logging.verbose_log(f'Docker no longer running container')
        remove_cached_containerid() # Clean up since it no longer exists
        return {'status': 'down'}
    
    result_json = json.loads(result.stdout)
    docker_state = result_json['State']
    logging.verbose_log(f'Docker container state: {docker_state}')
    if docker_state == 'running':
        return {'status': 'up', 'container_id': container_id}
    elif docker_state == 'exited':
        return {'status': 'stopped', 'container_id': container_id}
    else:
        assertions.unreachable()

def ensure_container_up():
    container_status = get_container_status()
    logging.verbose_log(f'Checking if up, got status: {container_status}')
    status_value = container_status['status']
    container_id = container_status.get('container_id')
    if status_value == 'up':
        logging.verbose_log(f"Container is already running, don't need to start")
    elif status_value == 'stopped':
        logging.verbose_log('Container exists but is stopped, starting again')
        subprocess_utils.run_subprocess(['docker', 'start', container_id], check=True)
    elif status_value == 'down':
        logging.verbose_log('Container is down, creating new container')
        devcontainer.ensure_devcontainer_files_exist()
        result = subprocess_utils.run_subprocess(['devcontainer', 'up', '--workspace-folder', PROJECT_DIR], check=True, stdout=subprocess.PIPE, stderr=sys.stderr)
        result_json = json.loads(result.stdout)
        if result_json['outcome'] != 'success':
            print(f"Error running devcontainer up: {result_json}", file=sys.stderr)
            sys.exit(1)
        container_id = result_json['containerId']
        put_cached_containerid(container_id)
        logging.verbose_log(f"Dev container started: {container_id}")