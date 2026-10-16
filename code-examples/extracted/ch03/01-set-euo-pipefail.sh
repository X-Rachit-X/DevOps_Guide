#!/bin/bash

set -euo pipefail

echo "Starting deployment..."

git pull origin main

npm ci

npm run build

npm test

sudo systemctl restart my-api

echo "Deployment successful."
