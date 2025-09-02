# Installation Guide

## 📋 Prerequisites

- **Python 3.11+** (Linux, macOS)
- **Git** for cloning the repository
- **GitHub Personal Access Token** ([create one here](https://github.com/settings/tokens))
- **Anthropic API key**

## 🚀 Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd gha-optimizer
```

### 2. Install the Package
```bash
# Install in development mode
pip install -e .

# Verify installation works
gha-optimizer --version
gha-optimizer --help
```

### 3. Setup GitHub Authentication
```bash
# Create a GitHub token with 'repo' and 'actions:read' permissions
# Then set it as an environment variable:
export GITHUB_TOKEN=ghp_your_token_here
```

### 4. Setup AI Key
Only Anthropic API key supported now:

```bash
# For Anthropic (Claude):
export ANTHROPIC_API_KEY=sk-ant-your_anthropic_key
```

### 5. Test Your Setup
```bash
# Test with a public repository
gha-optimizer scan microsoft/vscode --max-history-days 7

# Test with debug features
gha-optimizer scan microsoft/vscode --local-docs --output-prompt-file debug.txt
```

## 🔧 Alternative Configuration

Instead of environment variables, create a `config.yml` file:

```yaml
github:
  token: "ghp_your_token_here"

ai:
  provider: "anthropic"
  api_key: "sk-ant-your_anthropic_key"
  model: "claude-3-haiku-20240307"

analysis:
  max_history_days: 30
```

Then run:
```bash
gha-optimizer --config config.yml scan your-org/your-repo
```

## 🐛 Troubleshooting

**Command not found**: Make sure you installed with `pip install -e .`

**GitHub API errors**: Verify your token has correct permissions and isn't expired

**Python version**: Requires Python 3.11+, check with `python --version`

**Permission errors**: Make sure your GitHub token can access the repository you're analyzing
