#!/bin/bash

if curl -fs http://localhost:3000/health > /dev/null; then
    echo "API is healthy"
    exit 0
else
    echo "API is unhealthy"
    exit 1
fi
