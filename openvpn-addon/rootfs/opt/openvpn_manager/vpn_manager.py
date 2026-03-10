"""OpenVPN Manager - Core VPN management logic."""
import os
import subprocess
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VPNManager:
    """Manages OpenVPN process lifecycle and status."""

    def __init__(self, config_dir: str = "/data/configs", log_dir: str = "/data/logs"):
        """
        Initialize VPN Manager.

        Args:
            config_dir: Directory containing .ovpn configuration files
            log_dir: Directory for storing logs
        """
        self.config_dir = config_dir
        self.log_dir = log_dir
        self.status_file = os.path.join(log_dir, "openvpn.status")
        self.log_file = os.path.join(log_dir, "openvpn.log")
        self.pid_file = os.path.join(log_dir, "openvpn.pid")
        self.current_config_file = os.path.join("/data", "current_config.txt")
        self.start_time_file = os.path.join("/data", "start_time.txt")

        # Ensure directories exist
        os.makedirs(config_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)

        logger.info(f"VPNManager initialized with config_dir={config_dir}, log_dir={log_dir}")

    def check_openvpn_installed(self) -> bool:
        """
        Check if OpenVPN is installed on the system.

        Returns:
            True if OpenVPN is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ['which', 'openvpn'],
                capture_output=True,
                timeout=5
            )
            installed = result.returncode == 0
            logger.info(f"OpenVPN installation check: {installed}")
            return installed
        except Exception as e:
            logger.error(f"Error checking OpenVPN installation: {e}")
            return False

    def get_openvpn_version(self) -> Optional[str]:
        """
        Get OpenVPN version.

        Returns:
            Version string or None if not available
        """
        try:
            result = subprocess.run(
                ['openvpn', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                # First line contains version
                version_line = result.stdout.split('\n')[0]
                logger.info(f"OpenVPN version: {version_line}")
                return version_line
            return None
        except Exception as e:
            logger.error(f"Error getting OpenVPN version: {e}")
            return None

    def start_vpn(self, config_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Start OpenVPN connection.

        Args:
            config_name: Name of .ovpn file to use (optional, uses default if not specified)

        Returns:
            Dictionary with success status and message
        """
        try:
            # Check if already running
            if self.is_vpn_running():
                logger.warning("VPN is already running")
                return {
                    "success": False,
                    "error": "VPN is already running. Stop it first."
                }

            # Determine config file to use
            if not config_name:
                config_name = self._get_default_config()

            if not config_name:
                logger.error("No configuration file specified and no default set")
                return {
                    "success": False,
                    "error": "No configuration file available. Please upload an .ovpn file first."
                }

            config_path = os.path.join(self.config_dir, config_name)

            if not os.path.exists(config_path):
                logger.error(f"Configuration file not found: {config_path}")
                return {
                    "success": False,
                    "error": f"Configuration file '{config_name}' not found"
                }

            # Start OpenVPN
            logger.info(f"Starting OpenVPN with config: {config_name}")
            cmd = [
                'openvpn',
                '--config', config_path,
                '--daemon',
                '--writepid', self.pid_file,
                '--status', f'{self.status_file} 5',
                '--log', self.log_file,
                '--script-security', '2'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                logger.error(f"Failed to start OpenVPN: {error_msg}")
                return {
                    "success": False,
                    "error": f"Failed to start OpenVPN: {error_msg}"
                }

            # Save current config and start time
            self._set_current_config(config_name)
            self._set_start_time()

            # Wait a moment for process to start
            time.sleep(1)

            # Verify it started
            if not self.is_vpn_running():
                logger.error("OpenVPN process did not start successfully")
                return {
                    "success": False,
                    "error": "OpenVPN process failed to start. Check logs for details."
                }

            logger.info("OpenVPN started successfully")
            return {
                "success": True,
                "message": "VPN started successfully",
                "config_name": config_name
            }

        except subprocess.TimeoutExpired:
            logger.error("OpenVPN start command timed out")
            return {
                "success": False,
                "error": "OpenVPN start command timed out"
            }
        except Exception as e:
            logger.error(f"Error starting VPN: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def stop_vpn(self) -> Dict[str, Any]:
        """
        Stop OpenVPN connection.

        Returns:
            Dictionary with success status and message
        """
        try:
            if not self.is_vpn_running():
                logger.info("VPN is not running")
                return {
                    "success": True,
                    "message": "VPN is not running"
                }

            pid = self._get_vpn_pid()

            if pid:
                logger.info(f"Stopping OpenVPN process (PID: {pid})")
                try:
                    subprocess.run(['kill', str(pid)], timeout=5, check=True)
                    time.sleep(1)

                    # Force kill if still running
                    if self.is_vpn_running():
                        logger.warning("OpenVPN did not stop gracefully, force killing")
                        subprocess.run(['kill', '-9', str(pid)], timeout=5)
                        time.sleep(0.5)

                except subprocess.SubprocessError as e:
                    logger.error(f"Error killing OpenVPN process: {e}")

            # Clean up files
            self._cleanup_files()

            logger.info("OpenVPN stopped successfully")
            return {
                "success": True,
                "message": "VPN stopped successfully"
            }

        except Exception as e:
            logger.error(f"Error stopping VPN: {e}")
            return {
                "success": False,
                "error": f"Error stopping VPN: {str(e)}"
            }

    def is_vpn_running(self) -> bool:
        """
        Check if OpenVPN process is currently running.

        Returns:
            True if running, False otherwise
        """
        pid = self._get_vpn_pid()
        if not pid:
            return False

        # Check if process exists
        try:
            subprocess.run(['kill', '-0', str(pid)], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive VPN status.

        Returns:
            Dictionary containing status information
        """
        is_running = self.is_vpn_running()

        status_dict = {
            "is_running": is_running,
            "status": "disconnected",
            "current_config": None,
            "wan_ip": None,
            "uptime": 0,
            "process_id": None
        }

        if is_running:
            status_dict["process_id"] = self._get_vpn_pid()
            status_dict["current_config"] = self._get_current_config()
            status_dict["uptime"] = self._calculate_uptime()

            # Check if tunnel is actually active
            if self._check_tunnel_active():
                status_dict["status"] = "connected"
                status_dict["wan_ip"] = self._get_wan_ip()
            else:
                status_dict["status"] = "connecting"

        logger.debug(f"VPN status: {status_dict}")
        return status_dict

    def get_vpn_logs(self, lines: int = 50) -> str:
        """
        Get recent OpenVPN logs.

        Args:
            lines: Number of lines to retrieve (default: 50)

        Returns:
            Log content as string
        """
        try:
            if not os.path.exists(self.log_file):
                return "No logs available"

            result = subprocess.run(
                ['tail', '-n', str(lines), self.log_file],
                capture_output=True,
                text=True,
                timeout=5
            )

            return result.stdout if result.returncode == 0 else "Error reading logs"

        except Exception as e:
            logger.error(f"Error reading logs: {e}")
            return f"Error reading logs: {str(e)}"

    def _get_vpn_pid(self) -> Optional[int]:
        """
        Get OpenVPN process ID.

        Returns:
            PID as integer or None if not found
        """
        # Try PID file first
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                    return pid
            except (ValueError, IOError) as e:
                logger.debug(f"Could not read PID file: {e}")

        # Fallback to pgrep
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'openvpn.*--config'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                pid = int(result.stdout.strip().split('\n')[0])
                return pid
        except (ValueError, subprocess.SubprocessError) as e:
            logger.debug(f"pgrep failed: {e}")

        return None

    def _check_tunnel_active(self) -> bool:
        """
        Check if VPN tunnel device is active.

        Returns:
            True if tunnel device exists and is up, False otherwise
        """
        try:
            # Check for tun0 or tap0 device
            result = subprocess.run(
                ['ip', 'link', 'show'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                output = result.stdout.lower()
                return 'tun' in output or 'tap' in output

            return False

        except Exception as e:
            logger.debug(f"Error checking tunnel device: {e}")
            return False

    def _get_wan_ip(self) -> Optional[str]:
        """
        Get current WAN IP address.

        Returns:
            IP address as string or None if unavailable
        """
        try:
            # Try multiple IP check services
            services = [
                'https://api.ipify.org',
                'https://ifconfig.me/ip',
                'https://icanhazip.com'
            ]

            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        ip = response.text.strip()
                        logger.debug(f"WAN IP: {ip}")
                        return ip
                except requests.RequestException:
                    continue

            return None

        except Exception as e:
            logger.debug(f"Error getting WAN IP: {e}")
            return None

    def _calculate_uptime(self) -> int:
        """
        Calculate VPN uptime in seconds.

        Returns:
            Uptime in seconds
        """
        try:
            if os.path.exists(self.start_time_file):
                with open(self.start_time_file, 'r') as f:
                    start_time_str = f.read().strip()
                    start_time = datetime.fromisoformat(start_time_str)
                    uptime = (datetime.now() - start_time).total_seconds()
                    return int(uptime)
        except Exception as e:
            logger.debug(f"Error calculating uptime: {e}")

        return 0

    def _get_default_config(self) -> Optional[str]:
        """
        Get default configuration filename.

        Returns:
            Configuration filename or None
        """
        # Check for saved default
        default_file = os.path.join("/data", "default_config.txt")
        if os.path.exists(default_file):
            try:
                with open(default_file, 'r') as f:
                    return f.read().strip()
            except IOError:
                pass

        # Fallback: use first available config
        try:
            configs = [f for f in os.listdir(self.config_dir) if f.endswith('.ovpn')]
            if configs:
                return configs[0]
        except OSError:
            pass

        return None

    def _set_current_config(self, config_name: str):
        """Save current configuration name."""
        try:
            with open(self.current_config_file, 'w') as f:
                f.write(config_name)
        except IOError as e:
            logger.warning(f"Could not save current config: {e}")

    def _get_current_config(self) -> Optional[str]:
        """Get current configuration name."""
        try:
            if os.path.exists(self.current_config_file):
                with open(self.current_config_file, 'r') as f:
                    return f.read().strip()
        except IOError:
            pass
        return None

    def _set_start_time(self):
        """Save VPN start time."""
        try:
            with open(self.start_time_file, 'w') as f:
                f.write(datetime.now().isoformat())
        except IOError as e:
            logger.warning(f"Could not save start time: {e}")

    def _cleanup_files(self):
        """Clean up temporary files."""
        files_to_remove = [
            self.pid_file,
            self.current_config_file,
            self.start_time_file,
            self.status_file
        ]

        for file_path in files_to_remove:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except OSError as e:
                logger.debug(f"Could not remove {file_path}: {e}")
