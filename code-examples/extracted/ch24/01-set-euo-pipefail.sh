#!/bin/bash

set -euo pipefail

if curl -fsS http://localhost:3000/health; then
    echo "API healthy"
else
    echo "API unhealthy"
    exit 1
fi
