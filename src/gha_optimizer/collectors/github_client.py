"""GitHub API client for collecting workflow data."""

import base64
import logging
from functools import lru_cache
from typing import List, Optional

import requests

from ..models.workflow import Workflow, WorkflowRun
from ..utils.config import Config


class GitHubAPIError(Exception):
    """Exception raised for GitHub API errors."""

    pass


class GitHubClient:
    """Client for interacting with GitHub API to collect workflow data."""

    def __init__(
        self,
        token: str,
        config: Config,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize GitHub client.

        Args:
            token: GitHub personal access token
            config: Application configuration
            logger: Logger instance
        """
        self.token = token
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        self.base_url = config.github_api_url

        # Create reusable session with proper configuration
        self.session = self._create_session(token)

    def _create_session(self, token: str) -> requests.Session:
        """Create configured requests session."""
        session = requests.Session()
        session.headers.update(
            {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "gha-optimizer/0.1.0",
            }
        )

        # Set reasonable timeouts
        session.timeout = (10, 30)  # (connect_timeout, read_timeout)

        # Configure retries for connection issues
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def collect_workflows(self, owner: str, repo: str) -> List[Workflow]:
        """
        Collect all workflows from a repository.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            List of Workflow objects

        Raises:
            GitHubAPIError: If API request fails
        """
        try:
            self.logger.info(f"Collecting workflows for {owner}/{repo}")

            # Get list of workflows
            workflows_url = (
                f"{self.base_url}/repos/{owner}/{repo}/actions/workflows"
            )
            response = self.session.get(workflows_url)

            if response.status_code == 404:
                raise GitHubAPIError(f"Repository {owner}/{repo} not found")
            elif response.status_code == 403:
                raise GitHubAPIError(
                    "GitHub API rate limit exceeded or insufficient permissions"
                )
            elif response.status_code != 200:
                raise GitHubAPIError(
                    f"GitHub API error: {response.status_code}"
                )

            workflows_data = response.json()
            workflows = []

            for workflow_data in workflows_data.get("workflows", []):
                # Get workflow file content using Contents API
                file_path = workflow_data["path"]
                contents_url = (
                    f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
                )
                file_response = self.session.get(contents_url)

                if file_response.status_code == 200:
                    content_data = file_response.json()
                    # GitHub returns base64 encoded content
                    file_content = base64.b64decode(
                        content_data["content"]
                    ).decode("utf-8")
                    workflow = Workflow.from_yaml(
                        file_path=file_path,
                        yaml_content=file_content,
                    )
                    workflows.append(workflow)
                else:
                    self.logger.warning(
                        f"Failed to fetch content for {file_path}: "
                        f"{file_response.status_code}"
                    )

            self.logger.info(f"Collected {len(workflows)} workflows")
            return workflows

        except requests.RequestException as e:
            raise GitHubAPIError(f"Network error: {e}") from e

    def collect_run_history(
        self,
        owner: str,
        repo: str,
        workflow_id: Optional[str] = None,
        days: int = 30,
    ) -> List[WorkflowRun]:
        """
        Collect workflow run history.

        Args:
            owner: Repository owner
            repo: Repository name
            workflow_id: Specific workflow ID (optional)
            days: Number of days of history to collect

        Returns:
            List of WorkflowRun objects

        Raises:
            GitHubAPIError: If API request fails
        """
        try:
            self.logger.info(
                f"Collecting workflow runs for {owner}/{repo} (last {days} days)"
            )

            # Build URL based on whether we want all runs or specific workflow
            if workflow_id:
                runs_url = f"{self.base_url}/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
            else:
                runs_url = f"{self.base_url}/repos/{owner}/{repo}/actions/runs"

            # Add parameters for recent runs
            params = {
                "per_page": 100,
                "status": "completed",  # Only get completed runs for analysis
            }

            response = self.session.get(runs_url, params=params)

            if response.status_code != 200:
                raise GitHubAPIError(
                    f"GitHub API error: {response.status_code}"
                )

            runs_data = response.json()
            workflow_runs = []

            for run_data in runs_data.get("workflow_runs", []):
                # TODO: Parse run data into WorkflowRun objects
                # For now, create placeholder objects
                workflow_run = WorkflowRun(
                    id=str(run_data["id"]),
                    workflow_id=str(run_data["workflow_id"]),
                    name=run_data["name"],
                    status=run_data["status"],
                    conclusion=run_data["conclusion"] or "unknown",
                    created_at=run_data["created_at"],
                    updated_at=run_data["updated_at"],
                    run_started_at=run_data.get("run_started_at"),
                    jobs=[],  # TODO: Collect job data
                )
                workflow_runs.append(workflow_run)

            self.logger.info(f"Collected {len(workflow_runs)} workflow runs")
            return workflow_runs

        except requests.RequestException as e:
            raise GitHubAPIError(f"Network error: {e}") from e

    @lru_cache(maxsize=128)
    def collect_repository_metadata(self, owner: str, repo: str) -> dict:
        """
        Collect repository metadata.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Dictionary with repository metadata

        Raises:
            GitHubAPIError: If API request fails
        """
        try:
            self.logger.debug(f"Collecting metadata for {owner}/{repo}")

            repo_url = f"{self.base_url}/repos/{owner}/{repo}"
            response = self.session.get(repo_url)

            if response.status_code != 200:
                raise GitHubAPIError(
                    f"GitHub API error: {response.status_code}"
                )

            repo_data = response.json()

            return {
                "name": repo_data["name"],
                "full_name": repo_data["full_name"],
                "language": repo_data.get("language"),
                "size": repo_data["size"],
                "stars": repo_data["stargazers_count"],
                "forks": repo_data["forks_count"],
                "default_branch": repo_data["default_branch"],
                "created_at": repo_data["created_at"],
                "updated_at": repo_data["updated_at"],
            }

        except requests.RequestException as e:
            raise GitHubAPIError(f"Network error: {e}") from e

    def test_connection(self) -> bool:
        """
        Test GitHub API connection and token validity.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.logger.debug("Testing GitHub API connection")

            user_url = f"{self.base_url}/user"
            response = self.session.get(user_url)

            if response.status_code == 200:
                user_data = response.json()
                self.logger.info(
                    f"Connected to GitHub as: {user_data.get('login')}"
                )
                return True
            else:
                self.logger.error(
                    f"GitHub API connection failed: {response.status_code}"
                )
                return False

        except requests.RequestException as e:
            self.logger.error(f"GitHub API connection error: {e}")
            return False
