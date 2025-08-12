# AI Analysis Response Schema

This document defines the structured data format returned by the AI analysis engine for workflow optimization recommendations.

## 📋 **Overview**

The AI analyzer returns optimization recommendations in a standardized JSON format that enables consistent processing, reporting, and automation across the GHA-Optimizer system.

## 🔧 **Response Schema**

### **Primary Schema Format**

```json
[
  {
    "title": "string",
    "type": "string", 
    "priority": "string",
    "workflow_file": "string",
    "job_name": "string",
    "description": "string",
    "impact_time_minutes": "number",
    "monthly_cost_savings": "number",
    "confidence_score": "number",
    "implementation_effort": "string",
    "implementation": "string",
    "code_example": "string"
  }
]
```

### **Field Definitions**

| Field | Type | Required | Description | Example Values |
|-------|------|----------|-------------|----------------|
| `title` | string | ✅ | Human-readable optimization name | "Add Node.js Dependency Caching" |
| `type` | string | ✅ | Optimization category | `"caching"`, `"parallelization"`, `"docker"`, `"runner-optimization"`, `"conditional"` |
| `priority` | string | ✅ | Implementation priority level | `"critical"`, `"high"`, `"medium"`, `"low"` |
| `workflow_file` | string | ✅ | Relative path to workflow file | `".github/workflows/ci.yml"` |
| `job_name` | string | ✅ | Specific job within workflow | `"build"`, `"test"`, `"deploy"` |
| `description` | string | ✅ | Detailed explanation of the issue | "Missing npm dependency caching causing 3-5 minute rebuilds on every run" |
| `impact_time_minutes` | number | ✅ | Time saved per workflow run | `3.5`, `12.0`, `0.5` |
| `monthly_cost_savings` | number | ✅ | Estimated monthly cost savings (USD) | `89.60`, `256.80`, `1200.00` |
| `confidence_score` | number | ✅ | AI confidence in recommendation (0.0-1.0) | `0.9`, `0.7`, `0.5` |
| `implementation_effort` | string | ✅ | Required effort to implement | `"low"`, `"medium"`, `"high"` |
| `implementation` | string | ✅ | High-level implementation steps | "Add actions/cache@v3 before npm ci step with path ~/.npm and key based on package-lock.json hash" |
| `code_example` | string | ✅ | Ready-to-use YAML code snippet | See code examples below |

## 🎯 **Optimization Types**

### **High-Impact Types**
- `"caching"` - Dependency caching (npm, pip, maven, gradle)
- `"parallelization"` - Job parallelization and matrix strategies  
- `"docker"` - Docker layer caching and BuildKit optimization
- `"runner-optimization"` - Right-sizing runners for workload

### **Medium-Impact Types**
- `"conditional"` - Path-based triggers and conditional execution
- `"artifact"` - Artifact upload/download optimization
- `"environment"` - Environment setup and shared caching

### **Other Types**
- `"security"` - Security best practices
- `"workflow-optimization"` - General workflow improvements
- `"triggers"` - Trigger optimization

## 🏷️ **Priority Levels**

| Priority | When to Use | Expected Savings |
|----------|-------------|------------------|
| `"critical"` | Security issues, major cost inefficiencies | > $500/month |
| `"high"` | Clear optimization wins, minimal effort | $100-500/month |
| `"medium"` | Good optimizations, moderate effort | $25-100/month |
| `"low"` | Nice-to-have improvements | < $25/month |

## 💡 **Implementation Effort**

| Effort | Definition | Examples |
|--------|------------|----------|
| `"low"` | Simple configuration changes | Adding cache actions, changing runner types |
| `"medium"` | Moderate refactoring required | Job restructuring, workflow splitting |
| `"high"` | Significant changes needed | Architecture changes, custom actions |

## 📝 **Complete Example**

