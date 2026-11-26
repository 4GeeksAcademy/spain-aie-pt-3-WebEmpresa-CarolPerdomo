#!/bin/bash

# Nexova API Server Startup Script

# Activate virtual environment if using one
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set default environment variables if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file with default values..."
    cat > .env << EOF
SECRET_KEY=dev-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=./data/db.json
API_PORT=8000
API_HOST=0.0.0.0
EOF
fi

# Create data directory if it doesn't exist
mkdir -p data

# Start the server
echo "Starting Nexova API server on http://localhost:8000"
echo "Interactive API docs available at http://localhost:8000/docs"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
