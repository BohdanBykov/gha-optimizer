"""Workflow data collector for aggregating GitHub workflow information."""

import logging
from typing import Any, Dict, Optional

from ..utils.config import Config
from .github_client import GitHubAPIError, GitHubClient


class WorkflowCollector:
    """Collector for aggregating workflow data from GitHub API."""

    def __init__(self, config: Config, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize workflow collector.

        Args:
            config: Application configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)

    def collect_workflow_data(
        self, owner: str, repo: str, token: str, max_history_days: int
    ) -> Dict[str, Any]:
        """
        Collect comprehensive workflow data from GitHub API.

        Args:
            owner: Repository owner
            repo: Repository name
            token: GitHub token
            max_history_days: Maximum days of history to analyze

        Returns:
            Dictionary containing workflow metrics and data
        """
        try:
            # Initialize GitHub client
            github_client = GitHubClient(token, self.config, self.logger)

            # Test connection first
            if not github_client.test_connection():
                raise GitHubAPIError(
                    "GitHub API connection test failed - check your token and network connectivity"
                )

            # Collect workflows
            workflows = github_client.collect_workflows(owner, repo)

            # Collect workflow runs
            workflow_runs = github_client.collect_run_history(owner, repo, days=max_history_days)

            # Collect repository metadata
            repo_metadata = github_client.collect_repository_metadata(owner, repo)

            self.logger.info(
                f"Successfully collected data: {len(workflows)} workflows, {len(workflow_runs)} runs"
            )

            return {
                "workflows": workflows,
                "workflow_runs": workflow_runs,
                "repository": repo_metadata,
                "workflow_count": len(workflows),
                "runs_count": len(workflow_runs),
                "analysis_days": max_history_days,
                "data_source": "github_api",
            }

        except GitHubAPIError as e:
            self.logger.error(f"GitHub API error: {e}")
            raise  # Re-raise the exception instead of falling back
        except Exception as e:
            self.logger.error(f"Unexpected error collecting workflow data: {e}")
            raise GitHubAPIError(f"Failed to collect workflow data: {e}") from e

    def get_raw_workflows_for_ai(self, owner: str, repo: str, token: str) -> Dict[str, str]:
        """
        Get raw workflow YAML content for AI analysis.

        Args:
            owner: Repository owner
            repo: Repository name
            token: GitHub token

        Returns:
            Dictionary mapping file paths to raw YAML content
        """
        try:
            github_client = GitHubClient(token, self.config, self.logger)

            if not github_client.test_connection():
                raise GitHubAPIError(
                    "GitHub API connection test failed - check your token and network connectivity"
                )

            workflows = github_client.collect_workflows(owner, repo)

            # Return mapping of file path to raw YAML content
            return {workflow.file_path: workflow.content for workflow in workflows}

        except GitHubAPIError:
            raise
        except Exception as e:
            raise GitHubAPIError(f"Failed to get raw workflows: {e}") from e
