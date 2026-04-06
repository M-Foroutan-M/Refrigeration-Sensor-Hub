#!/bin/bash

set -e

SERVICE_NAME="sensorhub.service"
SOURCE_SERVICE_FILE="/home/pi/Refrigeration-Sensor-Hub/services/${SERVICE_NAME}"
TARGET_SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}"

echo "Installing ${SERVICE_NAME}..."

if [ ! -f "$SOURCE_SERVICE_FILE" ]; then
    echo "Error: service file not found at $SOURCE_SERVICE_FILE"
    exit 1
fi

sudo cp "$SOURCE_SERVICE_FILE" "$TARGET_SERVICE_FILE"
sudo chmod 644 "$TARGET_SERVICE_FILE"

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling ${SERVICE_NAME}..."
sudo systemctl enable "$SERVICE_NAME"

echo "Restarting ${SERVICE_NAME}..."
sudo systemctl restart "$SERVICE_NAME"

echo "Service installed successfully."
echo
echo "Useful commands:"
echo "  sudo systemctl status ${SERVICE_NAME}"
echo "  sudo journalctl -u ${SERVICE_NAME} -f"
