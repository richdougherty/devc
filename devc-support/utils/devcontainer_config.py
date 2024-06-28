import os
import json
import sys
import yaml
import hashlib
from . import env_utils, logging, project_state

def ensure_devcontainer_files_exist():
    logging.verbose_log(f"Checking for devcontainer files")
    devcontainer_dir = os.path.join(env_utils.PROJECT_DIR, '.devcontainer')
    devcontainer_json_path = os.path.join(devcontainer_dir, 'devcontainer.json')
    devc_generate_yml_path = os.path.join(devcontainer_dir, 'devc-generate.yml')

    current_devc_generate_hash = get_devc_generate_hash()
    current_devcontainer_json_hash = get_devcontainer_json_hash()

    saved_devc_generate_hash = project_state.get_state_value('devc_generate_hash')
    saved_devcontainer_json_hash = project_state.get_state_value('devcontainer_json_hash')

    if current_devcontainer_json_hash is not None and current_devc_generate_hash is None:
        logging.verbose_log(f"devcontainer.json exists but devc-generate.yml not found. Skipping generation.")
        project_state.set_state_value('devc_generate_hash', None)
        project_state.set_state_value('devcontainer_json_hash', current_devcontainer_json_hash)
        return
    
    if current_devcontainer_json_hash is not None and current_devcontainer_json_hash != saved_devcontainer_json_hash:
        # TODO: Add force option to always rebuild
        print('devcontainer.json has changed since devc was last run, cannot generate. Remove file and retry.', file=sys.stderr)
        sys.exit(1)

    if current_devcontainer_json_hash is not None and current_devc_generate_hash == saved_devc_generate_hash:
        logging.verbose_log('devcontainer.json already exists and devc-generate.yml file has not changed, no need to regenerate')
        return

    logging.verbose_log("Need to generate devcontainer.json file")

    # Set to nonsense values first in case anything goes wrong, to force regeneration on re-run
    project_state.set_state_value('devc_generate_hash', 'generating')

    if os.path.exists(devc_generate_yml_path):
        logging.verbose_log("Reading devc-generate.yml")
        with open(devc_generate_yml_path, 'r') as f:
            config = yaml.safe_load(f)
        logging.verbose_log(f"File contents: {config}")
    else:
        config = None # TODO: In the future might use different value for missing file since generation might be different
    generate_devcontainer_files(config)

    new_devcontainer_json_hash = get_devcontainer_json_hash()
    project_state.set_state_value('devcontainer_json_hash', new_devcontainer_json_hash)
    project_state.set_state_value('devc_generate_hash', current_devc_generate_hash)

def generate_devcontainer_files(config):
    generate_devcontainer_json(config)
    generate_dockerfile(config)

def generate_devcontainer_json(config):
    devcontainer_json_path = os.path.join(env_utils.PROJECT_DIR, '.devcontainer', 'devcontainer.json')
    
    json_content = generate_json_content(config)
    
    with open_file_create_dir(devcontainer_json_path, 'w') as f:
        json.dump(json_content, f, indent=2)
    
    logging.verbose_log(f"Generated devcontainer.json: {devcontainer_json_path}")

def generate_json_content(config):
    project_name = os.path.basename(env_utils.PROJECT_DIR)
    
    if config is None: config = {} # A bit cleaner to work with
    json_content = {
        "name": config.get('name', project_name),
        "image": config.get('image', 'mcr.microsoft.com/devcontainers/base:ubuntu'),
    }
    
    if 'features' in config:
        features = {}
        for feature in config['features']:
            if feature == 'python':
                features["ghcr.io/devcontainers/features/python:1"] = {}
            elif feature == 'node':
                features["ghcr.io/devcontainers/features/node:1"] = {}
        
        if features:
            json_content["features"] = features
    
    return json_content

def generate_dockerfile(config):
    # Placeholder for Dockerfile generation
    logging.verbose_log("Dockerfile generation not implemented yet.")

def get_devc_generate_hash():
    return get_file_hash(os.path.join(project_state.PROJECT_DIR, '.devcontainer', 'devc-generate.yml'))

def get_devcontainer_json_hash():
    return get_file_hash(os.path.join(project_state.PROJECT_DIR, '.devcontainer', 'devcontainer.json'))

# File utils
# TODO: maybe move to shared util if useful

def open_file_create_dir(file_path, *open_args, **open_kwargs):
    """
    Open a file for reading or writing, creating the directory if it doesn't exist.
    
    :param file_path: Path to the file to open
    :param mode: Mode to open the file in (default is 'r' for read)
    :return: File object
    """
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        logging.verbose_log(f"Created directory: {dir_path}")
    return open(file_path, *open_args, **open_kwargs)

def get_file_hash(file_path):
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()