"""OpenVPN Manager - Configuration file handler."""
import os
import re
import logging
from typing import Dict, List, Optional, Any
from werkzeug.utils import secure_filename

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConfigHandler:
    """Handles OpenVPN configuration file management."""

    MAX_FILE_SIZE = 1024 * 1024  # 1MB
    REQUIRED_DIRECTIVES = ['remote']

    def __init__(self, config_dir: str = "/data/configs"):
        """
        Initialize configuration handler.

        Args:
            config_dir: Directory for storing configuration files
        """
        self.config_dir = config_dir
        self.default_config_file = os.path.join("/data", "default_config.txt")

        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)

        logger.info(f"ConfigHandler initialized with config_dir={config_dir}")

    def upload_config(self, filename: str, content: bytes) -> Dict[str, Any]:
        """
        Upload and validate an OpenVPN configuration file.

        Args:
            filename: Name of the configuration file
            content: File content as bytes

        Returns:
            Dictionary with success status and message
        """
        try:
            # Secure the filename
            safe_filename = secure_filename(filename)

            if not safe_filename:
                logger.error("Invalid filename provided")
                return {
                    "success": False,
                    "error": "Invalid filename"
                }

            # Check file extension
            if not safe_filename.endswith('.ovpn'):
                logger.error(f"Invalid file extension: {safe_filename}")
                return {
                    "success": False,
                    "error": "File must have .ovpn extension"
                }

            # Check file size
            if len(content) > self.MAX_FILE_SIZE:
                logger.error(f"File too large: {len(content)} bytes")
                return {
                    "success": False,
                    "error": f"File size exceeds maximum of {self.MAX_FILE_SIZE} bytes"
                }

            # Check if content is empty
            if len(content) == 0:
                logger.error("Empty file content")
                return {
                    "success": False,
                    "error": "File content is empty"
                }

            # Validate content
            try:
                config_text = content.decode('utf-8')
            except UnicodeDecodeError:
                logger.error("File is not valid UTF-8")
                return {
                    "success": False,
                    "error": "File must be valid UTF-8 text"
                }

            validation_result = self.validate_config_content(config_text)
            if not validation_result["valid"]:
                logger.error(f"Invalid configuration: {validation_result['error']}")
                return {
                    "success": False,
                    "error": f"Invalid configuration: {validation_result['error']}"
                }

            # Save the file
            file_path = os.path.join(self.config_dir, safe_filename)

            try:
                with open(file_path, 'wb') as f:
                    f.write(content)

                # Set restrictive permissions (owner read/write only)
                os.chmod(file_path, 0o600)

                logger.info(f"Configuration file saved: {safe_filename}")

                # Set as default if it's the first config
                configs = self.list_configs()
                if len(configs) == 1:
                    self.set_default_config(safe_filename)
                    logger.info(f"Set {safe_filename} as default configuration")

                return {
                    "success": True,
                    "message": "Configuration uploaded successfully",
                    "config_name": safe_filename
                }

            except IOError as e:
                logger.error(f"Error writing file: {e}")
                return {
                    "success": False,
                    "error": f"Error saving file: {str(e)}"
                }

        except Exception as e:
            logger.error(f"Unexpected error uploading config: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def validate_config_content(self, content: str) -> Dict[str, Any]:
        """
        Validate OpenVPN configuration file content.

        Args:
            content: Configuration file content as string

        Returns:
            Dictionary with valid status and error message if invalid
        """
        try:
            lines = content.split('\n')

            # Check for required directives
            found_directives = set()

            for line in lines:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#') or line.startswith(';'):
                    continue

                # Extract directive (first word)
                parts = line.split()
                if parts:
                    directive = parts[0].lower()
                    found_directives.add(directive)

            # Check for required directives
            missing = []
            for required in self.REQUIRED_DIRECTIVES:
                if required not in found_directives:
                    missing.append(required)

            if missing:
                return {
                    "valid": False,
                    "error": f"Missing required directives: {', '.join(missing)}"
                }

            # Check for common issues
            if 'remote' in found_directives:
                # Find remote line and validate format
                for line in lines:
                    line = line.strip()
                    if line.startswith('remote '):
                        parts = line.split()
                        if len(parts) < 2:
                            return {
                                "valid": False,
                                "error": "Invalid 'remote' directive format"
                            }

            logger.debug("Configuration validation passed")
            return {
                "valid": True,
                "message": "Configuration is valid"
            }

        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }

    def list_configs(self) -> List[str]:
        """
        List all available configuration files.

        Returns:
            List of configuration filenames
        """
        try:
            if not os.path.exists(self.config_dir):
                return []

            configs = [
                f for f in os.listdir(self.config_dir)
                if f.endswith('.ovpn') and os.path.isfile(os.path.join(self.config_dir, f))
            ]

            logger.debug(f"Found {len(configs)} configuration files")
            return sorted(configs)

        except OSError as e:
            logger.error(f"Error listing configurations: {e}")
            return []

    def get_config_path(self, config_name: str) -> Optional[str]:
        """
        Get full path to a configuration file.

        Args:
            config_name: Name of the configuration file

        Returns:
            Full path to config file or None if not found
        """
        safe_name = secure_filename(config_name)
        file_path = os.path.join(self.config_dir, safe_name)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            return file_path

        return None

    def delete_config(self, config_name: str) -> Dict[str, Any]:
        """
        Delete a configuration file.

        Args:
            config_name: Name of the configuration file to delete

        Returns:
            Dictionary with success status and message
        """
        try:
            safe_name = secure_filename(config_name)
            file_path = os.path.join(self.config_dir, safe_name)

            if not os.path.exists(file_path):
                logger.warning(f"Configuration file not found: {safe_name}")
                return {
                    "success": False,
                    "error": "Configuration file not found"
                }

            os.remove(file_path)
            logger.info(f"Configuration file deleted: {safe_name}")

            # If this was the default, clear default
            if self.get_default_config() == safe_name:
                try:
                    os.remove(self.default_config_file)
                except OSError:
                    pass

                # Set new default if other configs exist
                remaining_configs = self.list_configs()
                if remaining_configs:
                    self.set_default_config(remaining_configs[0])

            return {
                "success": True,
                "message": "Configuration deleted successfully"
            }

        except OSError as e:
            logger.error(f"Error deleting configuration: {e}")
            return {
                "success": False,
                "error": f"Error deleting file: {str(e)}"
            }

    def set_default_config(self, config_name: str) -> bool:
        """
        Set default configuration file.

        Args:
            config_name: Name of the configuration file

        Returns:
            True if successful, False otherwise
        """
        try:
            safe_name = secure_filename(config_name)
            file_path = os.path.join(self.config_dir, safe_name)

            if not os.path.exists(file_path):
                logger.error(f"Cannot set default: config not found: {safe_name}")
                return False

            with open(self.default_config_file, 'w') as f:
                f.write(safe_name)

            logger.info(f"Default configuration set to: {safe_name}")
            return True

        except IOError as e:
            logger.error(f"Error setting default configuration: {e}")
            return False

    def get_default_config(self) -> Optional[str]:
        """
        Get default configuration filename.

        Returns:
            Configuration filename or None
        """
        try:
            if os.path.exists(self.default_config_file):
                with open(self.default_config_file, 'r') as f:
                    config_name = f.read().strip()
                    # Verify file still exists
                    if self.get_config_path(config_name):
                        return config_name
        except IOError:
            pass

        return None

    def get_config_info(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a configuration file.

        Args:
            config_name: Name of the configuration file

        Returns:
            Dictionary with config info or None if not found
        """
        try:
            file_path = self.get_config_path(config_name)

            if not file_path:
                return None

            stat_info = os.stat(file_path)

            return {
                "name": config_name,
                "size": stat_info.st_size,
                "modified": stat_info.st_mtime,
                "is_default": self.get_default_config() == config_name
            }

        except OSError as e:
            logger.error(f"Error getting config info: {e}")
            return None
