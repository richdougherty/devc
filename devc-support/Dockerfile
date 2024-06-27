FROM node:18-alpine

# Install necessary tools
RUN apk add --no-cache \
    docker-cli \
    bash \
    sudo \
    acl \
    jq \
    shadow

# Install devcontainers CLI
RUN npm install -g @devcontainers/cli

# Create a workspace directory
RUN mkdir -p /workspace && chmod 777 /workspace

# Copy and set permissions for entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY devcontainer-up.sh /usr/local/bin/devcontainer-up
RUN chmod +x /usr/local/bin/devcontainer-up

WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]