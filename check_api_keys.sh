#!/bin/bash
# Quick check to see which API keys are available

echo "🔍 Checking for API keys..."
echo ""

# Function to check and display key status
check_key() {
    local key_name=$1
    local key_value="${!key_name}"
    
    if [ -n "$key_value" ]; then
        # Show first 10 and last 10 characters
        local len=${#key_value}
        if [ $len -gt 20 ]; then
            local start="${key_value:0:10}"
            local end="${key_value: -10}"
            echo "✅ $key_name: ${start}...${end}"
        else
            echo "✅ $key_name: Set (too short to display safely)"
        fi
    else
        echo "❌ $key_name: NOT SET"
    fi
}

# Check Google API keys
echo "Google Search API:"
check_key "GOOGLE_API_KEY"
check_key "GOOGLE_CSE_ID"
check_key "GOOGLE_SEARCH_ENGINE_ID"

echo ""
echo "AI Services:"
check_key "OPENAI_API_KEY"
check_key "CLAUDE_API_KEY"

echo ""
echo "Contact Finding APIs:"
check_key "APOLLO_API_KEY"
check_key "HUNTER_API_KEY"

echo ""
echo "---"
echo ""

# Determine if we can run the test
if [ -n "$GOOGLE_API_KEY" ] && { [ -n "$GOOGLE_CSE_ID" ] || [ -n "$GOOGLE_SEARCH_ENGINE_ID" ]; }; then
    echo "✅ Ready to run search test!"
    echo "   Execute: ./run_search_test.sh"
else
    echo "❌ Missing required keys for search test"
    echo "   Need: GOOGLE_API_KEY and GOOGLE_CSE_ID"
    echo ""
    echo "Try running with Railway environment:"
    echo "   railway run ./check_api_keys.sh"
fi
