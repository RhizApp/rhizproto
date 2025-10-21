#!/bin/bash
# Generate TypeScript types from protocol schemas

set -e

echo "🔧 Generating TypeScript types..."

# Build protocol package first
cd packages/protocol
pnpm build

echo "✅ Protocol types generated"

# Copy types to other packages that need them
echo "📦 Distributing types to dependent packages..."

# SDK types
echo "  - Copying to sdk-ts..."
# Types are already available via workspace dependency

# Web app types
echo "  - Copying to web..."
# Types are already available via workspace dependency

echo "✅ Type generation complete!"