```json
[
  {
    "title": "Add Node.js Dependency Caching",
    "type": "caching",
    "priority": "high",
    "workflow_file": ".github/workflows/ci.yml",
    "job_name": "build",
    "description": "Missing npm dependency caching causing 3-5 minute rebuilds on every run. The workflow runs 'npm ci' without any caching mechanism, forcing complete dependency downloads for each run.",
    "impact_time_minutes": 3.5,
    "monthly_cost_savings": 89.60,
    "confidence_score": 0.9,
    "implementation_effort": "low",
    "implementation": "Add actions/cache@v3 before npm ci step with path ~/.npm and key based on package-lock.json hash",
    "code_example": "- name: Cache Node.js dependencies\\n  uses: actions/cache@v3\\n  with:\\n    path: ~/.npm\\n    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}\\n    restore-keys: |\\n      ${{ runner.os }}-node-"
  },
  {
    "title": "Parallelize Test Suites",
    "type": "parallelization", 
    "priority": "high",
    "workflow_file": ".github/workflows/ci.yml",
    "job_name": "test",
    "description": "Unit tests, integration tests, and E2E tests are running sequentially in a single job. These test suites are independent and could run in parallel to reduce total pipeline time.",
    "impact_time_minutes": 12.0,
    "monthly_cost_savings": 384.00,
    "confidence_score": 0.8,
    "implementation_effort": "medium",
    "implementation": "Split test job into parallel unit-test, integration-test, and e2e-test jobs using matrix strategy",
    "code_example": "jobs:\\n  test:\\n    strategy:\\n      matrix:\\n        test-type: [unit, integration, e2e]\\n    steps:\\n      - name: Run ${{ matrix.test-type }} tests\\n        run: npm run test:${{ matrix.test-type }}"
  },
  {
    "title": "Optimize Docker Layer Caching",
    "type": "docker",
    "priority": "high", 
    "workflow_file": ".github/workflows/docker-build.yml",
    "job_name": "build-image",
    "description": "Docker builds are not using layer caching, causing full rebuilds even when only application code changes. BuildKit caching can significantly reduce build times.",
    "impact_time_minutes": 6.0,
    "monthly_cost_savings": 192.00,
    "confidence_score": 0.85,
    "implementation_effort": "low",
    "implementation": "Replace docker build with docker/build-push-action and enable GitHub Actions cache",
    "code_example": "- name: Build Docker image\\n  uses: docker/build-push-action@v4\\n  with:\\n    context: .\\n    push: true\\n    tags: myapp:latest\\n    cache-from: type=gha\\n    cache-to: type=gha,mode=max"
  },
  {
    "title": "Add Conditional Path Triggers",
    "type": "conditional",
    "priority": "medium",
    "workflow_file": ".github/workflows/docs.yml", 
    "job_name": "build-docs",
    "description": "Documentation workflow runs on all file changes, including code changes that don't affect documentation. Adding path filters would reduce unnecessary runs.",
    "impact_time_minutes": 2.0,
    "monthly_cost_savings": 64.00,
    "confidence_score": 0.7,
    "implementation_effort": "low", 
    "implementation": "Add paths filter to only trigger on documentation and configuration changes",
    "code_example": "on:\\n  push:\\n    paths:\\n      - 'docs/**'\\n      - '*.md'\\n      - 'mkdocs.yml'\\n  pull_request:\\n    paths:\\n      - 'docs/**'\\n      - '*.md'\\n      - 'mkdocs.yml'"
  }
]
```

## 🔄 **Schema Evolution**

This schema represents the current and only supported format. All AI responses are expected to conform to this structure, ensuring consistency and reliability across the system.

## 📊 **Cost Calculation Guidelines**

### **GitHub Actions Pricing (as of 2024)**
- `ubuntu-latest`: $0.008/minute
- `ubuntu-latest-4-cores`: $0.016/minute  
- `ubuntu-latest-8-cores`: $0.032/minute
- `windows-latest`: $0.016/minute
- `macos-latest`: $0.08/minute

### **Monthly Savings Formula**
```
monthly_savings = time_saved_minutes * runs_per_month * cost_per_minute
```

**Example:**
- Time saved: 3.5 minutes
- Runs per month: 320 (based on repository activity)
- Cost per minute: $0.008 (ubuntu-latest)
- Monthly savings: 3.5 × 320 × $0.008 = $8.96

## 🛠️ **Implementation Notes**

### **For AI Prompt Engineering**
- Always request JSON array format
- Include specific examples in prompts
- Validate response format before processing
- Provide fallback for parsing errors

### **For Report Generation**
- Use `type` field for categorization and emojis
- Sort by `priority` then `monthly_cost_savings`
- Display `confidence_score` for transparency
- Format `code_example` with proper YAML indentation

### **For PR Generation**
- Use `workflow_file` to target specific files
- Insert `code_example` at appropriate job/step location
- Reference `implementation` in PR description
- Tag PRs with `type` and `priority` labels

## 🔍 **Validation Rules**

- `confidence_score` must be between 0.0 and 1.0
- `impact_time_minutes` must be positive number  
- `monthly_cost_savings` must be positive number
- `type` must be from predefined list
- `priority` must be: critical, high, medium, or low
- `workflow_file` must start with `.github/workflows/`
- `code_example` should be valid YAML when unescaped

## 🎯 **Usage in Code**

### **Parsing AI Response**
```python
def parse_ai_recommendations(ai_response: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    processed = []
    for rec in ai_response:
        # Validate required fields
        if not all(key in rec for key in ['title', 'type', 'priority']):
            continue
            
        # Normalize numeric fields
        rec['impact_time_minutes'] = float(rec.get('impact_time_minutes', 0))
        rec['monthly_cost_savings'] = float(rec.get('monthly_cost_savings', 0))
        rec['confidence_score'] = float(rec.get('confidence_score', 0.5))
        
        processed.append(rec)
    
    return processed
```

### **Generating Reports**
```python
def format_recommendation(rec: Dict[str, Any]) -> str:
    return f"""
{rec['title']}
├─ Type: {rec['type']} 
├─ Priority: {rec['priority']}
├─ Impact: {rec['impact_time_minutes']:.1f} min/run
├─ Savings: ${rec['monthly_cost_savings']:.0f}/month
├─ Confidence: {rec['confidence_score']:.0%}
└─ Implementation: {rec['implementation']}
"""
```

---

*This schema ensures consistent, actionable optimization recommendations that can be easily processed, reported, and automated across the GHA-Optimizer system.*
