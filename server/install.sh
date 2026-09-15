#!/usr/bin/env bash
set -euo pipefail

BASE_DIR=/home/shalom/Dropbox/backups/used-for-recovery/linux/services/manhwa
APP_DIR=${BASE_DIR}/app
DOCROOT_HOST_PATH=${DOCROOT_HOST_PATH:-/home/shalom/Dropbox/backups/quests, hobbies and entertainment/manhwa}
IMAGE_NAME=${IMAGE_NAME:-manhwa-lighttpd}
CONTAINER_NAME=${CONTAINER_NAME:-manhwa-lighttpd}
SERVICE_NAME=${SERVICE_NAME:-manhwa-lighttpd}
HTTP_PORT=${HTTP_PORT:-24083}
# Must match DB_PATH in last_page.py / hide_chapter.py (the path *inside* the container).
CONTAINER_DB_PATH=/var/lib/manhwa/state.sqlite3
HOST_DB_PATH=${HOST_DB_PATH:-/var/lib/manhwa/state.sqlite3}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ $EUID -ne 0 ]]; then
  echo "install.sh must run as root" >&2
  exit 1
fi

install -d -o shalom -g shalom -m 0755 "$APP_DIR"
install -d -m 0755 "$(dirname "$HOST_DB_PATH")"
touch "$HOST_DB_PATH"
install -d -m 0755 "$DOCROOT_HOST_PATH"

install -o shalom -g shalom -m 0644 "$SCRIPT_DIR/Dockerfile" "$APP_DIR/Dockerfile"
install -o shalom -g shalom -m 0644 "$SCRIPT_DIR/lighttpd.conf" "$APP_DIR/lighttpd.conf"
install -o shalom -g shalom -m 0755 "$SCRIPT_DIR/entrypoint.sh" "$APP_DIR/entrypoint.sh"
install -o shalom -g shalom -m 0755 "$SCRIPT_DIR/last_page.py" "$APP_DIR/last_page.py"
install -o shalom -g shalom -m 0755 "$SCRIPT_DIR/hide_chapter.py" "$APP_DIR/hide_chapter.py"

docker build -t "$IMAGE_NAME" "$APP_DIR"

cat > /etc/systemd/system/"$SERVICE_NAME".service <<UNIT
[Unit]
Description=Manhwa lighttpd container
After=docker.service
Requires=docker.service

[Service]
Restart=always
ExecStartPre=-/usr/bin/docker rm -f "$CONTAINER_NAME"
ExecStart=/usr/bin/docker run --rm --name "$CONTAINER_NAME" \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --tmpfs /run:rw,noexec,nosuid,size=16m \
  --cap-drop=ALL \
  --security-opt no-new-privileges:true \
  --pids-limit=64 \
  --memory=256m \
  --cpus=1 \
  -p ${HTTP_PORT}:80 \
  -v "$DOCROOT_HOST_PATH":/srv/www:ro \
  -v "$HOST_DB_PATH":"$CONTAINER_DB_PATH" \
  "$IMAGE_NAME"
ExecStop=-/usr/bin/docker stop "$CONTAINER_NAME"

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"
echo "Installed $SERVICE_NAME"
