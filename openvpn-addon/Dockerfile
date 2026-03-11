FROM alpine:3.19

# Install OpenVPN and dependencies
RUN apk add --no-cache \
    openvpn \
    iptables \
    iproute2 \
    ca-certificates \
    python3 \
    py3-flask \
    py3-requests \
    py3-werkzeug \
    bash \
    jq

# Create directories
RUN mkdir -p /opt/openvpn_manager /data/configs /data/logs

# Copy application files
COPY rootfs/ /

# Make scripts executable
RUN chmod +x /run.sh

# Set working directory
WORKDIR /opt/openvpn_manager

# Expose API port
EXPOSE 9876

# Run startup script
CMD ["/run.sh"]
