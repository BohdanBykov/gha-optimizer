# Optimization Patterns

**Version:** 1.3.0
**Last Updated:** September 2025
**Repository:** https://github.com/BohdanBykov/gha-optimizer

This document serves as the authoritative reference for GitHub Actions workflow optimization patterns detected by GHA-Optimizer. It provides specific patterns, implementation examples, impact calculations, and confidence scoring guidelines that the AI analyzer uses to generate accurate recommendations.

## 📋 **Documentation Purpose**

This document is directly referenced by the AI analyzer to ensure:
- **Consistent recommendations** across analysis runs
- **Accurate impact calculations** based on real-world data  
- **Version-aligned guidance** that matches tool capabilities
- **Reliable confidence scoring** based on pattern clarity

> **Note**: This documentation is version-controlled and linked to specific GHA-Optimizer releases. Always reference the documentation version that matches your tool version for accurate analysis.

## 🚀 **High-Impact Optimizations**

### 1. **Dependency Caching**

**Pattern Detection**: Missing or suboptimal caching for package managers

#### **Node.js Dependencies**
```yaml
# ❌ BEFORE: No caching
- name: Install dependencies
  run: npm ci

# ✅ AFTER: With caching
- name: Cache Node.js dependencies
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-

- name: Install dependencies
  run: npm ci
```

**Impact**: 2-5 minutes saved per run, ~$50-150/month cost reduction

#### **Python Dependencies**
```yaml
# ❌ BEFORE: No caching
- name: Install dependencies
  run: pip install -r requirements.txt

# ✅ AFTER: With caching
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-

- name: Install dependencies
  run: pip install -r requirements.txt
```

#### **Maven/Gradle Dependencies**
```yaml
# ❌ BEFORE: No caching
- name: Build with Maven
  run: mvn clean compile

# ✅ AFTER: With caching
- name: Cache Maven dependencies
  uses: actions/cache@v3
  with:
    path: ~/.m2
    key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
    restore-keys: |
      ${{ runner.os }}-m2-

- name: Build with Maven
  run: mvn clean compile
```

### 2. **Job Parallelization**

**Pattern Detection**: Sequential jobs that could run in parallel

#### **Test Suite Optimization**
```yaml
# ❌ BEFORE: Sequential testing
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Unit tests
        run: npm run test:unit
      - name: Integration tests
        run: npm run test:integration
      - name: E2E tests
        run: npm run test:e2e

# ✅ AFTER: Parallel testing
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Unit tests
        run: npm run test:unit
        
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Integration tests
        run: npm run test:integration
        
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: E2E tests
        run: npm run test:e2e
```

**Impact**: 40-60% reduction in total pipeline time

#### **Multi-Environment Builds**
```yaml
# ❌ BEFORE: Sequential builds
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16, 18, 20]
    steps:
      - uses: actions/checkout@v3
      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v3
        with:
          node-version: ${{ matrix.node-version }}

# ✅ AFTER: Already optimized with matrix strategy
# AI suggests: "Your matrix strategy is well-implemented!"
```

### 3. **Docker Optimization**

**Pattern Detection**: Inefficient Docker builds and missing layer caching

#### **Docker Layer Caching**
```yaml
# ❌ BEFORE: No Docker caching
- name: Build Docker image
  run: docker build -t myapp .

# ✅ AFTER: With BuildKit caching
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v2

- name: Build and push Docker image
  uses: docker/build-push-action@v4
  with:
    context: .
    push: true
    tags: myapp:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Impact**: 3-8 minutes saved per build, especially for large images

### 4. **Runner Optimization**

**Pattern Detection**: Suboptimal runner selection for workload

#### **Right-sizing Runners**
```yaml
# ❌ BEFORE: Over-provisioned for simple tasks
jobs:
  lint:
    runs-on: ubuntu-latest-8-cores  # Expensive for linting
    steps:
      - name: Lint code
        run: npm run lint

# ✅ AFTER: Appropriate sizing
jobs:
  lint:
    runs-on: ubuntu-latest  # Sufficient for linting
    
  build:
    runs-on: ubuntu-latest-4-cores  # Right-sized for builds
```

**Cost Analysis**:
- `ubuntu-latest`: $0.008/minute
- `ubuntu-latest-4-cores`: $0.016/minute  
- `ubuntu-latest-8-cores`: $0.032/minute

## ⚡ **Medium-Impact Optimizations**

### 5. **Artifact Optimization**

#### **Selective Artifact Upload**
```yaml
# ❌ BEFORE: Upload everything
- name: Upload artifacts
  uses: actions/upload-artifact@v3
  with:
    name: build-files
    path: .

# ✅ AFTER: Upload only necessary files
- name: Upload build artifacts
  uses: actions/upload-artifact@v3
  with:
    name: build-files
    path: |
      dist/
      build/
      !**/*.map
      !**/node_modules
