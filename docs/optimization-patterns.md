# Optimization Patterns

This document outlines the specific optimization patterns that GHA-Optimizer detects and the recommendations it provides.

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