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

# Handle group
if getent group $LOCAL_GROUP_ID > /dev/null 2>&1; then
    GROUP_NAME=$(getent group $LOCAL_GROUP_ID | cut -d: -f1)
    verbose_log "Group with GID $LOCAL_GROUP_ID already exists: $GROUP_NAME"
else
    GROUP_NAME="devgroup$LOCAL_GROUP_ID"
    verbose_log "Creating group $GROUP_NAME with GID $LOCAL_GROUP_ID"
    groupadd -g $LOCAL_GROUP_ID $GROUP_NAME
fi

# Handle user
if id -u $LOCAL_USER_ID > /dev/null 2>&1; then
    USER_NAME=$(id -nu $LOCAL_USER_ID)
    OLD_PRIMARY_GID=$(id -g $USER_NAME)
    verbose_log "User with UID $LOCAL_USER_ID already exists: $USER_NAME"    
    
    # Add old primary group as secondary group if it's different
    if [ "$OLD_PRIMARY_GID" != "$LOCAL_GROUP_ID" ]; then
        verbose_log "Changing primary group of $LOCAL_USER_ID to $LOCAL_GROUP_ID"
        usermod -g $LOCAL_GROUP_ID $USER_NAME
        verbose_log "Adding additional group of old group $OLD_PRIMARY_GID to user $LOCAL_USER_ID"
        usermod -a -G $OLD_PRIMARY_GID $USER_NAME
    fi
else
    USER_NAME="devuser$LOCAL_USER_ID"
    verbose_log "Creating user $USER_NAME with UID $LOCAL_USER_ID"
    useradd -u $LOCAL_USER_ID -g $LOCAL_GROUP_ID -m -s /bin/bash $USER_NAME
fi

verbose_log "Ensuring correct ownership of user home and workspace"
# Ensure the user owns its home directory and the workspace
chown $USER_NAME:$LOCAL_GROUP_ID $HOME
chown $USER_NAME:$LOCAL_GROUP_ID /workspace

# Set ACL for Docker socket
verbose_log "Setting ACL for Docker socket"
sudo setfacl --modify user:$LOCAL_USER_ID:rw /var/run/docker.sock

verbose_log "Executing command as user: $*"
# Execute command as user
exec sudo -E -H -u $USER_NAME bash -c "$*"