```

### 6. **Conditional Execution**

#### **Path-based Triggers**
```yaml
# ❌ BEFORE: Run on all changes
on:
  push:
  pull_request:

# ✅ AFTER: Run only when relevant files change
on:
  push:
    paths:
      - 'src/**'
      - 'package*.json'
      - '.github/workflows/**'
  pull_request:
    paths:
      - 'src/**'
      - 'package*.json'
```

### 7. **Environment Optimization**

#### **Skip Redundant Setup**
```yaml
# ❌ BEFORE: Redundant setup steps
jobs:
  test:
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm test
      
  build:
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3  # Duplicate setup
      - run: npm ci                  # Duplicate install
      - run: npm run build

# ✅ AFTER: Shared setup job
jobs:
  setup:
    outputs:
      cache-hit: ${{ steps.cache.outputs.cache-hit }}
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - id: cache
        uses: actions/cache@v3
        # ... cache configuration
      - if: steps.cache.outputs.cache-hit != 'true'
        run: npm ci
        
  test:
    needs: setup
    steps:
      - uses: actions/checkout@v3
      - run: npm test
      
  build:
    needs: setup
    steps:
      - uses: actions/checkout@v3
      - run: npm run build
```

## 🔍 **Advanced Optimizations**

### 8. **Smart Test Selection**

#### **Test Impact Analysis**
```yaml
# AI Recommendation: Implement test impact analysis
- name: Run affected tests only
  run: |
    # Get changed files
    CHANGED_FILES=$(git diff --name-only HEAD~1)
    
    # Run tests for affected modules only
    npm run test:affected -- $CHANGED_FILES
```

### 9. **Workflow Dependencies**

#### **Optimized Workflow Chains**
```yaml
# ❌ BEFORE: Monolithic workflow
name: CI/CD
on: [push]
jobs:
  everything:  # Single huge job
    steps: [test, build, deploy, notify, cleanup]

# ✅ AFTER: Optimized workflow separation
# .github/workflows/ci.yml - Fast feedback
name: CI
on: [push, pull_request]

# .github/workflows/cd.yml - Deployment
name: CD
on:
  workflow_run:
    workflows: ["CI"]
    types: [completed]
    branches: [main]
```

### 10. **Resource Monitoring**

#### **Performance Tracking**
```yaml
# AI Recommendation: Add performance monitoring
- name: Track build performance
  run: |
    echo "::notice::Build started at $(date)"
    START_TIME=$(date +%s)
    
    # Your build commands here
    npm run build
    
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    echo "::notice::Build completed in ${DURATION} seconds"
```

## 📊 **Pattern Detection Logic**

### **Caching Detection Algorithm**
```python
def detect_missing_cache(workflow: Workflow) -> List[CacheOpportunity]:
    opportunities = []
    
    for job in workflow.jobs:
        # Check for package manager commands without caching
        if has_npm_install(job) and not has_npm_cache(job):
            opportunities.append(CacheOpportunity(
                type="npm",
                estimated_savings="2-4 minutes",
                confidence=0.9
            ))
            
        if has_pip_install(job) and not has_pip_cache(job):
            opportunities.append(CacheOpportunity(
                type="pip",
                estimated_savings="1-3 minutes", 
                confidence=0.85
            ))
    
    return opportunities
```

### **Parallelization Detection**
```python
def detect_parallelization_opportunities(workflow: Workflow) -> List[ParallelOpportunity]:
    opportunities = []
    
    # Find jobs that could run in parallel
    dependency_graph = build_dependency_graph(workflow)
    independent_jobs = find_independent_sequential_jobs(dependency_graph)
    
    if len(independent_jobs) > 1:
        opportunities.append(ParallelOpportunity(
            jobs=independent_jobs,
            estimated_time_savings=calculate_parallel_savings(independent_jobs),
            confidence=0.8
        ))
    
    return opportunities
```

## 🎯 **Impact Calculation**

### **Time Savings Formula**
```python
def calculate_time_savings(optimization: Optimization) -> TimeSavings:
    base_time = get_average_workflow_time(workflow)
    
    savings = {
        "caching": min(base_time * 0.3, timedelta(minutes=5)),
        "parallelization": base_time * 0.4,
        "runner_optimization": base_time * 0.15,
        "docker_caching": min(base_time * 0.5, timedelta(minutes=8))
    }
    
    return savings.get(optimization.type, timedelta(0))
```

### **Cost Savings Formula**
```python
def calculate_cost_savings(time_saved: timedelta, runner_type: str, runs_per_month: int) -> float:
    runner_costs = {
        "ubuntu-latest": 0.008,
        "ubuntu-latest-4-cores": 0.016,
        "ubuntu-latest-8-cores": 0.032
    }
    
    cost_per_minute = runner_costs.get(runner_type, 0.008)
    minutes_saved = time_saved.total_seconds() / 60
    
    return minutes_saved * cost_per_minute * runs_per_month
