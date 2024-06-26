#!/bin/bash

set -e

DEVC_DIR="$PROJECT_DIR/.devc"
CONTAINER_ID_FILE="$DEVC_DIR/containerid"

# Function for verbose logging
verbose_log() {
    if [ "$DEVC_VERBOSE" = "true" ]; then
        echo "VERBOSE: $1" >&2
    fi
}

verbose_log "Starting devcontainer-up script"
verbose_log "Project directory: $PROJECT_DIR"
verbose_log "DEVC directory: $DEVC_DIR"
verbose_log "Container ID file: $CONTAINER_ID_FILE"

mkdir -p "$DEVC_DIR"
verbose_log "Ensured DEVC directory exists"

# Capture the output of devcontainer up
verbose_log "Running 'devcontainer up' command"
output=$(devcontainer up "$@")
echo "$output"

verbose_log "Parsing JSON output"
# Check if the outcome was successful
outcome=$(echo "$output" | jq -r '.outcome // empty')
verbose_log "Outcome: $outcome"

if [ "$outcome" = "success" ]; then
    verbose_log "devcontainer up succeeded"
    # Extract the container ID from the JSON output using jq
    container_id=$(echo "$output" | jq -r '.containerId // empty')
    verbose_log "Extracted container ID: $container_id"

    if [ -n "$container_id" ]; then
        echo "$container_id" > "$CONTAINER_ID_FILE"
        verbose_log "Container ID saved to $CONTAINER_ID_FILE"
        echo "Container ID saved to $CONTAINER_ID_FILE"
    else
        echo "Error: Container ID not found in successful output" >&2
        verbose_log "Error: Container ID not found in successful output"
        exit 1
    fi
else
    echo "Error: devcontainer up did not succeed. Outcome: $outcome" >&2
    verbose_log "Error: devcontainer up did not succeed. Outcome: $outcome"
    exit 1
fi

verbose_log "devcontainer-up script completed successfully"