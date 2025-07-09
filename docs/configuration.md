# Configuration File

DevEnvOps uses `src/config/docker_environments.json` to store the configuration of all your development environments. This file is automatically managed by the DevEnvOps GUI, but advanced users can also modify it directly.

## Structure of `docker_environments.json`

The `docker_environments.json` file is a JSON object where each key represents a unique identifier for an environment, and its value is a dictionary containing the environment's details.

```json
{
  "cpp": {
    "name": "C++ Development",
    "path": "docker/cpp",
    "port": 3001,
    "container": "cpp.workspace.common",
    "image": "cpp.workspace.image",
    "volume": "cpp.workspace.common.volume"
  },
  "python-cuda": {
    "name": "Python CUDA Workspace",
    "path": "workspaces/python.cuda.template",
    "port": 3004,
    "container": "python.cuda.workspace",
    "image": "python.cuda.workspace.image",
    "volume": "python_cuda_workspace_volume:/workspace",
    "type": "docker-compose",
    "base_image": "nvidia/cuda:12.9.0-cudnn-devel-ubuntu24.04",
    "description": "Python + CUDA development with web interface support",
    "gpu_support": true,
    "web_port": 7860
  }
}
```

## Editable Fields

Each environment entry can have the following fields:

*   `name`: (String) The human-readable display name for the environment shown in the GUI and console.
*   `path`: (String) The relative path to the directory containing the Docker Compose (`docker-compose.yaml`) or Vagrant (`Vagrantfile`) configuration files for this environment. This path is relative to the project root.
*   `port`: (Integer) The SSH port used to access the environment. This port must be unique across all environments.
*   `container`: (String) The name of the Docker container (for Docker Compose environments) or the Vagrant VM name (for Vagrant environments).
*   `image`: (String) The name of the Docker image associated with the environment.
*   `volume`: (String) The Docker volume mapping (e.g., `my_volume:/workspace`).
*   `type`: (String, Optional) The type of environment. Can be `docker-compose` or `vagrant`. Defaults to `docker-compose`.
*   `base_image`: (String, Optional) The base image used in the Dockerfile for this environment.
*   `description`: (String, Optional) A brief description of the environment.
*   `gpu_support`: (Boolean, Optional) Indicates if the environment has GPU support.
*   `web_port`: (Integer, Optional) A web interface port, if applicable.
*   `ssh_user`: (String, Optional) The SSH username for Vagrant environments. Defaults to `dev`.
*   `ssh_password`: (String, Optional) The SSH password for Vagrant environments. Defaults to `devpass`.
*   `ssh_key`: (String, Optional) The path to an SSH key for Vagrant environments.
*   `vnc_port`: (Integer, Optional) A VNC port for Vagrant environments.

## Important Notes

*   **Path:** The `path` field is crucial. It points to the actual directory containing the `Dockerfile`, `docker-compose.yaml`, or `Vagrantfile`.
*   **Port Uniqueness:** Ensure that the `port` field is unique for each environment to avoid conflicts.
*   **Manual Edits:** If you manually edit `src/config/docker_environments.json`, ensure the JSON syntax is correct. Incorrect syntax can prevent the DevEnvOps GUI from loading environments.
*   **Default Environments:** If `docker_environments.json` is not found or is invalid, DevEnvOps will load a set of default environments (which are hardcoded in `src/core/docker_manager.py`).
