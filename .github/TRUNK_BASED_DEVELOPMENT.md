# Development Workflow

This project uses **trunk-based development** with automated CI/CD for fast, quality-focused development.

## 🎯 Key Points

- **Main branch only**: All development merges to `main`
- **Short-lived PRs**: Feature branches live < 24 hours  
- **Quality gates**: Automated checks prevent broken code
- **Fast releases**: Semantic versioning with conventional commits

## 🔄 CI Pipeline

### Pull Request Checks (`.github/workflows/ci.yml`)

Runs on every PR to `main`:

```yaml
on:
  pull_request:
    branches: [ main ]
```

**What runs:**
1. **Code Quality** - black, isort, flake8, mypy, bandit
2. **Integration Tests** - `python test_cli.py`
3. **Build & Install** - Package build and installation test

## 📦 Releases (`.github/workflows/release.yml`)

Two ways to create releases with automatic changelog:

**Option 1: Tag-triggered (Recommended)**
```bash
# Develop normally on main
git commit -m "feat: add new optimization pattern"
git commit -m "fix: handle edge case"
git push origin main

# Release when ready
git tag v0.2.0
git push origin v0.2.0  # 🚀 Triggers automatic release
```

**Option 2: Manual with version control**
```bash
# Go to GitHub Actions → Release → Run workflow
# Select: patch (0.1.0→0.1.1), minor (0.1.0→0.2.0), or major (0.1.0→1.0.0)
# Version calculated automatically - no arbitrary versions allowed
```

## 🛠️ Developer Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature

# 2. Make changes and commit
git commit -m "feat: your feature description"

# 3. Push and create PR
git push origin feature/your-feature
gh pr create

# 4. Merge after CI passes
gh pr merge --squash
```

## 🔧 Local Quality Checks

```bash
# Setup (once)
pre-commit install

# Run same checks as CI
python test_cli.py
black src/
isort src/ 
flake8 src/
mypy src/gha_optimizer
bandit -r src/gha_optimizer
```

## 📋 Branch Protection

Recommended settings for `main` branch:
- Require PR reviews
- Require status checks to pass
- Dismiss stale reviews
- Restrict pushes to `main`
