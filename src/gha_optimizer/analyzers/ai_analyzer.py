"""AI-powered workflow analyzer using existing optimization patterns."""

import json
import logging
import re
import time
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .. import __version__
from ..utils.config import Config
from ..utils.helpers import validate_cost_calculation


class AIWorkflowAnalyzer:
    """AI-powered analyzer for GitHub Actions workflows using predefined optimization patterns."""

    def __init__(
        self, config: Config, logger: Optional[logging.Logger] = None, local_docs: bool = False
    ) -> None:
        """Initialize AI analyzer."""
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.local_docs = local_docs

        # Validate AI configuration
        if not self.config.ai_api_key:
            raise ValueError("AI API key is required for analysis")

        self.logger.info(
            f"Initialized AI analyzer with {self.config.ai_provider} ({self.config.ai_model})"
        )

        if self.local_docs:
            self.logger.info("Local documentation mode enabled for debugging")

    def analyze_workflows(
        self, workflows: Dict[str, str], repository_stats: Dict[str, Any]
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

        # Build comprehensive prompt with all workflows and IDs
        prompt = self._build_workflow_prompt(workflows, repository_stats)

        # Single AI API call for all workflows
        ai_response = self._call_ai_api(prompt)

        # Convert AI response to existing recommendation format
        recommendations = self._parse_ai_recommendations(ai_response, repository_stats, workflows)

        self.logger.info(
            f"AI analysis completed. Found {len(recommendations)} optimization opportunities"
        )
        return recommendations

    def generate_prompt_only(
        self, workflows: Dict[str, str], repository_stats: Dict[str, Any]
    ) -> str:
        """
        Generate AI prompt for debugging purposes without making API call.

        Args:
            workflows: Dictionary mapping file paths to raw YAML content
            repository_stats: Statistics from GitHub API

        Returns:
            Complete prompt string that would be sent to AI
        """
        self.logger.info(f"Generating prompt for {len(workflows)} workflows (debug mode)")

        # Use the same prompt building logic as regular analysis
        prompt = self._build_workflow_prompt(workflows, repository_stats)

        self.logger.info(f"Prompt generated successfully: {len(prompt)} characters")
        return prompt

    def _build_workflow_prompt(
        self, workflows: Dict[str, str], repository_stats: Dict[str, Any]
    ) -> str:
        """Build single prompt with all workflows using IDs for cost efficiency."""

        # Get optimization patterns
        optimization_patterns = self._get_optimization_patterns_from_docs()

        # Calculate estimated runs per week for impact calculation
        runs_per_week = (
            repository_stats.get("runs_count", 0) * 7 / repository_stats.get("analysis_days", 30)
        )

        # Build workflows section with IDs
        workflows_section = []
        workflow_ids = {}

        for idx, (workflow_path, workflow_content) in enumerate(workflows.items(), 1):
            workflow_id = f"WF{idx:02d}"
            workflow_ids[workflow_id] = workflow_path
            numbered_yaml = self._add_line_numbers_to_yaml(workflow_content)

            workflows_section.append(
                f"""
### Workflow {workflow_id}: `{workflow_path}`
```yaml
{numbered_yaml}
```"""
            )

        workflows_text = "\n".join(workflows_section)

        return f"""You are an expert GitHub Actions optimization analyst powered by GHA-Optimizer v{__version__}.

ANALYSIS TASK: Analyze ALL workflows below for optimization opportunities using the comprehensive patterns documentation provided.

## Repository Context
- **Repository**: {repository_stats.get('repository', {}).get('full_name', 'Unknown')}
- **Language**: {repository_stats.get('repository', {}).get('language', 'Unknown')}
- **Activity**: {repository_stats.get('runs_count', 0)} runs in {repository_stats.get('analysis_days', 30)} days (~{runs_per_week:.0f}/week)
- **Total Workflows**: {len(workflows)}

## Optimization Patterns Documentation
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
    "implementation": "Add actions/cache@v3 before npm install",
    "code_example": "- uses: actions/cache@v3\\n  with:\\n    path: ~/.npm\\n    key: ${{{{ runner.os }}}}-node-${{{{ hashFiles('package-lock.json') }}}}"
  }}
]
```
"""

    def _call_ai_api(self, prompt: str) -> List[Dict[str, Any]]:
        """Call Anthropic Claude AI API for workflow analysis."""
        self.logger.debug(f"Calling {self.config.ai_provider} API with {self.config.ai_model}")

        try:
            if self.config.ai_provider == "anthropic":
                return self._call_anthropic_api(prompt)
            else:
                raise ValueError(
                    f"Unsupported AI provider: {self.config.ai_provider}. Only 'anthropic' is supported."
                )

        except Exception as e:
            self.logger.error(f"AI API call failed: {e}")
            raise RuntimeError(
                f"AI analysis failed and no fallback available. GHA-Optimizer requires AI API access. "
                f"Please check your API key and network connection. Error: {e}"
            )

    def _call_anthropic_api(self, prompt: str) -> List[Dict[str, Any]]:
        """Call Anthropic Claude API for workflow analysis with simple retry logic."""
        max_retries = 3
        base_delay = 1

        for attempt in range(max_retries):
            try:
                import anthropic

                client = anthropic.Anthropic(api_key=self.config.ai_api_key)

                self.logger.debug(
                    f"Making Anthropic API request (attempt {attempt + 1}/{max_retries})"
                )
                response = client.messages.create(
                    model=self.config.ai_model,
                    max_tokens=4000,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}],
                )

                # Handle different content block types
                content_block = response.content[0]
                if hasattr(content_block, "text"):
                    content = content_block.text.strip()
                else:
                    self.logger.error(f"Unexpected content block type: {type(content_block)}")
                    return []
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
                    delay = base_delay * (2**attempt)  # Exponential backoff
                    self.logger.warning(
                        f"Anthropic API error (attempt {attempt + 1}): {e}. Retrying in {delay}s..."
                    )
                    time.sleep(delay)

        # This should never be reached due to the loop structure, but mypy requires it
        return []

    @lru_cache(maxsize=1)
    def _get_optimization_patterns_from_docs(self) -> str:
        """Return comprehensive optimization patterns based on documentation.

        Strategy:
        1. If --local-docs: Use local documentation (debug mode)
        2. Remote first: Try GitHub documentation (prompt economy)
        3. Fallback chain: packaged → local development
        """
        github_url = f"https://github.com/BohdanBykov/gha-optimizer/blob/v{__version__}/docs/optimization-patterns.md"

        # Debug mode: force local documentation
        if self.local_docs:
            self.logger.info("Using local documentation for debugging")
            doc_content, source = self._load_documentation_content(force_local=True)
            return self._wrap_documentation_for_prompt(
                doc_content, github_url, source, is_debug=True
            )

        # Normal mode: try remote first for prompt economy
        if self._try_fetch_remote_documentation(github_url):
            return self._create_remote_documentation_reference(github_url)

        # Fallback: load local content
        self.logger.warning("Remote documentation fetch failed, using local fallback")
        doc_content, source = self._load_documentation_content(force_local=False)
        return self._wrap_documentation_for_prompt(doc_content, github_url, source, is_debug=False)

    def _try_fetch_remote_documentation(self, github_url: str) -> bool:
        """Try to fetch remote documentation to verify it exists and is accessible."""
        try:
            # Convert GitHub blob URL to raw content URL for verification
            raw_url = github_url.replace("/blob/", "/raw/")

            self.logger.debug(f"Checking remote documentation availability: {raw_url}")

            # Use HEAD request with redirect following
            response = requests.head(raw_url, timeout=5, allow_redirects=True)

            if response.status_code == 200:
                self.logger.info(f"Remote documentation verified: {github_url}")
                return True
            else:
                # If HEAD fails, try a lightweight GET request to be sure
                self.logger.debug(
                    f"HEAD request failed ({response.status_code}), trying GET request"
                )
                get_response = requests.get(raw_url, timeout=5, stream=True)

                if get_response.status_code == 200:
                    # Don't download full content, just verify it's accessible
                    get_response.close()
                    self.logger.info(f"Remote documentation verified via GET: {github_url}")
                    return True
                else:
                    self.logger.warning(
                        f"Remote documentation not accessible: HEAD {response.status_code}, GET {get_response.status_code}"
                    )
                    return False

        except requests.exceptions.RequestException as e:
            self.logger.warning(f"Failed to verify remote documentation: {e}")
            return False
        except Exception as e:
            self.logger.warning(f"Unexpected error checking remote documentation: {e}")
            return False

    def _create_remote_documentation_reference(self, github_url: str) -> str:
        """Create compact prompt referencing remote documentation for prompt economy."""
        self.logger.info(f"Using remote documentation reference for prompt economy: {github_url}")
        return f"""

**Version:** {__version__}
**Documentation URL:** {github_url}

**INSTRUCTIONS:** The comprehensive optimization patterns documentation is available at the URL above.
It contains detailed patterns, confidence scoring guidelines, impact calculations, and implementation examples.

**KEY PATTERNS TO DETECT** (refer to full documentation for details):
- Dependency caching (Node.js, Python, Java/Maven, Docker)
- Job parallelization opportunities
- Runner optimization (right-sizing)
- Conditional execution improvements
- Artifact optimization

**CRITICAL ANALYSIS REQUIREMENTS:**
1. Reference the documentation URL above for complete pattern details
2. Use exact pattern matches for high confidence (0.8-1.0)
3. Apply conservative confidence scores when patterns are unclear
4. Provide specific line numbers and ready-to-use code examples
5. Calculate realistic time savings and monthly costs
6. Follow the JSON recommendation template from the documentation

Use the patterns and guidelines from the documentation URL as your authoritative source.
"""

    def _load_documentation_content(self, force_local: bool = False) -> tuple[str, str]:
        """Load documentation content from available sources.

        Returns:
            tuple: (content, source_description)
        """
        if force_local:
            # Debug mode: only try local development
            try:
                content = self._load_development_documentation()
                self.logger.info("Using local development documentation (debug mode)")
                return content, "local development documentation"
            except Exception as e:
                self.logger.error(f"Failed to load local development documentation: {e}")
                raise ValueError(
                    f"Cannot proceed without optimization patterns documentation. "
                    f"Local development documentation unavailable. Error: {e}"
                )

        # Normal fallback chain: packaged → local development
        try:
            content = self._load_packaged_documentation()
            self.logger.info("Using packaged documentation fallback")
            return content, "packaged documentation"
        except Exception as packaged_error:
            self.logger.warning(f"Packaged documentation failed: {packaged_error}")
            try:
                content = self._load_development_documentation()
                self.logger.info("Using local development documentation fallback")
                return content, "local development documentation"
            except Exception as dev_error:
                self.logger.error(
                    f"All documentation sources failed: packaged={packaged_error}, local={dev_error}"
                )
                raise ValueError(
                    "Cannot proceed without optimization patterns documentation. "
                    "All local sources are unavailable."
                )

    def _wrap_documentation_for_prompt(
        self, doc_content: str, github_url: str, source: str, is_debug: bool = False
    ) -> str:
        """Wrap documentation content with consistent prompt instructions."""
        # Verify version compatibility
        if f"**Version:** {__version__}" not in doc_content:
            self.logger.warning(
                f"Documentation version mismatch. Tool: {__version__}. "
                f"Recommendations may be inconsistent."
            )

        mode = "LOCAL DEBUG MODE" if is_debug else "LOCAL FALLBACK"
        url_label = "Debug URL" if is_debug else "Intended URL"
        note = (
            "Using local documentation in debug mode."
            if is_debug
            else "Using local documentation fallback due to remote access issues."
        )

        return f"""
GITHUB ACTIONS OPTIMIZATION PATTERNS DOCUMENTATION ({mode})
Version: {__version__}
Source: {source}
{url_label}: {github_url}

{doc_content}

CRITICAL INSTRUCTIONS FOR AI ANALYSIS:
1. Follow ALL guidelines and confidence scoring rules from the documentation above
2. Use EXACT pattern matches for high confidence recommendations
3. Apply cost calculation standards and validation requirements
4. Reference specific line numbers and provide ready-to-use code examples
5. Use conservative confidence scores when patterns are unclear

Note: {note}
"""

    def _load_packaged_documentation(self) -> str:
        """Load documentation from the packaged distribution."""
        # Use importlib.resources to access packaged documentation
        package_files = files("gha_optimizer.docs")
        doc_file = package_files / "optimization-patterns.md"

        if not doc_file.is_file():
            raise FileNotFoundError("Packaged documentation not found")

        return doc_file.read_text(encoding="utf-8")

    def _load_development_documentation(self) -> str:
        """Load documentation from development environment (src/gha_optimizer/docs/)."""
        docs_path = Path(__file__).parent.parent / "docs" / "optimization-patterns.md"

        if not docs_path.exists():
            raise FileNotFoundError(f"Development documentation not found at {docs_path}")

        with open(docs_path, "r", encoding="utf-8") as f:
            return f.read()

    def _parse_ai_recommendations(
        self,
        ai_response: List[Dict[str, Any]],
        repository_stats: Dict[str, Any],
        workflows: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """Convert AI response to standardized recommendation format with cost validation."""
        processed_recommendations = []
        runs_per_week = (
            repository_stats.get("runs_count", 0) * 7 / repository_stats.get("analysis_days", 30)
            if repository_stats.get("analysis_days", 0) > 0
            else 0
        )

        validation_stats = {"total_validated": 0, "adjusted": 0, "passed": 0}

        self.logger.info(
            f"MANDATORY cost validation starting - {len(ai_response)} recommendations to validate"
        )
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
                "implementation": rec.get("implementation", ""),
                "code_example": rec.get("code_example", ""),
            }

            # MANDATORY cost validation for every recommendation
            validation = validate_cost_calculation(
                processed_rec["impact_time_minutes"],
                processed_rec["monthly_cost_savings"],
                (runs_per_week if runs_per_week > 0 else 50),  # Use conservative default if no data
            )

            validation_stats["total_validated"] += 1

            if not validation["is_reasonable"]:
                validation_stats["adjusted"] += 1
                self.logger.warning(
                    f"Cost calculation adjusted for '{processed_rec['title']}': {validation['recommendation']}"
                )
                # Use the more conservative expected calculation
                processed_rec["monthly_cost_savings"] = validation["expected_savings"]
                if "Cost adjusted:" not in processed_rec["description"]:
                    processed_rec[
                        "description"
                    ] += " (Cost calculation adjusted based on usage patterns)"
            else:
                validation_stats["passed"] += 1
                self.logger.debug(
                    f"Cost calculation validated for '{processed_rec['title']}': ${processed_rec['monthly_cost_savings']:.2f}/month"
                )

            # Log if AI failed to provide line numbers
            if not processed_rec["line_number"]:
                self.logger.warning(
                    f"AI did not provide line number for '{processed_rec['title']}' in {processed_rec['workflow_file']}"
                )

            processed_recommendations.append(processed_rec)

        # Log validation summary
        self.logger.info(
            f"Cost validation complete: {validation_stats['total_validated']} total, "
            f"{validation_stats['passed']} passed, {validation_stats['adjusted']} adjusted"
        )

        return processed_recommendations

    def _add_line_numbers_to_yaml(self, yaml_content: str) -> str:
        """Add line numbers to YAML content for AI analysis."""
        lines = yaml_content.split("\n")
        numbered_lines = []

        for i, line in enumerate(lines, 1):
            numbered_lines.append(f"{i:3d}| {line}")

        return "\n".join(numbered_lines)

    def _extract_json_from_response(self, content: str) -> str:
        """Extract JSON from AI response that may be wrapped in markdown code blocks."""

        # First try to find JSON in code blocks

        # Look for ```json ... ``` blocks
        json_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
        matches = re.findall(json_pattern, content, re.DOTALL | re.IGNORECASE)

        if matches:
            # Use the first JSON block found
            json_content = matches[0].strip()
            self.logger.debug(f"Extracted JSON from code block: {len(json_content)} chars")
            return str(json_content)

        # Look for array starting with [ and ending with ]
        array_pattern = r"(\[.*\])"
        array_matches = re.findall(array_pattern, content, re.DOTALL)

        if array_matches:
            json_content = array_matches[0].strip()
            self.logger.debug(f"Extracted JSON array from response: {len(json_content)} chars")
            return str(json_content)

        # If no patterns found, return the original content
        self.logger.debug("No JSON patterns found, using original content")
        return content.strip()
