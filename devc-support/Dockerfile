FROM node:18-alpine

# Install necessary tools
RUN apk add --no-cache \
    docker-cli \
    bash \
    sudo \
    acl \
    jq \
    shadow \
    python3

# Install devcontainers CLI
RUN npm install -g @devcontainers/cli

# Create a workspace directory
RUN mkdir -p /workspace && chmod 777 /workspace

# Copy scripts
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY devc-backend.py /usr/local/bin/devc-backend.py
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/devc-backend.py

WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]