#!/bin/bash
# Development environment check script

set -e

echo "🔍 Checking Rhiz development environment..."
echo ""

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    echo "✅ Node.js: $NODE_VERSION"
else
    echo "❌ Node.js not found. Install from https://nodejs.org/"
    exit 1
fi

# Check pnpm
if command -v pnpm &> /dev/null; then
    PNPM_VERSION=$(pnpm -v)
    echo "✅ pnpm: $PNPM_VERSION"
else
    echo "❌ pnpm not found. Install with: npm install -g pnpm"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found. Install from https://python.org/"
    exit 1
fi

# Check Poetry
if command -v poetry &> /dev/null; then
    POETRY_VERSION=$(poetry --version)
    echo "✅ Poetry: $POETRY_VERSION"
else
    echo "❌ Poetry not found. Install from https://python-poetry.org/"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "✅ Docker: $DOCKER_VERSION"

    # Check if Docker is running
    if docker ps &> /dev/null; then
        echo "✅ Docker daemon is running"
    else
        echo "⚠️  Docker daemon not running. Start Docker Desktop."
    fi
else
    echo "❌ Docker not found. Install from https://docker.com/"
    exit 1
fi

# Check PostgreSQL container
if docker ps | grep -q rhiz-postgres; then
    echo "✅ PostgreSQL container is running"
else
    echo "⚠️  PostgreSQL container not running. Run: make docker-up"
fi

# Check Redis container
if docker ps | grep -q rhiz-redis; then
    echo "✅ Redis container is running"
else
    echo "⚠️  Redis container not running. Run: make docker-up"
fi

# Check .env file
if [ -f ".env" ]; then
    echo "✅ .env file exists"
else
    echo "⚠️  .env file not found. Copy from .env.example"
fi

echo ""
echo "🎉 Environment check complete!"
echo ""
echo "Next steps:"
echo "  1. make install  # Install dependencies"
echo "  2. make dev      # Start development servers"

