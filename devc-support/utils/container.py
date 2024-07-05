# devc-support/utils/container.py

import json
import subprocess
import sys
from . import assertions, logging, subprocess_utils, devcontainer_config, project_state

def get_container_status():
    container_id = project_state.get_state_value('container_id')
    if not container_id:
        logging.verbose_log("No cached container ID found")
        return {'status': 'down'}
    
    result = subprocess_utils.run_subprocess(['docker', 'ps', '-a', '-f', f'id={container_id}', '--format', 'json'], 
                            stdout=subprocess.PIPE, stderr=sys.stderr, check=True)

    logging.verbose_log(f'Got result from docker ps: {result.stdout.strip()}')
    if not result.stdout.strip():
        logging.verbose_log(f'Docker no longer running container')
        project_state.set_state_value('container_id', None)  # Clean up since it no longer exists
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
    devcontainer_config.ensure_devcontainer_files_exist()
    devcontainer_json_hash = project_state.get_state_value('devcontainer_json_hash')

    container_status = get_container_status()
    logging.verbose_log(f'Checking if up, got status: {container_status}')
    status_value = container_status['status']
    if status_value == 'up':
        container_devcontainer_json_hash = project_state.get_state_value('container_devcontainer_json_hash')
        logging.verbose_log(f"Container is running with devcontainer.json: {container_devcontainer_json_hash}")
        if devcontainer_json_hash != container_devcontainer_json_hash:
            # TODO: Ask interactively and also provide option to ignore and continue or to force restart
            print('Running container is out of date because devcontainer.json has changed. Run "down" to remove and try again.', file=sys.stderr)
            sys.exit(1)
    elif status_value == 'stopped':
        container_id = container_status['container_id']  # Get container_id from status
        container_devcontainer_json_hash = project_state.get_state_value('container_devcontainer_json_hash')
        logging.verbose_log(f'Container stopped, built from devcontainer.json: {container_devcontainer_json_hash}')
        if devcontainer_json_hash != container_devcontainer_json_hash:
            # TODO: Ask interactively and also provide option to ignore and continue or to force restart
            print('Container exists, but devcontainer.json has changed, run "down" to remove and try again', file=sys.stderr)
            sys.exit(1)
        subprocess_utils.run_subprocess(['docker', 'start', container_id], check=True)
    elif status_value == 'down':
        logging.verbose_log('Container is down, creating new container')
        result = subprocess_utils.run_subprocess(['devcontainer', 'up', '--workspace-folder', project_state.PROJECT_DIR], check=True, stdout=subprocess.PIPE, stderr=sys.stderr)
        result_json = json.loads(result.stdout)
        if result_json['outcome'] != 'success':
            print(f"Error running devcontainer up: {result_json}", file=sys.stderr)
            sys.exit(1)
        container_id = result_json['containerId']
        project_state.set_state_value('container_id', container_id)
        project_state.set_state_value('container_devcontainer_json_hash', devcontainer_json_hash)
        logging.verbose_log(f"Starting dev container from devcontainer.json: {devcontainer_json_hash}")

        logging.verbose_log(f"Dev container started: {container_id}")

def check_devcontainer_status():
    devc_generate_hash, devcontainer_json_hash = project_state.get_devcontainer_hashes()
    current_devc_generate_hash = devcontainer.get_devc_generate_hash()
    current_devcontainer_json_hash = devcontainer.get_devcontainer_json_hash()

    if current_devc_generate_hash != devc_generate_hash:
        print("devc-generate.yml has changed. Please run 'devc down' and then 'devc up' to apply changes.", file=sys.stderr)
        sys.exit(1)
    elif current_devcontainer_json_hash != devcontainer_json_hash:
        print("devcontainer.json has been modified outside of devc. Please review changes and run 'devc down' and then 'devc up' to apply changes.", file=sys.stderr)
        sys.exit(1)