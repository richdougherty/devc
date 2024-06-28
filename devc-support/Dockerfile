# Use a more recent Node.js version
FROM node:20-alpine

# Install necessary tools
RUN apk add --no-cache \
    docker-cli \
    bash \
    sudo \
    acl \
    jq \
    shadow \
    python3 \
    py3-pip

# Install devcontainers CLI
RUN npm install -g @devcontainers/cli

# Create necessary directories
RUN mkdir -p /workspace /opt/devc

# Copy devc backend files
COPY devc_backend.py /opt/devc/
COPY commands /opt/devc/commands
COPY utils /opt/devc/utils

# Make sure the scripts are executable
RUN chmod +x /opt/devc/devc_backend.py

# Copy entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Set up Python path
ENV PYTHONPATH="/opt/devc:$PYTHONPATH"

WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]