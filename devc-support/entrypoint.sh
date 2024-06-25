#!/bin/bash

set -e

verbose_log() {
    if [ "$DEVC_VERBOSE" = "true" ]; then
        echo "VERBOSE: $1" >&2
    fi
}

# Check for required environment variables
if [ -z "$LOCAL_USER_ID" ]; then
    echo "Error: LOCAL_USER_ID is not set. This is required."
    exit 1
fi

if [ -z "$LOCAL_GROUP_ID" ]; then
    echo "Error: LOCAL_GROUP_ID is not set. This is required."
    exit 1
fi

verbose_log "Starting with UID : $LOCAL_USER_ID, GID : $LOCAL_GROUP_ID"

# Create or modify group
if getent group $LOCAL_GROUP_ID > /dev/null 2>&1; then
    verbose_log "Modifying existing group with GID $LOCAL_GROUP_ID"
    groupmod -g $LOCAL_GROUP_ID $(getent group $LOCAL_GROUP_ID | cut -d: -f1)
else
    verbose_log "Creating new group with GID $LOCAL_GROUP_ID"
    groupadd -g $LOCAL_GROUP_ID usergroup
fi

# Create or modify user
if id user > /dev/null 2>&1; then
    verbose_log "Modifying existing user with UID $LOCAL_USER_ID"
    usermod -u $LOCAL_USER_ID -g $LOCAL_GROUP_ID user
else
    verbose_log "Creating new user with UID $LOCAL_USER_ID"
    useradd --shell /bin/bash -u $LOCAL_USER_ID -g $LOCAL_GROUP_ID -o -c "" -m user
fi

export HOME=/home/user

verbose_log "Ensuring correct ownership of user home and workspace"
# Ensure the user owns its home directory and the workspace
chown user:$LOCAL_GROUP_ID $HOME
chown user:$LOCAL_GROUP_ID /workspace

# Set ACL for Docker socket
verbose_log "Setting ACL for Docker socket"
sudo setfacl --modify user:$LOCAL_USER_ID:rw /var/run/docker.sock

verbose_log "Executing command as user: $*"
# Execute command as user
exec sudo -E -H -u user bash -c "$*"