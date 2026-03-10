"""OpenVPN Manager - Flask API Server."""
import os
import logging
from flask import Flask, request, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
from vpn_manager import VPNManager
from config_handler import ConfigHandler
from utils import create_api_response, get_log_level, format_uptime

# Configure logging
log_level_str = os.environ.get('LOG_LEVEL', 'info')
logging.basicConfig(
    level=get_log_level(log_level_str),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max upload

# Initialize managers
vpn_manager = VPNManager()
config_handler = ConfigHandler()

logger.info("OpenVPN Manager API Server initialized")


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify(create_api_response(
        success=True,
        data={"status": "healthy"}
    ))


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get VPN status."""
    try:
        status = vpn_manager.get_status()

        # Add formatted uptime
        if status['uptime'] > 0:
            status['uptime_formatted'] = format_uptime(status['uptime'])

        return jsonify(create_api_response(
            success=True,
            status=status['status'],
            data=status
        ))
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500


@app.route('/api/start', methods=['POST'])
def start_vpn():
    """Start VPN connection."""
    try:
        data = request.get_json() or {}
        config_name = data.get('config_name')

        logger.info(f"API request to start VPN with config: {config_name}")

        result = vpn_manager.start_vpn(config_name)

        if result['success']:
            return jsonify(create_api_response(
                success=True,
                status='connecting',
                data=result
            ))
        else:
            return jsonify(create_api_response(
                success=False,
                error=result.get('error', 'Unknown error')
            )), 400

    except Exception as e:
        logger.error(f"Error starting VPN: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500


@app.route('/api/stop', methods=['POST'])
def stop_vpn():
    """Stop VPN connection."""
    try:
        logger.info("API request to stop VPN")

        result = vpn_manager.stop_vpn()

        if result['success']:
            return jsonify(create_api_response(
                success=True,
                status='disconnected',
                data=result
            ))
        else:
            return jsonify(create_api_response(
                success=False,
                error=result.get('error', 'Unknown error')
            )), 400

    except Exception as e:
        logger.error(f"Error stopping VPN: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500


@app.route('/api/upload', methods=['POST'])
def upload_config():
    """Upload OpenVPN configuration file."""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify(create_api_response(
                success=False,
                error='No file provided'
            )), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify(create_api_response(
                success=False,
                error='No file selected'
            )), 400

        # Read file content
        content = file.read()
        filename = file.filename

        logger.info(f"API request to upload config: {filename} ({len(content)} bytes)")

        # Upload and validate
        result = config_handler.upload_config(filename, content)

        if result['success']:
            return jsonify(create_api_response(
                success=True,
                data=result
            ))
        else:
            return jsonify(create_api_response(
                success=False,
                error=result.get('error', 'Upload failed')
            )), 400

    except RequestEntityTooLarge:
        return jsonify(create_api_response(
            success=False,
            error='File too large (max 2MB)'
        )), 413
    except Exception as e:
        logger.error(f"Error uploading config: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500


@app.route('/api/configs', methods=['GET'])
def list_configs():
    """List all configuration files."""
    try:
        configs = config_handler.list_configs()
        default_config = config_handler.get_default_config()

        # Get detailed info for each config
        config_list = []
        for config_name in configs:
            info = config_handler.get_config_info(config_name)
            if info:
                config_list.append(info)

        return jsonify(create_api_response(
            success=True,
            data={
                'configs': config_list,
                'default': default_config,
                'count': len(config_list)
            }
        ))

    except Exception as e:
        logger.error(f"Error listing configs: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500


@app.route('/api/configs/<config_name>', methods=['DELETE'])
def delete_config(config_name):
    """Delete a configuration file."""
    try:
        logger.info(f"API request to delete config: {config_name}")

        # Check if VPN is running with this config
        status = vpn_manager.get_status()
        if status['is_running'] and status['current_config'] == config_name:
            return jsonify(create_api_response(
                success=False,
                error='Cannot delete configuration that is currently in use. Stop VPN first.'
            )), 400

        result = config_handler.delete_config(config_name)

        if result['success']:
            return jsonify(create_api_response(
                success=True,
                data=result
            ))
        else:
            return jsonify(create_api_response(
                success=False,
                error=result.get('error', 'Delete failed')
            )), 400

    except Exception as e:
        logger.error(f"Error deleting config: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500


@app.route('/api/configs/<config_name>/default', methods=['POST'])
def set_default_config(config_name):
    """Set default configuration file."""
    try:
        logger.info(f"API request to set default config: {config_name}")

        success = config_handler.set_default_config(config_name)

        if success:
            return jsonify(create_api_response(
                success=True,
                data={'default': config_name}
            ))
        else:
            return jsonify(create_api_response(
                success=False,
                error='Failed to set default configuration'
            )), 400

    except Exception as e:
        logger.error(f"Error setting default config: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get OpenVPN logs."""
    try:
        lines = request.args.get('lines', default=50, type=int)
        lines = min(max(lines, 1), 500)  # Limit between 1 and 500

        logs = vpn_manager.get_vpn_logs(lines)

        return jsonify(create_api_response(
            success=True,
            data={'logs': logs, 'lines': lines}
        ))

    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500


@app.route('/api/info', methods=['GET'])
def get_info():
    """Get OpenVPN Manager information."""
    try:
        openvpn_installed = vpn_manager.check_openvpn_installed()
        openvpn_version = vpn_manager.get_openvpn_version()

        return jsonify(create_api_response(
            success=True,
            data={
                'openvpn_installed': openvpn_installed,
                'openvpn_version': openvpn_version,
                'api_version': '1.0.0'
            }
        ))

    except Exception as e:
        logger.error(f"Error getting info: {e}")
        return jsonify(create_api_response(
            success=False,
            error=str(e)
        )), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify(create_api_response(
        success=False,
        error='Endpoint not found'
    )), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify(create_api_response(
        success=False,
        error='Internal server error'
    )), 500


if __name__ == '__main__':
    # Get configuration from environment
    api_port = int(os.environ.get('API_PORT', 9876))

    logger.info(f"Starting OpenVPN Manager API Server on port {api_port}")

    # Run Flask app
    # Bind to 0.0.0.0 to allow connections from Home Assistant Core
    # In production add-on environment, this is still local network only
    app.run(
        host='0.0.0.0',
        port=api_port,
        debug=False,
        threaded=True
    )
