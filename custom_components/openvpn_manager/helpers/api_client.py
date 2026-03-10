"""API Client for OpenVPN Manager Add-on."""
import logging
import aiohttp
import async_timeout
from typing import Dict, Any, Optional

_LOGGER = logging.getLogger(__name__)


class APIClient:
    """Client to communicate with OpenVPN Manager Add-on API."""

    def __init__(self, host: str, port: int, timeout: int = 30):
        """
        Initialize API client.

        Args:
            host: API host (e.g., localhost)
            port: API port (e.g., 9876)
            timeout: Request timeout in seconds
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}/api"
        _LOGGER.info(f"APIClient initialized for {self.base_url}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the add-on API is available.

        Returns:
            Dictionary with health status
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(self.timeout):
                    async with session.get(f"{self.base_url}/health") as response:
                        if response.status == 200:
                            data = await response.json()
                            _LOGGER.debug(f"Health check successful: {data}")
                            return data
                        else:
                            _LOGGER.warning(f"Health check failed with status {response.status}")
                            return {"success": False, "error": f"HTTP {response.status}"}
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Connection error during health check: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            _LOGGER.error(f"Unexpected error during health check: {e}")
            return {"success": False, "error": str(e)}

    async def get_status(self) -> Dict[str, Any]:
        """
        Get VPN status.

        Returns:
            Dictionary with VPN status
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(self.timeout):
                    async with session.get(f"{self.base_url}/status") as response:
                        if response.status == 200:
                            data = await response.json()
                            _LOGGER.debug(f"Status retrieved: {data}")
                            return data
                        else:
                            _LOGGER.warning(f"Status request failed with status {response.status}")
                            return {"success": False, "error": f"HTTP {response.status}"}
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Connection error getting status: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error getting status: {e}")
            raise

    async def start_vpn(self, config_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Start VPN connection.

        Args:
            config_name: Configuration file name (optional)

        Returns:
            Dictionary with result
        """
        try:
            payload = {}
            if config_name:
                payload['config_name'] = config_name

            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(self.timeout):
                    async with session.post(
                        f"{self.base_url}/start",
                        json=payload
                    ) as response:
                        data = await response.json()
                        _LOGGER.info(f"Start VPN response: {data}")
                        return data
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Connection error starting VPN: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error starting VPN: {e}")
            raise

    async def stop_vpn(self) -> Dict[str, Any]:
        """
        Stop VPN connection.

        Returns:
            Dictionary with result
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(self.timeout):
                    async with session.post(f"{self.base_url}/stop") as response:
                        data = await response.json()
                        _LOGGER.info(f"Stop VPN response: {data}")
                        return data
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Connection error stopping VPN: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error stopping VPN: {e}")
            raise

    async def upload_config(self, filename: str, content: bytes) -> Dict[str, Any]:
        """
        Upload OpenVPN configuration file.

        Args:
            filename: Name of the file
            content: File content as bytes

        Returns:
            Dictionary with result
        """
        try:
            data = aiohttp.FormData()
            data.add_field('file', content, filename=filename, content_type='text/plain')

            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(self.timeout):
                    async with session.post(
                        f"{self.base_url}/upload",
                        data=data
                    ) as response:
                        result = await response.json()
                        _LOGGER.info(f"Upload config response: {result}")
                        return result
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Connection error uploading config: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error uploading config: {e}")
            raise

    async def list_configs(self) -> Dict[str, Any]:
        """
        List available configuration files.

        Returns:
            Dictionary with config list
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(self.timeout):
                    async with session.get(f"{self.base_url}/configs") as response:
                        data = await response.json()
                        _LOGGER.debug(f"Config list retrieved: {data}")
                        return data
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Connection error listing configs: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error listing configs: {e}")
            raise

    async def delete_config(self, config_name: str) -> Dict[str, Any]:
        """
        Delete a configuration file.

        Args:
            config_name: Name of the configuration file

        Returns:
            Dictionary with result
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(self.timeout):
                    async with session.delete(
                        f"{self.base_url}/configs/{config_name}"
                    ) as response:
                        data = await response.json()
                        _LOGGER.info(f"Delete config response: {data}")
                        return data
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Connection error deleting config: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error deleting config: {e}")
            raise

    async def set_default_config(self, config_name: str) -> Dict[str, Any]:
        """
        Set default configuration file.

        Args:
            config_name: Name of the configuration file

        Returns:
            Dictionary with result
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(self.timeout):
                    async with session.post(
                        f"{self.base_url}/configs/{config_name}/default"
                    ) as response:
                        data = await response.json()
                        _LOGGER.info(f"Set default config response: {data}")
                        return data
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Connection error setting default config: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error setting default config: {e}")
            raise

    async def get_logs(self, lines: int = 50) -> Dict[str, Any]:
        """
        Get OpenVPN logs.

        Args:
            lines: Number of log lines to retrieve

        Returns:
            Dictionary with logs
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(self.timeout):
                    async with session.get(
                        f"{self.base_url}/logs",
                        params={'lines': lines}
                    ) as response:
                        data = await response.json()
                        _LOGGER.debug("Logs retrieved successfully")
                        return data
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Connection error getting logs: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error getting logs: {e}")
            raise

    async def get_info(self) -> Dict[str, Any]:
        """
        Get OpenVPN Manager information.

        Returns:
            Dictionary with info
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(self.timeout):
                    async with session.get(f"{self.base_url}/info") as response:
                        data = await response.json()
                        _LOGGER.debug(f"Info retrieved: {data}")
                        return data
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Connection error getting info: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"Unexpected error getting info: {e}")
            raise
