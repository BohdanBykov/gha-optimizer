#!/bin/bash

# GHA-Optimizer Testing Setup Script
# This script helps set up the testing environment

echo "🚀 GHA-Optimizer Testing Setup"
echo "==============================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the gha-optimizer project root"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists curl; then
    echo "❌ curl is required but not installed"
    exit 1
fi

if ! command_exists git; then
    echo "❌ git is required but not installed"  
    exit 1
fi

echo "✅ Prerequisites check passed"

# Check GitHub token
echo ""
echo "🔑 Checking GitHub API token..."
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ GITHUB_TOKEN environment variable not set"
    echo "📝 Please follow these steps:"
    echo "   1. Go to https://github.com/settings/tokens"
    echo "   2. Generate new token with 'repo' and 'workflow' permissions"
    echo "   3. Export token: export GITHUB_TOKEN=ghp_your_token_here"
    echo "   4. Add to shell profile: echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.bashrc"
    GITHUB_TOKEN_SET=false
else
    # Test GitHub token
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: token $GITHUB_TOKEN" \
        https://api.github.com/user)
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ GitHub token is valid"
        GITHUB_TOKEN_SET=true
    else
        echo "❌ GitHub token is invalid (HTTP $HTTP_STATUS)"
        GITHUB_TOKEN_SET=false
    fi
fi

# Check AI API token
echo ""
echo "🤖 Checking AI API token..."
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OpenAI API key found"
    AI_TOKEN_SET=true
elif [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ Anthropic API key found"
    AI_TOKEN_SET=true
else
    echo "❌ No AI API key found"
    echo "📝 Please set up one of these:"
    echo "   OpenAI: export OPENAI_API_KEY=sk-your_openai_key"
    echo "   Anthropic: export ANTHROPIC_API_KEY=sk-ant-your_anthropic_key"
    AI_TOKEN_SET=false
fi

# Create test config file
echo ""
echo "📄 Creating test configuration..."

cat > test-config.yml << EOF
github:
  token: "${GITHUB_TOKEN}"
  api_url: "https://api.github.com"

ai:
  provider: "openai"
  api_key: "${OPENAI_API_KEY}"
  model: "gpt-4"

analysis:
  max_history_days: 30
  confidence_threshold: 0.7
  parallel_requests: 3

output:
  default_format: "markdown"
  include_code_examples: true
  generate_pr_descriptions: true
EOF

echo "✅ Created test-config.yml"

# Test CLI installation
echo ""
echo "🔧 Testing CLI installation..."

if [ -f "src/gha_optimizer/cli/main.py" ]; then
    echo "✅ CLI source code found"
    
    # Try to run CLI help
    if python -m src.gha_optimizer.cli.main --help >/dev/null 2>&1; then
        echo "✅ CLI is working"
        CLI_WORKING=true
    else
        echo "❌ CLI has issues. Try: pip install -e ."
        CLI_WORKING=false
    fi
else
    echo "❌ CLI source code not found"
    CLI_WORKING=false
fi

# Summary
echo ""
echo "📊 Setup Summary"
echo "================="
echo "GitHub Token: $([ "$GITHUB_TOKEN_SET" = true ] && echo "✅ Ready" || echo "❌ Needs setup")"
echo "AI API Token: $([ "$AI_TOKEN_SET" = true ] && echo "✅ Ready" || echo "❌ Needs setup")"
echo "CLI Working:  $([ "$CLI_WORKING" = true ] && echo "✅ Ready" || echo "❌ Needs setup")"

if [ "$GITHUB_TOKEN_SET" = true ] && [ "$AI_TOKEN_SET" = true ] && [ "$CLI_WORKING" = true ]; then
    echo ""
echo "🎉 All systems ready! You can now:"
echo "   1. Create GitHub repository 'gha-optimizer-test-repo'"
echo "   2. Copy files from test-repos/gha-optimizer-test-repo/ to your repository"
echo "   3. Run: gha-optimizer --config test-config.yml scan your-username/gha-optimizer-test-repo"
echo "   4. See docs/testing-setup.md for detailed instructions"
else
    echo ""
    echo "⚠️  Please complete the setup steps above before testing"
    echo "📚 See docs/testing-setup.md for detailed instructions"
fi