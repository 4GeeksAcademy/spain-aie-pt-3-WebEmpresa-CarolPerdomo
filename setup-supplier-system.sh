#!/bin/bash
# Setup script for Supplier Management System

set -e

echo "================================================"
echo "  Supplier Management — Setup Script"
echo "================================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Backend setup
echo -e "\n${BLUE}1. Installing backend dependencies...${NC}"
cd services/supplier_management

if command -v uv &> /dev/null; then
    echo "Using uv..."
    uv sync
else
    echo "Using pip..."
    pip install -q fastapi uvicorn pydantic pydantic-settings tinydb python-multipart
fi

echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Seed database
echo -e "\n${BLUE}2. Seeding database with initial suppliers...${NC}"
if command -v uv &> /dev/null; then
    uv run seed.py
else
    python seed.py
fi

echo -e "${GREEN}✓ Database seeded${NC}"

# Frontend setup
echo -e "\n${BLUE}3. Installing frontend dependencies...${NC}"
cd ../../uis/backoffice

if [ ! -d "node_modules" ]; then
    npm install -q
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
fi

# Summary
echo -e "\n================================================"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd services/supplier_management"
echo "    python main.py"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd uis/backoffice"
echo "    npm run dev -- --port 3001"
echo ""
echo "Then open:"
echo "  • API docs: http://localhost:8000/docs"
echo "  • Backoffice: http://localhost:3001/suppliers"
echo ""
echo "See SUPPLIER_QUICKSTART.md for more info"
echo ""
