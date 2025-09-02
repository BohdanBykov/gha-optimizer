# Contributing to GHA-Optimizer

Thank you for your interest in contributing! This guide will help you get started with development.

## 🚀 Quick Development Setup

```bash
# Clone and setup
git clone https://github.com/BohdanBykov/gha-optimizer
cd gha-optimizer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install

# Run tests to verify setup
python test_cli.py
```

## 🧪 Testing Your Changes

```bash
# Run integration tests
python test_cli.py

# Run code quality checks (same as CI)
black src/
isort src/
flake8 src/
mypy src/gha_optimizer
bandit -r src/gha_optimizer
```

## 🤖 Using AI Assistants

This project includes `.ai_assistant_config.md` to help AI agents maintain code quality and consistency.

**When using AI assistants (Claude, ChatGPT, etc.), start your prompts with:**

```
Read .ai_assistant_config.md and follow all guidelines strictly before responding to:

<your development question>
```

This ensures the AI follows our:
- Technology stack constraints (Python 3.11+, Anthropic only)
- Coding standards and patterns
- File update requirements
- KISS principle for junior-friendly code

## 📝 Code Standards

We use these tools (same as CI):
- **black**: Code formatting  
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security scanning

## 🔧 Making Changes

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Follow the existing code style
- Add tests for new functionality
- Update documentation if needed

### 3. Test Your Changes
```bash
# Run the same checks as CI
python test_cli.py
black src/
isort src/
flake8 src/
mypy src/gha_optimizer
bandit -r src/gha_optimizer
```

### 4. Submit a Pull Request
- Use our [pull request template](.github/pull_request_template.md)
- Follow [Conventional Commits](https://www.conventionalcommits.org/) format
- Link any related issues

## 🚀 Release Process

### Automatic Releases (Recommended)
Releases are triggered by pushing tags:

```bash
# After features are merged to main
git checkout main
git pull origin main

# Update documentation versions before tagging
python scripts/update-docs-version.py

# Create and push tag to trigger release
git tag v0.2.0
git push origin v0.2.0
```

### Manual Releases (Maintainers)
Alternatively, use GitHub Actions with controlled version bumping:

```bash
# Go to GitHub Actions → Release → Run workflow
# Select release type: patch, minor, or major
# Version is calculated automatically from current version
```

Both methods automatically:
- Generate changelog from git commit messages
- Create GitHub release with changelog
- Build and upload packages  
- Update version in code

### Documentation Versioning

**Important**: All documentation must be version-aligned with releases:

```bash
# Before any release, update documentation versions
python scripts/update-docs-version.py
```

This ensures:
- `src/gha_optimizer/docs/optimization-patterns.md` references the correct version
- AI analyzer validates documentation version matches tool version  
- Users get consistent recommendations based on their tool version
- Version-specific documentation links work correctly

## 📚 Code Examples

### Adding a New Optimization Pattern
```python
# src/gha_optimizer/analyzers/your_analyzer.py
def detect_your_pattern(workflow_content: str) -> List[dict]:
    """Detect your optimization opportunity."""
    # Your detection logic here
    return recommendations
```

### Writing Tests
```python
# Test your new functionality
def test_your_feature():
    result = your_function("test input")
    assert result == "expected output"
```

## 🐛 Reporting Issues

When reporting bugs, include:
- Python version and OS
- Command you ran
- Error message or unexpected behavior
- Sample repository (if applicable)

## 🎯 Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/) format for automatic changelog generation:

```bash
feat: add caching optimization detection
fix: handle missing workflow files gracefully
docs: update installation instructions
test: add integration tests for GitHub API
chore: update dependencies to latest versions
```

**Why this matters:** Commit messages are automatically used to generate the changelog during releases.

Thank you for contributing! 🎉 