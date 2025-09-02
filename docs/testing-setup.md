# Testing Setup Guide

This guide helps you set up example repositories and API tokens for testing GHA-Optimizer functionality.

## 🏗️ **Step 1: Create Test Repository**

Create **one test repository** with multiple workflows demonstrating different optimization opportunities:

### **Repository: `gha-optimizer-test-repo`**
**Purpose**: Comprehensive collection of optimization patterns in multiple workflows

**Workflow Files** (copy from `test-repos/gha-optimizer-test-repo/`):
- **`basic-nodejs.yml`** - Missing Node.js caching, sequential jobs, duplicate setups
- **`basic-python.yml`** - Missing pip caching, duplicate dependency installs  
- **`basic-java.yml`** - Missing Maven caching, repeated setup
- **`docker-build.yml`** - Missing Docker layer caching, repeated builds
- **`runner-issues.yml`** - Over/under-provisioned runners, wrong OS selection
- **`conditional-problems.yml`** - Missing path triggers, inefficient conditions
- **`full-pipeline.yml`** - Complex workflow with multiple optimization opportunities

**Supporting Files**:
- **`package.json`** - Node.js dependencies and scripts
- **`requirements.txt`** - Python dependencies
- **`requirements-dev.txt`** - Python dev dependencies
- **`pom.xml`** - Maven configuration
- **`Dockerfile`** - Basic Docker configuration (with inefficiencies)
- **`Dockerfile.prod`** - Production Docker setup
- **`Dockerfile.dev`** - Development Docker setup

## 🔑 **Step 2: GitHub API Token Setup**

### **Create Personal Access Token**

1. **Go to GitHub Settings**:
   - Navigate to GitHub.com → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Generate New Token**:
   - Click "Generate new token (classic)"
   - Name: `gha-optimizer-testing`
   - Expiration: 90 days (or as needed)

3. **Required Permissions**:
   ```
   ✅ repo (Full control of private repositories)
     ✅ repo:status (Access commit status)
     ✅ repo_deployment (Access deployment status) 
     ✅ public_repo (Access public repositories)
     ✅ repo:invite (Access repository invitations)
   
   ✅ workflow (Update GitHub Action workflows)
   
   ✅ read:org (Read org and team membership, read org projects)
   ```

4. **Copy Token**:
   ```bash
   # Save your token (starts with ghp_)
   ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### **Set Environment Variable**

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc)
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Reload shell or run:
source ~/.bashrc
```

### **Test GitHub Token**

```bash
# Test API access
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/user

# Test workflow access
curl -H "Authorization: token $GITHUB_TOKEN" \
     https://api.github.com/repos/your-username/gha-optimizer-test-basic/actions/workflows
```

## 🤖 **Step 3: AI API Token Setup**

### **Anthropic Claude Setup**

1. **Create Anthropic Account**:
   - Go to https://console.anthropic.com/
   - Sign up or log in

2. **Generate API Key**:
   - Navigate to API Keys section
   - Create new API key
   - Name: `gha-optimizer-testing`
   - Copy the key (starts with `sk-ant-`)

3. **Set Environment Variable**:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   # Add to shell profile for persistence
   echo 'export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Test Anthropic API**:
   ```bash
   curl -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"model": "claude-3-5-sonnet-20241022", "max_tokens": 10, "messages": [{"role": "user", "content": "Hello!"}]}' \
        https://api.anthropic.com/v1/messages
   ```

1. **Create Anthropic Account**:
   - Go to https://console.anthropic.com/
   - Sign up for API access

2. **Generate API Key**:
   - Get API key from dashboard
   - Copy the key

3. **Set Environment Variable**:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   # Add to shell profile
   echo 'export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' >> ~/.bashrc
   source ~/.bashrc
   ```

## 🧪 **Step 4: Test Configuration**

### **Create Test Config File**

```bash
# Create config file
cat > gha-optimizer/test-config.yml << EOF
github:
  token: "${GITHUB_TOKEN}"
  api_url: "https://api.github.com"

ai:
  provider: "anthropic"
  api_key: "${ANTHROPIC_API_KEY}"
  model: "claude-3-5-sonnet-20241022"

analysis:
  max_history_days: 30
  confidence_threshold: 0.7
  parallel_requests: 3

output:
  default_format: "markdown"
  include_code_examples: true
  generate_pr_descriptions: true
EOF
```

### **Test CLI with Real Repository**

```bash
# Navigate to project
cd gha-optimizer

# Test scan command with your test repository
gha-optimizer --config test-config.yml scan your-username/gha-optimizer-test-repo

# Test with debug options
gha-optimizer --config test-config.yml scan your-username/gha-optimizer-test-repo --local-docs --output-prompt-file debug.txt

# Test apply command (dry run)  
gha-optimizer --config test-config.yml apply --dry-run your-username/gha-optimizer-test-repo
```

## 🎯 **Expected Optimization Opportunities**

Based on our test repository workflows, GHA-Optimizer should detect:

### **From `basic-nodejs.yml`**:
- ✅ Missing Node.js dependency caching
- ✅ Sequential jobs that could be parallelized 
- ✅ Duplicate setup work across jobs
- ✅ Inefficient artifact uploads

### **From `basic-python.yml`**:
- ✅ Missing pip dependency caching
- ✅ Redundant dependency installs in matrix strategy
- ✅ Duplicate Python setup across jobs

### **From `basic-java.yml`**:
- ✅ Missing Maven dependency caching
- ✅ Repeated Maven setup without optimization

### **From `docker-build.yml`**:
- ✅ Missing Docker layer caching
- ✅ Multiple image builds without layer reuse
- ✅ Redundant image building across jobs

### **From `runner-issues.yml`**:
- ✅ Over-provisioned runners (8-cores for linting)
- ✅ Under-provisioned runners (basic for heavy builds)
- ✅ Wrong OS selection (Linux for Windows tasks)

### **From `conditional-problems.yml`**:
- ✅ Missing path-based triggers
- ✅ Workflows running on irrelevant changes
- ✅ Branch-specific jobs running on all branches

### **From `full-pipeline.yml`**:
- ✅ Multiple optimization issues in one workflow
- ✅ Sequential dependencies that could be parallel
- ✅ Repeated setups without caching
- ✅ Resource misallocation across jobs

## 🔍 **Test Scenarios**

### **Scenario 1: Basic Pattern Detection**
```bash
# Should detect caching and parallelization opportunities across all workflows
gha-optimizer scan your-username/gha-optimizer-test-repo
```

**Expected Output**:
- Node.js, Python, and Maven caching recommendations
- Job parallelization suggestions
- Runner optimization recommendations
- Time/cost savings estimates

### **Scenario 2: Debug Mode Analysis**
```bash
# Should use local documentation and save debug information
gha-optimizer scan your-username/gha-optimizer-test-repo --local-docs --output-prompt-file debug.txt --output-ai-response response.json
```

**Expected Output**:
- Debug files with prompt and AI response data
- Local documentation usage confirmation in logs
- Complete analysis with same quality as remote mode
- Detailed optimization explanations for each workflow

## 🚀 **Next Steps**

Once you have the test repositories and API tokens set up:

1. **Verify CLI works** with placeholder data
2. **Test GitHub API integration** with real workflow data
3. **Test AI API integration** with actual recommendations
4. **Implement real workflow parsing** based on test data
5. **Build pattern detection engines** using test scenarios

Ready to start implementing the actual workflow analysis logic! 🔧