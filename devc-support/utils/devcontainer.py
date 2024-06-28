import os
import json
from . import env_utils, logging

def ensure_devcontainer_files_exist():
    logging.verbose_log(f"Checking for devcontainer files")
    devcontainer_dir = os.path.join(env_utils.PROJECT_DIR, '.devcontainer')
    dockerfile_path = os.path.join(devcontainer_dir, 'Dockerfile')
    devcontainer_json_path = os.path.join(devcontainer_dir, 'devcontainer.json')

    if not os.path.exists(devcontainer_dir):
        os.makedirs(devcontainer_dir)
        logging.verbose_log(f"Created .devcontainer directory: {devcontainer_dir}")

    if not os.path.exists(dockerfile_path):
        dockerfile_content = '''
FROM ubuntu:22.04
'''
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content.strip())
        logging.verbose_log(f"Created Dockerfile: {dockerfile_path}")

    if not os.path.exists(devcontainer_json_path):
        devcontainer_json_content = {
            "name": "Ubuntu Python Dev Container",
            "build": {
                "dockerfile": "Dockerfile"
            },
            "features": {
                "ghcr.io/devcontainers/features/python:1": {}
            },
            "customizations": {
                "vscode": {
                    "extensions": [
                        "ms-python.python",
                        "ms-python.vscode-pylance"
                    ]
                }
            }
        }
        with open(devcontainer_json_path, 'w') as f:
            json.dump(devcontainer_json_content, f, indent=2)
        logging.verbose_log(f"Created devcontainer.json: {devcontainer_json_path}")