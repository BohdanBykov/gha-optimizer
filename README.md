# GHA-Optimizer 🚀

**AI-Powered GitHub Actions Workflow Optimization Tool**

A pluggable tool that analyzes GitHub Actions workflows and generates actionable optimization recommendations with quantified impact metrics.

## 🎯 Vision

Transform any GitHub organization's CI/CD efficiency by 
**Reducing build times** leads to:
- **Cutting runner costs** through intelligent resource optimization  
- **Improving developer productivity** by eliminating wait times
- **Automating best practice adoption** across teams

## ✨ Features

### 🤖 **AI-Powered Analysis**
- **Real-time GitHub API integration** - Live workflow and run history data
- **GPT-4/Claude analysis** - Advanced pattern recognition and optimization strategies
- **Comprehensive scanning** - All `.github/workflows/*` configurations analyzed
- **Best practices enforcement** - Based on industry-standard optimization patterns

### 📊 **Quantified Impact Metrics**
- **Monthly cost savings** - Precise dollar amounts based on runner usage
- **Time optimization** - Minutes saved per workflow run
- **ROI calculations** - Clear cost-benefit analysis for each recommendation
- **Priority-based recommendations** - High/medium/low impact categorization

### 🔌 **Easy Integration**
- **CLI Tool**: `gha-optimizer scan --repo your-org/repo`
- **Linux-native**: Optimized for DevOps and CI/CD environments

## 🚀 Quick Start

**Requirements**: Python 3.9+, GitHub token, AI API key

### 2. Configuration
```bash
# Set required environment variables
export GITHUB_TOKEN=ghp_your_token_here
export OPENAI_API_KEY=sk-your_openai_key_here
# OR configure in config.yml (see examples/config.yml)
```

> 📋 **Detailed Setup**: See [Configuration Guide](./docs/configuration.md) for all options

### 3. Analyze Repository
```bash
# Basic analysis with AI-powered recommendations
gha-optimizer scan microsoft/vscode

# Analyze recent activity (last 7 days)
gha-optimizer scan microsoft/vscode --max-history-days 7

# Generate detailed report file
gha-optimizer scan microsoft/vscode --output report.md --format markdown
```

### 4. Apply Optimizations
```bash
# Apply high-priority optimizations (coming in v0.2.0)
gha-optimizer apply microsoft/vscode --priority high

```

See [INSTALL.md](./INSTALL.md) for detailed installation instructions.

## 🏗️ Architecture

See [docs/architecture.md](./docs/architecture.md) for detailed system design and [docs/ai-schema.md](./docs/ai-schema.md) for AI response format specification.

## 📋 Implementation Plan

- **Phase 1**: Core analysis engine + basic recommendations
- **Phase 2**: AI-powered optimization suggestions
- **Phase 3**: Automated PR generation + monitoring
- **Phase 4**: Multi-org dashboards + enterprise features

## 🤝 Contributing

This project is part of a DevOps automation challenge. See [CONTRIBUTING.md](./CONTRIBUTING.md) for development setup.

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details. 