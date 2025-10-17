#!/bin/bash
# Check if API keys are available in Railway environment

echo "🔍 Checking Railway API Keys..."
echo ""

# Try to use railway run to check environment
echo "Attempting to read environment variables from Railway..."
echo ""

railway run bash -c 'echo "=== API Keys Status ===" && \
echo "Google API Key: ${GOOGLE_API_KEY:+SET (${#GOOGLE_API_KEY} chars)} ${GOOGLE_API_KEY:-NOT SET}" && \
echo "Google CSE ID: ${GOOGLE_CSE_ID:+SET} ${GOOGLE_CSE_ID:-NOT SET}" && \
echo "Hunter API Key: ${HUNTER_API_KEY:+SET (${#HUNTER_API_KEY} chars)} ${HUNTER_API_KEY:-NOT SET}" && \
echo "OpenAI API Key: ${OPENAI_API_KEY:+SET (${#OPENAI_API_KEY} chars)} ${OPENAI_API_KEY:-NOT SET}" && \
echo "Claude API Key: ${CLAUDE_API_KEY:+SET (${#CLAUDE_API_KEY} chars)} ${CLAUDE_API_KEY:-NOT SET}"'
