FROM alpine:3.19

# Install OpenVPN and dependencies
RUN apk add --no-cache \
    openvpn \
    iptables \
    iproute2 \
    ca-certificates \
    python3 \
    py3-pip \
    py3-flask \
    bash \
    jq

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    requests \
    werkzeug

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
