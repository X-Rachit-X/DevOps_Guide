#!/bin/bash

set -euo pipefail

APP_DIR="/opt/my-api"

echo "Deploying application..."

cd "$APP_DIR"

echo "Pulling latest code..."
git pull origin main

echo "Installing dependencies..."
npm ci

echo "Building..."
npm run build

echo "Running tests..."
npm test

echo "Restarting service..."
sudo systemctl restart my-api

echo "Checking application..."

if curl -fs http://localhost:3000/health > /dev/null; then
    echo "Deployment successful"
else
    echo "Deployment failed: health check unsuccessful"
    exit 1
fi
