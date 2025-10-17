#!/bin/bash
# Setup environment variables for testing
# Usage: source setup_test_env.sh

echo "🔧 Setting up test environment..."
echo ""
echo "Please provide your API keys:"
echo ""

# Google API Key
read -p "Enter GOOGLE_API_KEY: " google_key
export GOOGLE_API_KEY="$google_key"

# Google CSE ID
read -p "Enter GOOGLE_CSE_ID (Custom Search Engine ID): " cse_id
export GOOGLE_CSE_ID="$cse_id"

echo ""
echo "✅ Environment variables set!"
echo "   GOOGLE_API_KEY: ${GOOGLE_API_KEY:0:10}...${GOOGLE_API_KEY: -10}"
echo "   GOOGLE_CSE_ID: $GOOGLE_CSE_ID"
echo ""
echo "Now run: python3 test_search_simple.py"
