#!/bin/bash
# Quick start script for Nexova API
# This script starts the FastAPI server with all authentication and user management features

set -e

echo "🚀 Starting Nexova API with Authentication System"
echo "=================================================="

# Check if SECRET_KEY is set
if [ -z "$SECRET_KEY" ]; then
    echo "⚠️  SECRET_KEY not set. Using default for development."
    export SECRET_KEY="dev-secret-key-change-in-production-12345"
fi

echo "✅ SECRET_KEY is set"
echo ""
echo "Installing dependencies..."
cd services/api

# Install dependencies
pip install PyJWT bcrypt pydantic[email] fastapi uvicorn tinydb python-multipart -q

echo "✅ Dependencies installed"
echo ""
echo "Starting API server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the API
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
