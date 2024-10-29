#!/bin/bash

# Test script for verifying backend deployment
# Usage: ./test_deployment.sh <backend_url>

if [ -z "$1" ]; then
    echo "Usage: ./test_deployment.sh <backend_url>"
    exit 1
fi

BACKEND_URL=$1

echo "Testing backend deployment at $BACKEND_URL"

# Test health check endpoint
echo -e "\nTesting health check endpoint..."
curl -s "$BACKEND_URL/healthz" | jq '.'

# Test workspaces endpoint
echo -e "\nTesting workspaces endpoint..."
curl -s "$BACKEND_URL/workspaces" | jq '.'

# Test specific workspace occupancy
echo -e "\nTesting workspace occupancy endpoint..."
curl -s "$BACKEND_URL/workspace/1/occupancy" | jq '.'

# Test WebSocket connection (requires wscat)
echo -e "\nTesting WebSocket connection..."
echo "To test WebSocket manually:"
echo "wscat -c $BACKEND_URL/ws"

echo -e "\nDeployment tests completed"
