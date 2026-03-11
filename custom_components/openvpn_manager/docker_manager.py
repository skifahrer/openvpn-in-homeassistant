"""Automatic Docker container management for OpenVPN Manager."""
import logging
import os
from typing import Optional, Dict, Any

try:
    import docker
    from docker.errors import DockerException, NotFound, APIError
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

_LOGGER = logging.getLogger(__name__)

CONTAINER_NAME = "openvpn-manager"
CONTAINER_IMAGE = "ghcr.io/skifahrer/openvpn-manager:latest"


class DockerManager:
    """Automatically manage OpenVPN Docker container."""

    def __init__(self, hass=None):
        """Initialize Docker manager."""
        self.client = None
        self._docker_available = DOCKER_AVAILABLE
        self.hass = hass

        if DOCKER_AVAILABLE:
            try:
                self.client = docker.from_env()
                self.client.ping()
                _LOGGER.info("Docker connection established")
            except Exception as e:
                _LOGGER.warning(f"Docker not available: {e}")
                self._docker_available = False

    def is_available(self) -> bool:
        """Check if Docker is available."""
        return self._docker_available and self.client is not None

    def get_data_path(self) -> str:
        """Get data path for volumes."""
        # Try to get HA config path
        if self.hass and hasattr(self.hass.config, 'config_dir'):
            return os.path.join(os.path.dirname(self.hass.config.config_dir), 'openvpn-manager')
        return "/opt/openvpn-manager"

    async def ensure_container_running(self) -> Dict[str, Any]:
        """Ensure container is running, start if needed."""
        if not self.is_available():
            return {"success": False, "error": "Docker not available on this system"}

        try:
            # Check if container exists and is running
            try:
                container = self.client.containers.get(CONTAINER_NAME)
                if container.status == "running":
                    _LOGGER.info("OpenVPN container already running")
                    return {"success": True, "status": "already_running"}
                else:
                    _LOGGER.info("Starting existing OpenVPN container")
                    container.start()
                    return {"success": True, "status": "started"}
            except NotFound:
                # Container doesn't exist, create it
                return await self._create_and_start_container()

        except Exception as e:
            _LOGGER.error(f"Error ensuring container: {e}")
            return {"success": False, "error": str(e)}

    async def _create_and_start_container(self) -> Dict[str, Any]:
        """Create and start the container."""
        try:
            _LOGGER.info("Creating OpenVPN Manager container")

            data_path = self.get_data_path()

            # Create data directories
            os.makedirs(f"{data_path}/configs", exist_ok=True)
            os.makedirs(f"{data_path}/logs", exist_ok=True)

            # Try to pull latest image first
            try:
                _LOGGER.info(f"Pulling image: {CONTAINER_IMAGE}")
                self.client.images.pull(CONTAINER_IMAGE)
            except Exception as e:
                _LOGGER.warning(f"Could not pull image, will use local: {e}")

            # Create container
            container = self.client.containers.run(
                image=CONTAINER_IMAGE,
                name=CONTAINER_NAME,
                detach=True,
                privileged=True,
                network_mode="host",
                cap_add=["NET_ADMIN", "NET_RAW"],
                devices=["/dev/net/tun:/dev/net/tun"],
                volumes={
                    f"{data_path}/configs": {"bind": "/data/configs", "mode": "rw"},
                    f"{data_path}/logs": {"bind": "/data/logs", "mode": "rw"},
                    f"{data_path}": {"bind": "/data", "mode": "rw"},
                },
                environment={
                    "API_PORT": "9876",
                    "LOG_LEVEL": "info",
                    "AUTO_START": "false",
                },
                ports={"9876/tcp": 9876},
                restart_policy={"Name": "unless-stopped"},
            )

            _LOGGER.info(f"Container created successfully: {container.id[:12]}")
            return {
                "success": True,
                "status": "created",
                "container_id": container.id[:12],
                "data_path": data_path,
            }

        except APIError as e:
            _LOGGER.error(f"Docker API error: {e}")
            return {"success": False, "error": f"Docker error: {str(e)}"}
        except Exception as e:
            _LOGGER.error(f"Error creating container: {e}")
            return {"success": False, "error": str(e)}

    def is_container_running(self) -> bool:
        """Check if container is running."""
        if not self.is_available():
            return False

        try:
            container = self.client.containers.get(CONTAINER_NAME)
            return container.status == "running"
        except NotFound:
            return False
        except Exception as e:
            _LOGGER.error(f"Error checking container: {e}")
            return False

    async def stop_container(self) -> Dict[str, Any]:
        """Stop the container."""
        if not self.is_available():
            return {"success": False, "error": "Docker not available"}

        try:
            container = self.client.containers.get(CONTAINER_NAME)
            container.stop(timeout=10)
            return {"success": True}
        except NotFound:
            return {"success": True, "message": "Container not found"}
        except Exception as e:
            _LOGGER.error(f"Error stopping container: {e}")
            return {"success": False, "error": str(e)}

    def get_container_logs(self, lines: int = 50) -> str:
        """Get container logs."""
        if not self.is_available():
            return "Docker not available"

        try:
            container = self.client.containers.get(CONTAINER_NAME)
            logs = container.logs(tail=lines, timestamps=False)
            return logs.decode('utf-8') if isinstance(logs, bytes) else str(logs)
        except Exception as e:
            return f"Error getting logs: {e}"
