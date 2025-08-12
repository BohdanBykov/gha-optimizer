# Contributing to GHA-Optimizer

Thank you for your interest in contributing to GHA-Optimizer! This guide will help you get started with development and understand our contribution process.

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.9+
- GitHub account with personal access token
- Git

### **Development Setup**
```bash
# Clone the repository
git clone https://github.com/your-org/gha-optimizer.git
cd gha-optimizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Set up environment variables
cp .env.example .env
# Edit .env with your GitHub token
```

### **Configuration**
Create a `config.yml` file:
```yaml
github:
  token: "ghp_your_token_here"
  api_url: "https://api.github.com"
  
ai:
  provider: "openai"  # or "anthropic"
  api_key: "your_ai_api_key"
  model: "gpt-4"

analysis:
  max_history_days: 30
  confidence_threshold: 0.7
  parallel_requests: 5

output:
  default_format: "markdown"
  include_code_examples: true
  generate_pr_descriptions: true
```

## 🏗️ **Project Structure**

```
gha-optimizer/
├── src/gha_optimizer/
│   ├── __init__.py
│   ├── cli/                    # Command-line interface
│   │   ├── main.py
│   │   └── commands/
│   ├── collectors/             # Data collection from GitHub
│   │   ├── github_client.py
│   │   └── workflow_collector.py
│   ├── parsers/               # YAML and configuration parsing
│   │   ├── workflow_parser.py
│   │   └── yaml_analyzer.py
│   ├── analyzers/             # Pattern detection and analysis
│   │   ├── caching_analyzer.py
│   │   ├── parallel_analyzer.py
│   │   └── performance_analyzer.py
│   ├── ai/                    # AI-powered recommendations
│   │   ├── llm_client.py
│   │   └── recommendation_engine.py
│   ├── outputs/               # Report generation
│   │   ├── markdown_generator.py
│   │   ├── html_generator.py
│   │   └── pr_generator.py
│   ├── models/                # Data models
│   │   ├── workflow.py
│   │   └── optimization.py
│   └── utils/                 # Shared utilities
│       ├── github_utils.py
│       └── yaml_utils.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
├── examples/
└── scripts/
```

## 🧪 **Testing**

### **Running Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=gha_optimizer --cov-report=html

# Run specific test types
pytest tests/unit/
pytest tests/integration/

# Run tests with specific markers
pytest -m "not slow"  # Skip slow tests
pytest -m "api"       # Only API tests
```

### **Test Categories**
- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test component interactions
- **API Tests**: Test GitHub API integration
- **End-to-End Tests**: Test complete workflows

### **Writing Tests**
```python
import pytest
from unittest.mock import Mock, patch
from gha_optimizer.analyzers.caching_analyzer import CachingAnalyzer

class TestCachingAnalyzer:
    def test_detect_missing_npm_cache(self):
        """Test detection of missing npm caching."""
        workflow = Mock()
        workflow.jobs = [Mock()]
        workflow.jobs[0].steps = [
            {"run": "npm ci"},
            {"run": "npm test"}
        ]
        
        analyzer = CachingAnalyzer()
        opportunities = analyzer.detect_missing_cache(workflow)
        
        assert len(opportunities) == 1
        assert opportunities[0].type == "npm"
        assert opportunities[0].confidence > 0.8

    @patch('gha_optimizer.collectors.github_client.GitHubClient')
    def test_github_integration(self, mock_client):
        """Test GitHub API integration."""
        mock_client.return_value.get_workflows.return_value = []
        # Test implementation...
```

## 📝 **Code Standards**

### **Code Style**
We use the following tools for code quality:
- **Black**: Code formatting
- **isort**: Import sorting  
- **pylint**: Code analysis
- **mypy**: Type checking

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check code quality
pylint src/gha_optimizer/
mypy src/gha_optimizer/
```

