"""AI-powered workflow analyzer using existing optimization patterns."""

import json
import logging
import re
import time
from functools import lru_cache
from typing import Dict, List, Optional, Any

from ..utils.config import Config
from ..utils.helpers import validate_cost_calculation, calculate_github_actions_cost


class AIWorkflowAnalyzer:
    """AI-powered analyzer for GitHub Actions workflows using predefined optimization patterns."""
    
    def __init__(self, config: Config, logger: Optional[logging.Logger] = None) -> None:
        """Initialize AI analyzer."""
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Validate AI configuration
        if not self.config.ai_api_key:
            raise ValueError("AI API key is required for analysis")
        
        self.logger.info(f"Initialized AI analyzer with {self.config.ai_provider} ({self.config.ai_model})")
    
    def analyze_workflows(
        self, 
        workflows: Dict[str, str], 
        repository_stats: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Analyze workflows using AI based on optimization patterns from docs.
        
        Args:
            workflows: Dictionary mapping file paths to raw YAML content
            repository_stats: Statistics from GitHub API
            
        Returns:
            List of optimization opportunities (compatible with existing format)
        """
        self.logger.info(f"Starting AI analysis of {len(workflows)} workflows")
        
        # For demo purposes, limit to first 3 workflows
        if len(workflows) > 3:
            self.logger.info(f"Demo mode: limiting analysis to first 3 workflows out of {len(workflows)}")
            workflow_items = list(workflows.items())[:3]
            workflows = dict(workflow_items)
        
        # Build comprehensive prompt with all workflows and IDs
        prompt = self._build_multi_workflow_prompt(workflows, repository_stats)
        
        # Single AI API call for all workflows
        ai_response = self._call_ai_api(prompt)
        
        # Convert AI response to existing recommendation format
        recommendations = self._parse_ai_recommendations(ai_response, repository_stats, workflows)
        
        self.logger.info(f"AI analysis completed. Found {len(recommendations)} optimization opportunities")
        return recommendations
    
    def _build_multi_workflow_prompt(self, workflows: Dict[str, str], repository_stats: Dict[str, Any]) -> str:
        """Build single prompt with all workflows using IDs for cost efficiency."""
        
        # Get optimization patterns
        optimization_patterns = self._get_optimization_patterns_from_docs()
        
        # Calculate estimated runs per week for impact calculation
        runs_per_week = repository_stats.get('runs_count', 0) * 7 / repository_stats.get('analysis_days', 30)
        
        # Build workflows section with IDs
        workflows_section = []
        workflow_ids = {}
        
        for idx, (workflow_path, workflow_content) in enumerate(workflows.items(), 1):
            workflow_id = f"WF{idx:02d}"
            workflow_ids[workflow_id] = workflow_path
            numbered_yaml = self._add_line_numbers_to_yaml(workflow_content)
            
            workflows_section.append(f"""
### Workflow {workflow_id}: `{workflow_path}`
```yaml
{numbered_yaml}
```""")
        
        workflows_text = "\n".join(workflows_section)
        
        return f"""You are an expert GitHub Actions optimization analyst. Analyze ALL workflows below for optimization opportunities.

## Repository Context
- **Repository**: {repository_stats.get('repository', {}).get('full_name', 'Unknown')}
- **Language**: {repository_stats.get('repository', {}).get('language', 'Unknown')}
- **Activity**: {repository_stats.get('runs_count', 0)} runs in {repository_stats.get('analysis_days', 30)} days (~{runs_per_week:.0f}/week)
- **Total Workflows**: {len(workflows)}

{optimization_patterns}

## Workflows to Analyze
{workflows_text}

## Critical Instructions

### 1. Workflow Identification
- Each workflow has an ID (WF01, WF02, etc.) and file path
- Use the exact workflow_file path in your response
- Reference the correct workflow ID when analyzing

### 2. Line Number Requirements
- **MANDATORY**: Provide exact line numbers relative to each workflow file start
- Be precise - reference the actual line where optimization applies
- Example: If optimization is on line 25 of WF02, use "25" (not cumulative line number)

### 3. Impact Calculation
- Time savings per run (realistic minutes)
- Monthly cost: $0.008/minute × time_saved × {runs_per_week:.0f} runs/week × 4.33 weeks
- Implementation effort: low/medium/high
- Confidence: 0.0-1.0 based on pattern clarity

### 4. Required Output
Return ONLY a JSON array with ALL optimizations found across ALL workflows:

```json
[
  {{
    "title": "Add Node.js Dependency Caching",
    "type": "caching",
    "priority": "high",
    "workflow_file": ".github/workflows/ci.yml",
    "job_name": "build", 
    "line_number": "47",
    "description": "Missing npm dependency caching causing repeated installs",
    "impact_time_minutes": 3.0,
    "monthly_cost_savings": 31.19,
    "confidence_score": 0.9,
    "implementation_effort": "low",
    "implementation": "Add actions/cache@v3 before npm install",
    "code_example": "- uses: actions/cache@v3\\n  with:\\n    path: ~/.npm\\n    key: ${{{{ runner.os }}}}-node-${{{{ hashFiles('package-lock.json') }}}}"
  }}
]
```
"""
    
    def _call_ai_api(self, prompt: str) -> List[Dict[str, Any]]:
        """Call AI API with real implementation for OpenAI or Anthropic."""
        self.logger.debug(f"Calling {self.config.ai_provider} API with {self.config.ai_model}")
        
        try:
            if self.config.ai_provider == "openai":
                return self._call_openai_api(prompt)
            elif self.config.ai_provider == "anthropic":
                return self._call_anthropic_api(prompt)
            else:
                raise ValueError(f"Unsupported AI provider: {self.config.ai_provider}")
                
        except Exception as e:
            self.logger.error(f"AI API call failed: {e}")
            # Return fallback analysis based on simple pattern matching
            return self._fallback_pattern_analysis(prompt)
    
    def _call_openai_api(self, prompt: str) -> List[Dict[str, Any]]:
        """Call OpenAI API for workflow analysis with simple retry logic."""
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                import openai
                client = openai.OpenAI(api_key=self.config.ai_api_key)
                
                self.logger.debug(f"Making OpenAI API request (attempt {attempt + 1}/{max_retries})")
                response = client.chat.completions.create(
                    model=self.config.ai_model,
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are a GitHub Actions optimization expert. Always return valid JSON arrays with optimization recommendations."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=0.3,  # Lower temperature for more consistent results
                    max_tokens=4000
                )
                
                content = response.choices[0].message.content.strip()
                self.logger.debug(f"OpenAI response length: {len(content)} characters")
                
                # Parse JSON response
                # Extract JSON from markdown code blocks if present
                json_content = self._extract_json_from_response(content)
                recommendations = json.loads(json_content)
                if not isinstance(recommendations, list):
                    self.logger.warning("OpenAI returned non-list response, wrapping in list")
                    recommendations = [recommendations]
                    
                return recommendations
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse OpenAI JSON response: {e}")
                raise  # Don't retry JSON parse errors
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    self.logger.error(f"OpenAI API error after {max_retries} attempts: {e}")
                    raise
                else:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(f"OpenAI API error (attempt {attempt + 1}): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
    
    def _call_anthropic_api(self, prompt: str) -> List[Dict[str, Any]]:
        """Call Anthropic Claude API for workflow analysis with simple retry logic."""
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=self.config.ai_api_key)
                
                self.logger.debug(f"Making Anthropic API request (attempt {attempt + 1}/{max_retries})")
                response = client.messages.create(
                    model=self.config.ai_model,
                    max_tokens=4000,
                    temperature=0.3,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                content = response.content[0].text.strip()
                self.logger.debug(f"Anthropic response length: {len(content)} characters")
                self.logger.debug(f"Anthropic response content: {repr(content[:500])}")
                
                # Parse JSON response
                if not content:
                    self.logger.warning("Anthropic returned empty response")
                    return []
                
                # Extract JSON from markdown code blocks if present
                json_content = self._extract_json_from_response(content)
                recommendations = json.loads(json_content)
                if not isinstance(recommendations, list):
                    self.logger.warning("Anthropic returned non-list response, wrapping in list")
                    recommendations = [recommendations]
                    
                return recommendations
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse Anthropic JSON response: {e}")
                raise  # Don't retry JSON parse errors
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt
                    self.logger.error(f"Anthropic API error after {max_retries} attempts: {e}")
                    raise
                else:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(f"Anthropic API error (attempt {attempt + 1}): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
    
    def _fallback_pattern_analysis(self, prompt: str) -> List[Dict[str, Any]]:
        """Fallback pattern-based analysis when AI API fails."""
        self.logger.warning("Using fallback pattern analysis due to AI API failure")
        
        # Extract workflows from prompt
        workflow_pattern = r"FILE: (.+?)\n```yaml\n(.*?)\n```"
        workflows = re.findall(workflow_pattern, prompt, re.DOTALL)
        
        recommendations = []
        
        for file_path, workflow_content in workflows:
            # Simple pattern detection
            if "npm ci" in workflow_content and "actions/cache" not in workflow_content:
                recommendations.append({
                    "title": "Add Node.js Dependency Caching",
                    "type": "caching",
                    "priority": "high",
                    "workflow_file": file_path,
                    "job_name": "build",
                    "description": "Missing npm dependency caching detected",
                    "impact_time_minutes": 3.0,
                    "monthly_cost_savings": 75.0,
                    "confidence_score": 0.8,
                    "implementation_effort": "low",
                    "implementation": "Add actions/cache@v3 for npm dependencies",
                    "code_example": "- name: Cache Node.js dependencies\\n  uses: actions/cache@v3\\n  with:\\n    path: ~/.npm\\n    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}"
                })
            
            if "pip install" in workflow_content and "actions/cache" not in workflow_content:
                recommendations.append({
                    "title": "Add Python Dependency Caching",
                    "type": "caching", 
                    "priority": "high",
                    "workflow_file": file_path,
                    "job_name": "test",
                    "description": "Missing pip dependency caching detected",
                    "impact_time_minutes": 2.5,
                    "monthly_cost_savings": 60.0,
                    "confidence_score": 0.8,
                    "implementation_effort": "low",
                    "implementation": "Add actions/cache@v3 for pip dependencies",
                    "code_example": "- name: Cache pip dependencies\\n  uses: actions/cache@v3\\n  with:\\n    path: ~/.cache/pip\\n    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}"
                })
        
        return recommendations
    
    @lru_cache(maxsize=1)
    def _get_optimization_patterns_from_docs(self) -> str:
        """Return comprehensive optimization patterns based on documentation.
        
        Cached since this is expensive string processing that doesn't change.
        """
        return """
OPTIMIZATION PATTERNS TO DETECT:

## 1. HIGH-IMPACT OPTIMIZATIONS

### DEPENDENCY CACHING
**Node.js Dependencies:**
- Pattern: Look for "npm ci", "npm install", "yarn install" WITHOUT preceding actions/cache step
- Implementation: Add actions/cache@v3 with path ~/.npm and key based on package-lock.json
- Impact: 2-5 minutes saved per run, ~$50-150/month cost reduction

**Python Dependencies:**  
- Pattern: Look for "pip install" WITHOUT preceding actions/cache step
- Implementation: Add actions/cache@v3 with path ~/.cache/pip and key based on requirements.txt
- Impact: 1-3 minutes saved per run

**Maven/Gradle Dependencies:**
- Pattern: Look for "mvn", "gradle" commands WITHOUT cache
- Implementation: Add actions/cache@v3 with path ~/.m2 or ~/.gradle
- Impact: 3-8 minutes saved per run

### JOB PARALLELIZATION
- Pattern: Sequential jobs with no dependencies that could run in parallel
- Pattern: Test suites running sequentially (unit, integration, e2e)
- Implementation: Split into parallel jobs or use matrix strategy
- Impact: 40-60% reduction in total pipeline time

### DOCKER OPTIMIZATION
- Pattern: "docker build" WITHOUT Docker layer caching
- Pattern: Multiple docker builds without BuildKit
- Implementation: Use docker/build-push-action@v4 with cache-from/cache-to
- Impact: 3-8 minutes saved per build

### RUNNER OPTIMIZATION
- Pattern: Over-provisioned runners (8-cores for linting, documentation builds)
- Pattern: Under-provisioned runners (basic for heavy compilation)
- Implementation: Right-size runners based on workload
- Cost Analysis: ubuntu-latest ($0.008/min), ubuntu-latest-4-cores ($0.016/min), ubuntu-latest-8-cores ($0.032/min)

## 2. MEDIUM-IMPACT OPTIMIZATIONS

### CONDITIONAL EXECUTION
- Pattern: Workflows triggering on ALL file changes
- Pattern: Missing path-based triggers for specific file types
- Implementation: Add paths filter to workflow triggers
- Impact: Reduce unnecessary runs by 30-50%

### ARTIFACT OPTIMIZATION  
- Pattern: Uploading entire workspace as artifacts
- Pattern: Large artifacts without compression
- Implementation: Selective artifact upload, exclude unnecessary files
- Impact: Faster upload/download, reduced storage costs

### ENVIRONMENT OPTIMIZATION
- Pattern: Redundant setup steps across jobs
- Pattern: Missing shared caching between jobs
- Implementation: Use job outputs, shared setup job
- Impact: 1-2 minutes saved per job

ANALYSIS INSTRUCTIONS:
1. Scan each workflow for these exact patterns
2. Calculate time savings based on pattern type and repository activity
3. Estimate monthly cost savings using GitHub Actions pricing
4. Provide specific implementation with exact code examples
5. Set confidence scores based on pattern clarity (0.9 for obvious patterns, 0.7 for probable, 0.5 for possible)
"""
    
    def _parse_ai_recommendations(
        self, 
        ai_response: List[Dict[str, Any]], 
        repository_stats: Dict[str, Any],
        workflows: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """Convert AI response to standardized recommendation format with cost validation."""
        processed_recommendations = []
        runs_per_week = repository_stats.get('runs_count', 0) * 7 / repository_stats.get('analysis_days', 30) if repository_stats.get('analysis_days', 0) > 0 else 0
        
        validation_stats = {
            "total_validated": 0,
            "adjusted": 0,
            "passed": 0
        }
        
        self.logger.info(f"MANDATORY cost validation starting - {len(ai_response)} recommendations to validate")
        if runs_per_week > 0:
            self.logger.debug(f"Using actual usage data: {runs_per_week:.1f} runs/week")
        else:
            self.logger.debug("Using conservative default: 50 runs/week for validation")
        
        for rec in ai_response:
            # Ensure all required fields are present
            processed_rec = {
                "title": rec.get("title", "Unknown Optimization"),
                "type": rec.get("type", "unknown"),
                "priority": rec.get("priority", "medium"),
                "workflow_file": rec.get("workflow_file", rec.get("workflow", "unknown")),
                "job_name": rec.get("job_name", "unknown"),
                "line_number": rec.get("line_number", ""),
                "description": rec.get("description", ""),
                "impact_time_minutes": float(rec.get("impact_time_minutes", 0)),
                "monthly_cost_savings": float(rec.get("monthly_cost_savings", 0)),
                "confidence_score": float(rec.get("confidence_score", 0.5)),
                "implementation_effort": rec.get("implementation_effort", "medium"),
                "implementation": rec.get("implementation", ""),
                "code_example": rec.get("code_example", "")
            }
            
            # MANDATORY cost validation for every recommendation
            validation = validate_cost_calculation(
                processed_rec["impact_time_minutes"],
                processed_rec["monthly_cost_savings"],
                runs_per_week if runs_per_week > 0 else 50  # Use conservative default if no data
            )
            
            validation_stats["total_validated"] += 1
            
            if not validation["is_reasonable"]:
                validation_stats["adjusted"] += 1
                self.logger.warning(f"Cost calculation adjusted for '{processed_rec['title']}': {validation['recommendation']}")
                # Use the more conservative expected calculation
                processed_rec["monthly_cost_savings"] = validation["expected_savings"]
                if "Cost adjusted:" not in processed_rec["description"]:
                    processed_rec["description"] += f" (Cost calculation adjusted based on usage patterns)"
            else:
                validation_stats["passed"] += 1
                self.logger.debug(f"Cost calculation validated for '{processed_rec['title']}': ${processed_rec['monthly_cost_savings']:.2f}/month")
            
            # Log if AI failed to provide line numbers
            if not processed_rec["line_number"]:
                self.logger.warning(f"AI did not provide line number for '{processed_rec['title']}' in {processed_rec['workflow_file']}")

            processed_recommendations.append(processed_rec)
        
        # Log validation summary
        self.logger.info(f"Cost validation complete: {validation_stats['total_validated']} total, "
                        f"{validation_stats['passed']} passed, {validation_stats['adjusted']} adjusted")
        
        return processed_recommendations
    
    def _add_line_numbers_to_yaml(self, yaml_content: str) -> str:
        """Add line numbers to YAML content for AI analysis."""
        lines = yaml_content.split('\n')
        numbered_lines = []
        
        for i, line in enumerate(lines, 1):
            numbered_lines.append(f"{i:3d}| {line}")
        
        return '\n'.join(numbered_lines)
    
    def _extract_json_from_response(self, content: str) -> str:
        """Extract JSON from AI response that may be wrapped in markdown code blocks."""
        
        # First try to find JSON in code blocks
        import re
        
        # Look for ```json ... ``` blocks
        json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
        matches = re.findall(json_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if matches:
            # Use the first JSON block found
            json_content = matches[0].strip()
            self.logger.debug(f"Extracted JSON from code block: {len(json_content)} chars")
            return json_content
        
        # Look for array starting with [ and ending with ]
        array_pattern = r'(\[.*\])'
        array_matches = re.findall(array_pattern, content, re.DOTALL)
        
        if array_matches:
            json_content = array_matches[0].strip()
            self.logger.debug(f"Extracted JSON array from response: {len(json_content)} chars")
            return json_content
        
        # If no patterns found, return the original content
        self.logger.debug("No JSON patterns found, using original content")
        return content.strip()
