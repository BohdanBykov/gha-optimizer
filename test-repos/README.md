# Test Repository Templates

This directory contains template files for creating example GitHub repositories to test GHA-Optimizer functionality.

## 📁 **Repository Templates**

### **gha-optimizer-test-basic**
Basic optimization patterns including:
- Missing Node.js dependency caching
- Sequential jobs that could be parallelized
- Suboptimal runner usage

### **gha-optimizer-test-docker**
Docker-specific optimizations including:
- Missing Docker layer caching
- Inefficient Dockerfile structure

### **gha-optimizer-test-complex**
Complex workflow patterns including:
- Over-provisioned runners
- Missing conditional path triggers
- Inefficient artifact uploads
- Multiple optimization opportunities

### **gha-optimizer-test-python**
Python-specific patterns including:
- Missing pip dependency caching
- Redundant setup across matrix jobs

## 🚀 **How to Use**

1. **Create new GitHub repositories** with these names
2. **Copy template files** from each directory to your repositories
3. **Push to GitHub** to trigger workflows
4. **Test GHA-Optimizer** against these repositories

## 📋 **Setup Checklist**

- [ ] Create GitHub repositories
- [ ] Copy template files
- [ ] Set up GitHub API token
- [ ] Set up AI API token (OpenAI/Anthropic)
- [ ] Test CLI commands

See [testing-setup.md](../docs/testing-setup.md) for detailed setup instructions.