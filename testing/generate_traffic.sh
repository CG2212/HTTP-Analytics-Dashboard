#!/bin/bash

echo "Starting continuous HTTP traffic..."
echo "Press Ctrl+C to stop."

while true
do
    echo "[$(date '+%H:%M:%S')] DELETE"
    curl -s -o /dev/null -w "HTTP %{http_code}\n" \
        -X DELETE \
        http://localhost:8000/proxy/get

    echo "[$(date '+%H:%M:%S')] POST"
    curl -s -o /dev/null -w "HTTP %{http_code}\n" \
        -X POST \
        -A "MobileAgent/1.0" \
        -H "Content-Type: application/json" \
        -d '{"key":"value"}' \
        http://localhost:8000/proxy/post

    echo "[$(date '+%H:%M:%S')] GET"
    curl -s -o /dev/null -w "HTTP %{http_code}\n" \
        -A "CustomApp/2.1" \
        http://localhost:8000/proxy/get

    sleep 0.1
done