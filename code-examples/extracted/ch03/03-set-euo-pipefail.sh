#!/bin/bash

set -euo pipefail

SOURCE="/var/log/myapp"
BACKUP="/var/backups/myapp"

mkdir -p "$BACKUP"

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

tar -czf "$BACKUP/logs_$TIMESTAMP.tar.gz" "$SOURCE"

echo "Backup created successfully"
