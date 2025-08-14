"""Scan command implementation for quick workflow analysis."""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..analyzers.ai_analyzer import AIWorkflowAnalyzer
from ..collectors.workflow_collector import WorkflowCollector
from ..reports.console_reporter import ConsoleReporter
from ..utils.config import Config


@dataclass
class ScanResult:
    """Result of scan command execution."""

    success: bool
    recommendations: List[Dict[str, Any]]
    estimated_savings: float
    time_savings: float
    error: Optional[str] = None


class ScanCommand:
    """Command for quick scan of GitHub repository workflows."""

    def __init__(self, config: Config, logger: logging.Logger) -> None:
        """
        Initialize scan command.

        Args:
            config: Application configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger

    def execute(
        self,
        repository: str,
        github_token: Optional[str] = None,
        output_file: Optional[Path] = None,
        output_format: str = "markdown",
        max_history_days: int = 30,
        workflow_files: Optional[List[str]] = None,
        output_prompt_file: Optional[Path] = None,
    ) -> ScanResult:
        """
        Execute scan command.

        Args:
            repository: GitHub repository in format 'owner/repo'
            github_token: GitHub personal access token
            output_file: Output file for detailed report
            output_format: Output format (markdown, html, json)
            max_history_days: Maximum days of workflow history to analyze
            workflow_files: List of specific workflow files to analyze (optional)
            output_prompt_file: Debug option to save AI prompt to file without API call

        Returns:
            ScanResult with success status, recommendations, and impact metrics
        """
        try:
            self.logger.info(f"Starting scan of repository: {repository}")

            # Validate repository format
            if "/" not in repository:
                return ScanResult(
                    success=False,
                    recommendations=[],
                    estimated_savings=0.0,
                    time_savings=0.0,
                    error="Repository must be in format 'owner/repo'",
                )

            owner, repo = repository.split("/", 1)
            self.logger.debug(f"Repository owner: {owner}, repo: {repo}")

            # Get GitHub token
            token = github_token or self.config.github_token
            if not token:
                return ScanResult(
                    success=False,
                    recommendations=[],
                    estimated_savings=0.0,
                    time_savings=0.0,
                    error=(
                        "GitHub token is required. Set GITHUB_TOKEN environment variable "
                        "or use --token"
                    ),
                )

            # Validate AI configuration (mandatory)
            if not self.config.ai_api_key:
                return ScanResult(
                    success=False,
                    recommendations=[],
                    estimated_savings=0.0,
                    time_savings=0.0,
                    error=(
                        "AI API key is required for analysis. Set your AI API key in "
                        "config or environment."
                    ),
                )

            # Collect real workflow data from GitHub
            workflow_collector = WorkflowCollector(self.config, self.logger)
            workflow_data = workflow_collector.collect_workflow_data(
                owner, repo, token, max_history_days, workflow_files
            )

            # Get raw workflows for AI analysis
            raw_workflows = workflow_collector.get_raw_workflows_for_ai(owner, repo, token, workflow_files)

            # Run AI analysis on raw workflows or save prompt to file
            ai_analyzer = AIWorkflowAnalyzer(self.config, self.logger)

            # Debug mode: Save prompt to file without making API call
            if output_prompt_file:
                self.logger.info(f"Debug mode: Saving AI prompt to {output_prompt_file}")
                prompt_content = ai_analyzer.generate_prompt_only(raw_workflows, workflow_data)

                try:
                    with open(output_prompt_file, "w", encoding="utf-8") as f:
                        f.write(prompt_content)
                    self.logger.info(f"Prompt saved successfully to {output_prompt_file}")

                    return ScanResult(
                        success=True,
                        recommendations=[],
                        estimated_savings=0.0,
                        time_savings=0.0,
                        error=None,
                    )
                except Exception as e:
                    return ScanResult(
                        success=False,
                        recommendations=[],
                        estimated_savings=0.0,
                        time_savings=0.0,
                        error=f"Failed to save prompt to file: {e}",
                    )

            ai_recommendations = ai_analyzer.analyze_workflows(raw_workflows, workflow_data)

            # Calculate impact metrics from AI recommendations
            estimated_savings, time_savings = self._calculate_impact_from_ai_recommendations(
                ai_recommendations
            )

            recommendations = ai_recommendations

            self.logger.info(
                f"Analysis completed. Found {len(recommendations)} optimization opportunities"
            )
            self.logger.info(f"Estimated monthly savings: ${estimated_savings:.0f}")
            self.logger.info(f"Estimated time savings: {time_savings:.1f} minutes per run")

            # Generate and print console report
            reporter = ConsoleReporter(self.config)
            report = reporter.generate_report(
                repository,
                recommendations,
                estimated_savings,
                time_savings,
                workflow_data,
            )
            print(report)

            # TODO: Generate detailed report if output file specified
            if output_file:
                self.logger.info(f"Generating {output_format} report: {output_file}")
                # Placeholder: would generate actual report here

            return ScanResult(
                success=True,
                recommendations=recommendations,
                estimated_savings=estimated_savings,
                time_savings=time_savings,
            )

        except Exception as e:
            self.logger.error(f"Scan failed: {e}")
            return ScanResult(
                success=False,
                recommendations=[],
                estimated_savings=0.0,
                time_savings=0.0,
                error=str(e),
            )

    def _calculate_impact_from_ai_recommendations(
        self, recommendations: List[Dict[str, Any]]
    ) -> tuple[float, float]:
        """Calculate total impact from AI recommendations."""
        total_savings = 0.0
        total_time = 0.0

        for rec in recommendations:
            # Extract monetary savings
            total_savings += float(rec.get("monthly_cost_savings", 0))

            # Extract time savings
            total_time += float(rec.get("impact_time_minutes", 0))

        return total_savings, total_time
