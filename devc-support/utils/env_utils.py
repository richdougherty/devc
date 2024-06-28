import os

def get_env_var(name, default=None):
    """
    Retrieve an environment variable.
    If the variable doesn't exist, return the default value if provided,
    otherwise raise a ValueError.
    """
    value = os.environ.get(name)
    if value is None:
        if default is not None:
            return default
        raise ValueError(f"Environment variable '{name}' is not set and no default value was provided.")
    return value

# Define constants for commonly used environment variables
DEVC_HOME = get_env_var('DEVC_HOME')
PROJECT_DIR = get_env_var('PROJECT_DIR')
DEVC_VERBOSE = get_env_var('DEVC_VERBOSE', 'false') == 'true'