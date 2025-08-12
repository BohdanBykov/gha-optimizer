"""
GHA-Optimizer: AI-Powered GitHub Actions Workflow Optimization Tool

A pluggable tool that analyzes GitHub Actions workflows and generates
actionable optimization recommendations with quantified impact metrics.
"""

__version__ = "0.0.1"
__author__ = "https://github.com/BohdanBykov"

from .models.workflow import Workflow, WorkflowRun
from .collectors.github_client import GitHubClient

__all__ = [
    "Workflow",
    "WorkflowRun", 
    "GitHubClient",
]