# devc - Dev Container helper

**Note: This project is in active development and may undergo significant changes.**

devc is a command-line tool designed to simplify the management of development containers. It provides an easy-to-use interface for creating, starting, stopping, and interacting with development containers based on the Dev Containers specification.

## Key Features

- Easy container management with simple commands
- Minimal dependencies - only Docker is required for installation and setup
- Automatic generation of devcontainer.json and Dockerfile based on project requirements
- Seamless integration with Docker
- Support for custom configurations via devc-generate.yml
- Compatible with various IDEs and development environments that support the Dev Containers specification

## Installation

To install devc, simply download the `devc` script and place it in your project directory:

```bash
curl -o devc https://raw.githubusercontent.com/richdougherty/devc/main/devc
chmod +x devc
```

## Usage

### Quick Start

The easiest way to get started is to simply run `./devc` in your project directory. This will spin up a container and give you a shell inside it:

```bash
./devc
```

### Basic Commands

- `./devc`: Start a shell in the dev container, automatically starting it if needed
- `./devc up`: Start the dev container, creating it if needed
- `./devc down`: Stop and remove the dev container and its image
- `./devc stop`: Stop the dev container, but keep it around
- `./devc exec <command>`: Execute a command in the dev container

### Options

- `-v` or `--verbose`: Enable verbose logging

## Configuration

You can customize your development container by creating a `devc-generate.yml` file in the `.devcontainer` directory of your project. This file allows you to specify:

- Base image
- Features to include (e.g., Python, Node.js)
- Custom name for your dev container

Example `devc-generate.yml`:

```yaml
name: my-project
image: mcr.microsoft.com/devcontainers/base:ubuntu
features:
  - python
  - node
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.