#!/bin/bash
set -e

echo "🔨 Building AI Lead Generation Platform for Cloudflare Pages..."

# Build Frontend
echo "📦 Building React frontend..."
cd frontend
npm ci
npm run build
cd ..

# Copy backend for Cloudflare Workers
echo "🔧 Preparing backend..."
mkdir -p .cloudflare-output
cp -r backend/* .cloudflare-output/

# Copy frontend build to output
cp -r frontend/dist .cloudflare-output/public

echo "✅ Build complete!"
