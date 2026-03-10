#!/usr/bin/env bash
set -e

echo "Starting OpenVPN Manager Add-on..."

# Create necessary directories
mkdir -p /data/configs /data/logs

# Read configuration
CONFIG_PATH=/data/options.json

if [ -f "$CONFIG_PATH" ]; then
    API_PORT=$(jq -r '.api_port // 9876' "$CONFIG_PATH")
    LOG_LEVEL=$(jq -r '.log_level // "info"' "$CONFIG_PATH")
    AUTO_START=$(jq -r '.auto_start // true' "$CONFIG_PATH")

    echo "Configuration loaded:"
    echo "  API Port: $API_PORT"
    echo "  Log Level: $LOG_LEVEL"
    echo "  Auto Start: $AUTO_START"

    export API_PORT
    export LOG_LEVEL
    export AUTO_START
else
    echo "No configuration found, using defaults"
    export API_PORT=9876
    export LOG_LEVEL=info
    export AUTO_START=true
fi

# Start Flask API server
echo "Starting API server on port $API_PORT..."
cd /opt/openvpn_manager
python3 api_server.py &

# Wait for API server to start
sleep 2

echo "OpenVPN Manager Add-on started successfully"
echo "API available at http://localhost:$API_PORT/api"

# Keep container running
wait
