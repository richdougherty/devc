import os
import yaml
import hashlib
import fcntl
import re
from . import env_utils, logging

DEVC_HOME = env_utils.DEVC_HOME
PROJECT_DIR = os.path.realpath(env_utils.PROJECT_DIR)

# Generate project ID
dir_hash = hashlib.md5(PROJECT_DIR.encode()).hexdigest()[:8]
base_name = os.path.basename(PROJECT_DIR)
sanitized_name = re.sub(r'[^a-z0-9]', '', base_name.lower())[:8]
PROJECT_ID = f"{sanitized_name}-{dir_hash}"
STATE_FILE = os.path.join(DEVC_HOME, 'project', PROJECT_ID, 'state.yml')
LOCK_FILE = f"{STATE_FILE}.lock"

class StateLockException(Exception):
    pass

def get_state_file_path():
    return STATE_FILE

def read_state():
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, 'w') as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except IOError:
            raise StateLockException(f"Unable to acquire read lock. Lock file: {LOCK_FILE}")
        
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                state = yaml.safe_load(f)
                if state.get('project_path') != PROJECT_DIR:
                    raise ValueError(f"Project path mismatch. Expected: {PROJECT_DIR}, Found: {state.get('project_path')}")
                return state
        return {'project_path': PROJECT_DIR}

def write_state(state):
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, 'w') as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            raise StateLockException(f"Unable to acquire write lock. Lock file: {LOCK_FILE}")
        
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            yaml.dump(state, f)

def get_state_value(key, default=None):
    state = read_state()
    value = state.get(key, default)
    logging.verbose_log(f'Read project state {key} value: {value}')
    return value

def set_state_value(key, value):
    state = read_state()
    state[key] = value
    logging.verbose_log(f'Writing project state {key} value: {value}')
    write_state(state)