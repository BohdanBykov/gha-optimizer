# GHA-Optimizer 🚀

**AI-Powered GitHub Actions Workflow Optimization Tool**

Automatically analyze your GitHub Actions workflows and get actionable optimization recommendations with quantified savings.

## 🎯 What It Does

GHA-Optimizer scans your GitHub repositories and finds ways to make your CI/CD workflows faster and cheaper:

- **🔍 Analyzes** all your `.github/workflows/*.yml` files
- **🤖 Uses AI** to understand your workflows and suggest improvements  
- **💰 Calculates** exact time and money savings for each recommendation
- **📝 Generates** ready-to-use code examples you can copy-paste

## ✨ Key Benefits

- **Save Time**: Reduce workflow run times by 30-50%
- **Save Money**: Lower GitHub Actions runner costs
- **Accurate Analysis**: Uses version-specific optimization patterns for consistent recommendations
- **Best Practices**: Automatically apply proven CI/CD optimization patterns
- **Easy Setup**: Get started in under 5 minutes

## 🚀 Quick Start

### 1. Install
```bash
# Clone and install
git clone <current_repo>
cd gha-optimizer
pip install -e .
```

### 2. Setup Authentication
```bash
# Get a GitHub token from: https://github.com/settings/tokens
export GITHUB_TOKEN=ghp_your_token_here

# Get an Anthropic API key (optional but recommended):
export ANTHROPIC_API_KEY=sk-ant-your_key_here
```

### 3. Analyze a Repository
```bash
# Analyze any public repository
gha-optimizer scan microsoft/vscode

# Or analyze with more recent data
gha-optimizer scan microsoft/vscode --max-history-days 7

# Analyze specific workflow files only
gha-optimizer scan microsoft/vscode -w \'ci.yml\' -w \'test.yml\'

# Debug: Save AI prompt to file (doesn't block analysis)
gha-optimizer scan microsoft/vscode --output-prompt-file debug_prompt.txt

# Debug: Save AI response to file before report generation
gha-optimizer scan microsoft/vscode --output-ai-response debug_response.json
```

### 4. Get Your Results
The tool will show you:
- 📊 **Impact Summary**: Total time and cost savings
- 🎯 **Prioritized Recommendations**: What to fix first
- 💻 **Code Examples**: Ready-to-use YAML snippets
- 📈 **Confidence Scores**: How sure we are about each suggestion

## 📖 Documentation

- **[Installation Guide](./INSTALL.md)** - Detailed setup instructions
- **[Contributing Guide](./CONTRIBUTING.md)** - How to contribute to the project
- **[Architecture Overview](./docs/architecture.md)** - Technical details
- **[Optimization Patterns](./docs/optimization-patterns.md)** - Version-aligned optimization patterns and guidelines

## 🛠️ Development

Want to contribute? Here's how to get started:

```bash
# Setup development environment
git clone <current_repo>
cd gha-optimizer
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
python test_cli.py
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed development guidelines.

## 🐛 Debugging Features

For development and troubleshooting, you can use these debugging options:

### Debug Options

For development and troubleshooting, you can use these debugging options:

#### Save AI Prompt to File
When you want to see exactly what prompt is being sent to the AI:

```bash
# Generate and save the AI prompt to a file
gha-optimizer scan microsoft/vscode --output-prompt-file debug_prompt.txt
```

This is useful for:
- **Debugging AI responses**: See exactly what context the AI receives
- **Prompt optimization**: Analyze and improve the prompts we send
- **Cost estimation**: Preview what will be sent before using API credits  
- **Offline analysis**: Generate prompts to analyze later

The generated file contains the complete prompt with:
- Repository context and statistics
- All workflow YAML files with line numbers
- Optimization pattern guidelines
- Structured output requirements

#### Save AI Response to File
When you want to see the raw AI response before it's processed into recommendations:

```bash
# Save AI response to file before report generation
gha-optimizer scan microsoft/vscode --output-ai-response debug_response.json
```

This is useful for:
- **Debugging AI parsing**: See the raw JSON response from the AI
- **Response validation**: Verify the AI is returning the expected format
- **Performance analysis**: Analyze response quality and completeness
- **Development testing**: Test AI response handling without affecting reports

The generated file contains the raw JSON response with all optimization recommendations as returned by the AI.

## 📚 Documentation-Driven Analysis

GHA-Optimizer uses a unique approach to ensure accurate and consistent AI recommendations:

### Version-Aligned Documentation
- **Comprehensive Patterns**: All optimization patterns are packaged with the tool for consistent access
- **Version Control**: Documentation versions match tool releases for consistency
- **AI Reference**: The AI analyzer loads packaged documentation to guide analysis
- **Pattern Specificity**: Each pattern includes confidence guidelines and impact calculations

### Benefits of This Approach
- **Consistent Results**: Same workflows analyzed with same tool version produce identical recommendations
- **Transparent Logic**: All optimization patterns are documented and auditable
- **Reduced Hallucination**: AI follows specific documented patterns rather than general knowledge
- **Version Safety**: Tool updates include corresponding documentation updates

### Pattern Categories
- **High-Impact**: Dependency caching, parallelization, Docker optimization
- **Medium-Impact**: Conditional execution, artifact optimization, environment setup
- **Confidence Scoring**: Clear guidelines for 0.2-1.0 confidence ranges

This ensures that recommendations are not only accurate but also reproducible and trustworthy.

## 🔧 Configuration

Create a `config.yml` file for advanced settings:

```yaml
github:
  token: "ghp_your_token_here"

ai:
  provider: "anthropic"
  api_key: "sk-ant-your_anthropic_key"

analysis:
  max_history_days: 30
  confidence_threshold: 0.7
```

## ❓ FAQ

**Q: Do I need an AI API key?**  
A: Yes, the tool uses AI analysis

**Q: What GitHub permissions do I need?**  
A: Only `repo:read` and `actions:read` permissions for the repositories you want to analyze.

**Q: Does this work with private repositories?**  
A: Yes, as long as your GitHub token has access to them.

**Q: How much does this save?**  
A: Typical users see 20-50% reduction in workflow run times and proportional cost savings.

## 🤖 Working with AI Assistants

This project includes `.ai_assistant_config.md` to help AI agents understand the project context and follow best practices.

**For developers using AI assistants (Claude, ChatGPT, etc.):**

Start your prompts with this header for better results:

```
Read .ai_assistant_config.md and follow all guidelines strictly before responding to:

<your question or request>
```

This ensures the AI understands the project's technology stack, coding standards, and mandatory file update requirements.

## 📊 Project Status

- ✅ **Core Analysis**: Basic workflow scanning and optimization detection
- ✅ **AI Integration**: Anthropic Claude powered recommendations  
- ✅ **CLI Interface**: Full command-line tool with reporting
- ✅ **CI/CD Pipeline**: Tag-triggered releases with automated changelog
- ✅ **AI Assistant Config**: Context file for better AI collaboration
- 🚧 **Auto-Apply**: Automatic PR generation (coming soon)
- 🚧 **Web Interface**: Browser-based analysis (planned)

*This project was created as part of a DevOps automation challenge to demonstrate practical AI applications in CI/CD optimization.* 