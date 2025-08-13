"""
GHA-Optimizer: AI-Powered GitHub Actions Workflow Optimization Tool

A pluggable tool that analyzes GitHub Actions workflows and generates
actionable optimization recommendations with quantified impact metrics.
"""

__version__ = "1.0.0"
__author__ = "https://github.com/BohdanBykov"

from .analyzers.ai_analyzer import AIWorkflowAnalyzer
from .collectors.github_client import GitHubClient
from .models.workflow import Workflow, WorkflowRun
from .reports.console_reporter import ConsoleReporter

__all__ = [
    "__version__",
    "Workflow",
    "WorkflowRun",
    "GitHubClient",
    "AIWorkflowAnalyzer",
    "ConsoleReporter",
]
