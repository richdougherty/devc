import os
import json
import sys
import yaml
from . import env_utils, logging

def ensure_devcontainer_files_exist():
    logging.verbose_log(f"Checking for devcontainer files")
    devcontainer_dir = os.path.join(env_utils.PROJECT_DIR, '.devcontainer')
    devcontainer_json_path = os.path.join(devcontainer_dir, 'devcontainer.json')
    devc_generate_yml_path = os.path.join(devcontainer_dir, 'devc-generate.yml')

    if os.path.exists(devcontainer_json_path) and not os.path.exists(devc_generate_yml_path):
        logging.verbose_log(f"devcontainer.json exists but devc-generate.yml not found. Skipping generation.")
        return

    # It is safe to generate because we either have:
    # - a devc-generate.yml file
    # - no files at all

    logging.verbose_log("Either found devc-generate.yml or missing a devcontainer.json, so will generate config.")

    if os.path.exists(devc_generate_yml_path):
        logging.verbose_log("Reading devc-generate.yml")
        with open(devc_generate_yml_path, 'r') as f:
            config = yaml.safe_load(f)
        logging.verbose_log(f"File contents: {config}")
    else:
        config = None # TODO: In the future might use different value for missing file since generation might be different
    generate_devcontainer_files(config)

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
