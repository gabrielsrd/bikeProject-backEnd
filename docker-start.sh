#!/bin/bash

# Docker startup script for bikeProject backend
# This script builds and runs the Django backend in Docker with SQLite

echo "🚀 Starting bikeProject Backend with Docker..."
echo ""

# Stop any existing containers
echo "📦 Stopping any existing containers..."
docker compose -f docker-compose.sqlite.yml down

# Build the image
echo "🔨 Building Docker image..."
docker compose -f docker-compose.sqlite.yml build

# Start the container
echo "▶️  Starting container..."
docker compose -f docker-compose.sqlite.yml up

# Note: Press Ctrl+C to stop the server
# To run in background (detached mode), use: docker compose -f docker-compose.sqlite.yml up -d
