# GHA-Optimizer Test Repository

This repository contains multiple GitHub Actions workflows designed to test different optimization patterns that GHA-Optimizer should detect and improve.

## 📁 **Workflow Files**

Each workflow demonstrates specific optimization opportunities:

### **Basic Patterns**
- **`basic-nodejs.yml`** - Missing Node.js dependency caching, sequential jobs
- **`basic-python.yml`** - Missing Python pip caching  
- **`basic-java.yml`** - Missing Maven dependency caching

### **Advanced Patterns**
- **`docker-build.yml`** - Missing Docker layer caching, inefficient builds
- **`runner-issues.yml`** - Over/under-provisioned runners
- **`conditional-problems.yml`** - Missing path-based triggers, inefficient conditions

### **Complex Scenarios**  
- **`full-pipeline.yml`** - Multiple optimization opportunities in one workflow
- **`artifact-issues.yml`** - Inefficient artifact handling
- **`matrix-problems.yml`** - Suboptimal matrix strategy usage

## 🎯 **Expected Detections**

GHA-Optimizer should identify and recommend fixes for:

- ✅ **Missing caching** (Node.js, Python, Maven, Docker)
- ✅ **Job parallelization** opportunities
- ✅ **Runner right-sizing** suggestions  
- ✅ **Conditional execution** improvements
- ✅ **Artifact optimization** recommendations
- ✅ **Docker build** optimizations

## 🧪 **Testing Commands**

```bash
# Basic scan
gha-optimizer scan your-username/gha-optimizer-test-repo

# AI-enhanced analysis  
gha-optimizer scan --ai-enhanced your-username/gha-optimizer-test-repo

# Apply optimizations (dry run)
gha-optimizer apply --dry-run your-username/gha-optimizer-test-repo
```

## 📊 **Expected Results**

Each workflow should trigger specific optimization recommendations with quantified impact estimates (time savings, cost reductions).