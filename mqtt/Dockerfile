# ============================================================================
# EnMS - MQTT Broker (Eclipse Mosquitto)
# Zero-touch deployment with auto-generated credentials
# ============================================================================

FROM eclipse-mosquitto:2.0

# Copy configuration
COPY config/mosquitto.conf /mosquitto/config/mosquitto.conf

# Create password file with default credentials during build
# Username: raptorblingx, Password: raptorblingx
RUN mosquitto_passwd -c -b /mosquitto/config/passwd raptorblingx raptorblingx && \
    chown mosquitto:mosquitto /mosquitto/config/passwd && \
    chmod 600 /mosquitto/config/passwd

# Ensure proper ownership
RUN chown -R mosquitto:mosquitto /mosquitto/config

EXPOSE 1883 9001

CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
