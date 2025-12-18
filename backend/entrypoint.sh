#!/bin/bash
set -e

if [ -e /var/run/docker.sock ]; then
    HOST_DOCKER_GID=$(stat -c '%g' /var/run/docker.sock)
  
    groupmod -g "$HOST_DOCKER_GID" docker || true
    echo "✅ Docker socket mapped to GID: $HOST_DOCKER_GID"
else
    echo "Warning: No Docker socket found."
fi


chown -R r4r:r4r /app/storage
export HOME="/home/r4r"
export USER="r4r"
export LOGNAME="r4r"
export VISUAL="/bin/true"
echo "Starting application as user 'r4r'..."
exec gosu r4r "$@"