#!/bin/bash

set -euo pipefail

REPO_DIR="/home/pi/Refrigeration-Sensor-Hub"
LOCAL_DIR="${REPO_DIR}/data/raw"
REMOTE_NAME="gdrive"
REMOTE_DIR="Refrigeration-Sensor-Hub"

echo "Manual Google Drive sync"
echo "Local:  ${LOCAL_DIR}"
echo "Remote: ${REMOTE_NAME}:${REMOTE_DIR}"
echo

if ! command -v rclone >/dev/null 2>&1; then
    echo "Error: rclone is not installed or not in PATH."
    exit 1
fi

if ! rclone listremotes | grep -q "^${REMOTE_NAME}:$"; then
    echo "Error: rclone remote '${REMOTE_NAME}:' was not found."
    echo "Run 'rclone config' first."
    exit 1
fi

mkdir -p "${LOCAL_DIR}"

echo "Starting upload..."
rclone copy "${LOCAL_DIR}" "${REMOTE_NAME}:${REMOTE_DIR}" --create-empty-src-dirs --progress

echo
echo "Upload complete."
echo "Recent remote files:"
rclone ls "${REMOTE_NAME}:${REMOTE_DIR}" | tail -n 20