```

## 🎯 **Confidence Scoring Guidelines**

The AI analyzer must assign confidence scores based on these criteria:

### **High Confidence (0.8-1.0)**
- **Missing dependency caching**: Clear package manager commands without cache actions
- **Obviously inefficient runners**: 8-core runners for linting/formatting
- **Clear parallelization opportunities**: Independent test suites running sequentially
- **Missing Docker layer caching**: Standard `docker build` commands

### **Medium Confidence (0.6-0.8)**  
- **Potential parallelization**: Jobs with unclear dependencies
- **Runner right-sizing**: Workload assessment based on step types
- **Conditional execution**: Workflows triggering on all file changes
- **Artifact optimization**: Large artifact uploads without specific paths

### **Low Confidence (0.4-0.6)**
- **Complex workflow dependencies**: Unclear if parallelization is safe
- **Advanced optimizations**: Smart test selection, custom caching strategies
- **Environment-specific optimizations**: Dependent on repository context

### **Very Low Confidence (0.2-0.4)**
- **Speculative optimizations**: Based on limited workflow context
- **Repository-dependent patterns**: Requiring deep knowledge of codebase
- **Complex CI/CD patterns**: Multiple workflow interactions

## 📊 **Impact Calculation Standards**

### **Time Savings (Minutes per Run)**

#### **Dependency Caching**
- **Node.js (npm/yarn)**: 2-5 minutes for medium projects, 5-10 for large
- **Python (pip)**: 1-3 minutes for typical projects, 3-6 for ML/data science
- **Java (Maven)**: 3-8 minutes for enterprise projects
- **Docker builds**: 3-15 minutes depending on image complexity

#### **Parallelization**
- **Test suites**: 40-60% time reduction (measure against longest single job)
- **Matrix builds**: Already optimal if properly configured
- **Independent jobs**: Sum of all parallelizable jobs minus longest

#### **Runner Optimization**
- **Over-provisioned**: 15-30% cost reduction with minimal time impact
- **Under-provisioned**: 20-40% time reduction for compute-heavy workloads

### **Monthly Cost Calculation**
```
Monthly Savings = (Minutes Saved × Runs per Week × 4.33 × Cost per Minute)

Where:
- Minutes Saved: Based on pattern-specific estimates above
- Runs per Week: Repository activity (use 50 as conservative default)
- Cost per Minute: Runner-type specific ($0.008 for ubuntu-latest)
```



## 🔍 **Pattern Detection Specificity**

### **Exact Pattern Matches (High Confidence)**
```yaml
# Missing Node.js caching - DEFINITIVE PATTERN
- name: Install dependencies
  run: npm ci  # or npm install, yarn install
# Missing: actions/cache step before this

# Missing Python caching - DEFINITIVE PATTERN  
- name: Install dependencies
  run: pip install -r requirements.txt
# Missing: actions/cache step before this
```

### **Contextual Pattern Matches (Medium Confidence)**
```yaml
# Sequential test jobs - PROBABLE PATTERN
jobs:
  unit-test:
    steps: [checkout, setup, test-unit]
  integration-test:
    needs: unit-test  # This dependency may be unnecessary
    steps: [checkout, setup, test-integration]
```

### **Complex Pattern Analysis (Lower Confidence)**
```yaml
# Complex workflow dependencies - UNCERTAIN PATTERN
jobs:
  job-a:
    steps: [checkout, build-artifact]
  job-b: 
    needs: job-a  # May or may not need the artifact
    steps: [checkout, different-task]
```

## 📝 **Recommendation Template**

All AI recommendations must follow this exact structure:

```json
{
  "title": "Descriptive action-oriented title",
  "type": "caching|parallelization|runner|docker|conditional|artifact|environment",
  "priority": "high|medium|low",
  "workflow_file": "exact file path from workflow input",
  "job_name": "specific job name or 'multiple'",
  "line_number": "exact line number where optimization applies",
  "description": "Clear explanation of current inefficiency and impact",
  "impact_time_minutes": "realistic time savings based on guidelines above",
  "monthly_cost_savings": "calculated using standard formula",
  "confidence_score": "0.0-1.0 based on pattern clarity guidelines",
  "implementation": "Step-by-step implementation description",
  "code_example": "Complete YAML code ready to copy-paste"
}
```

## 🚨 **Critical Analysis Requirements**

1. **Line Number Accuracy**: Always provide exact line numbers relative to workflow file start
2. **Cost Validation**: All cost calculations must pass validation logic  
3. **Pattern Specificity**: Only recommend optimizations with clear pattern matches
4. **Implementation Readiness**: Code examples must be immediately usable
5. **Confidence Honesty**: Use conservative confidence scores when uncertain

This documentation ensures that AI analysis provides consistent, accurate, and actionable optimization recommendations that users can trust and implement immediately. 