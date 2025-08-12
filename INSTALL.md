# Installation Guide

## 🚀 **Quick Start**

### **Prerequisites**
- **Python 3.9+** (Linux, macOS, Windows supported)
- **GitHub Personal Access Token** with `repo` and `actions:read` permissions
- **AI API Key** (OpenAI or Anthropic) for analysis capabilities

### **Installation**

#### **Option 1: Development Install (Recommended for testing)**
```bash
# Clone or navigate to the project directory
cd gha-optimizer
```

# Install in development mode
pip install -e .

# Verify installation
gha-optimizer --version
```

### **Setup GitHub Token**

1. **Create a GitHub Personal Access Token**:
   - Go to GitHub → Settings → Developer settings → Personal access tokens
   - Generate new token with `repo` and `actions:read` permissions

2. **Set environment variable**:
   ```bash
   export GITHUB_TOKEN=ghp_your_token_here
   ```

### **Development Setup**

```bash
# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/gha_optimizer/
```
