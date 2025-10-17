#!/bin/bash
# Quick test runner for Google Search API
# Usage: ./run_search_test.sh [GOOGLE_API_KEY] [GOOGLE_CSE_ID]

echo "=================================="
echo "🔍 Google Search API Test Runner"
echo "=================================="
echo ""

# Check if API keys provided as arguments
if [ "$#" -eq 2 ]; then
    export GOOGLE_API_KEY="$1"
    export GOOGLE_CSE_ID="$2"
    echo "✅ Using API keys from command line arguments"
elif [ -n "$GOOGLE_API_KEY" ] && [ -n "$GOOGLE_CSE_ID" ]; then
    echo "✅ Using API keys from environment variables"
elif [ -n "$GOOGLE_API_KEY" ] && [ -n "$GOOGLE_SEARCH_ENGINE_ID" ]; then
    export GOOGLE_CSE_ID="$GOOGLE_SEARCH_ENGINE_ID"
    echo "✅ Using API keys from environment variables (GOOGLE_SEARCH_ENGINE_ID)"
else
    echo "❌ API keys not found!"
    echo ""
    echo "Please provide API keys in one of these ways:"
    echo ""
    echo "Option 1 - Command line:"
    echo "  ./run_search_test.sh YOUR_GOOGLE_API_KEY YOUR_CSE_ID"
    echo ""
    echo "Option 2 - Environment variables:"
    echo "  export GOOGLE_API_KEY='your_key_here'"
    echo "  export GOOGLE_CSE_ID='your_cse_id_here'"
    echo "  ./run_search_test.sh"
    echo ""
    echo "Option 3 - Use Railway environment:"
    echo "  railway run ./run_search_test.sh"
    echo ""
    exit 1
fi

echo ""
echo "📋 Configuration:"
echo "   GOOGLE_API_KEY: ${GOOGLE_API_KEY:0:15}...${GOOGLE_API_KEY: -10}"
echo "   GOOGLE_CSE_ID: $GOOGLE_CSE_ID"
echo ""
echo "🚀 Starting test..."
echo ""

# Run the test
python3 test_search_simple.py

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "✅ Test completed successfully!"
else
    echo "❌ Test failed with exit code: $exit_code"
fi

exit $exit_code