### **Docstring Format**
```python
def analyze_workflow(workflow: Workflow, options: AnalysisOptions) -> List[Optimization]:
    """Analyze a workflow for optimization opportunities.
    
    Args:
        workflow: The workflow to analyze
        options: Analysis configuration options
        
    Returns:
        List of optimization recommendations
        
    Raises:
        AnalysisError: If workflow analysis fails
        
    Example:
        >>> workflow = Workflow.from_yaml(yaml_content)
        >>> options = AnalysisOptions(include_ai=True)
        >>> optimizations = analyze_workflow(workflow, options)
        >>> print(f"Found {len(optimizations)} optimizations")
    """
```

### **Commit Messages**
We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

feat(analyzers): add Docker optimization detection
fix(github): handle rate limiting gracefully  
docs(api): update endpoint documentation
test(integration): add GitHub API integration tests
refactor(parsers): simplify YAML parsing logic
```

## 🔧 **Development Workflow**

### **Adding New Features**

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement Feature**
   - Write code following our style guidelines
   - Add comprehensive tests
   - Update documentation
   - Add configuration options if needed

3. **Test Thoroughly**
   ```bash
   pytest
   pylint src/gha_optimizer/
   mypy src/gha_optimizer/
   ```

4. **Submit Pull Request**
   - Fill out the PR template
   - Link related issues
   - Request review from maintainers

### **Adding New Optimization Patterns**

To add a new optimization pattern:

1. **Create Analyzer Class**
   ```python
   # src/gha_optimizer/analyzers/your_analyzer.py
   from typing import List
   from ..models.workflow import Workflow
   from ..models.optimization import Optimization
   
   class YourAnalyzer:
       def analyze(self, workflow: Workflow) -> List[Optimization]:
           """Detect your optimization pattern."""
           # Implementation here
   ```

2. **Add Pattern Configuration**
   ```yaml
   # patterns/your_pattern.yml
   name: "Your Optimization Pattern"
   description: "Description of what this optimizes"
   detection_rules:
     - condition: "has_step_with_command('your-command')"
       action: "suggest_optimization"
   impact:
     time_savings: "2-5 minutes"
     confidence: 0.85
   ```

3. **Write Tests**
   ```python
   # tests/unit/analyzers/test_your_analyzer.py
   def test_your_pattern_detection():
       # Test implementation
   ```

4. **Update Documentation**
   ```markdown
   # docs/optimization-patterns.md
   ## Your New Optimization
   Description and examples...
   ```

### **Adding AI Recommendations**

To enhance AI recommendations:

1. **Update Prompt Templates**
   ```python
   # src/gha_optimizer/ai/prompts.py
   YOUR_OPTIMIZATION_PROMPT = """
   Analyze this GitHub Actions workflow for {pattern} opportunities:
   
   Workflow: {workflow_content}
   Context: {context}
   
   Provide specific recommendations with:
   1. Exact code changes
   2. Impact estimation
   3. Implementation difficulty
   """
   ```

2. **Enhance Recommendation Engine**
   ```python
   # src/gha_optimizer/ai/recommendation_engine.py
   def generate_your_recommendations(self, workflow: Workflow) -> List[Recommendation]:
       # AI-powered analysis implementation
   ```

## 🐛 **Bug Reports**

When reporting bugs, please include:

1. **Environment Information**
   - Python version
   - Operating system
   - GHA-Optimizer version

2. **Reproduction Steps**
   ```bash
   gha-optimizer analyze your-org/your-repo --verbose
   ```

3. **Expected vs Actual Behavior**

4. **Relevant Logs**
   ```
   DEBUG: Starting workflow analysis
   ERROR: Failed to parse workflow: invalid YAML
   ```

5. **Sample Repository** (if possible)

## 🚀 **Release Process**

### **Version Numbering**
We follow [Semantic Versioning](https://semver.org/):
- **Major**: Breaking changes
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes

## 🏆 **Recognition**

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Annual contributor spotlight
- Swag program for significant contributions

Thank you for contributing to GHA-Optimizer! 🎉 