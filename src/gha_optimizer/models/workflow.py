"""Data models for GitHub Actions workflows and runs."""

import yaml
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..utils.config import Config
from ..utils.helpers import validate_string, validate_list, safe_execute, SimpleTimer


@dataclass
class Job:
    """Represents a job in a GitHub Actions workflow."""
    
    name: str
    runs_on: str
    steps: List[Dict[str, Any]]
    needs: List[str] = field(default_factory=list)
    if_condition: Optional[str] = None
    strategy: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Simple validation after initialization."""
        self.name = validate_string(self.name, "Job name")
        self.runs_on = validate_string(self.runs_on, "Job runs_on")
        self.steps = validate_list(self.steps, "Job steps")


@dataclass
class Trigger:
    """Represents a trigger configuration for a workflow."""
    
    event: str
    branches: List[str] = field(default_factory=list)
    paths: List[str] = field(default_factory=list)
    types: List[str] = field(default_factory=list)


@dataclass
class Workflow:
    """Represents a GitHub Actions workflow."""
    
    name: str
    file_path: str
    content: str
    jobs: List[Job]
    triggers: List[Trigger]
    
    def __post_init__(self):
        """Simple validation after initialization."""
        self.name = validate_string(self.name, "Workflow name")
        self.file_path = validate_string(self.file_path, "Workflow file_path")
        self.jobs = validate_list(self.jobs, "Workflow jobs")
        self.triggers = validate_list(self.triggers, "Workflow triggers")
    
    @classmethod
    def from_yaml(cls, file_path: str, yaml_content: str) -> "Workflow":
        """
        Create Workflow instance from YAML content.
        
        Args:
            file_path: Path to the workflow file
            yaml_content: Raw YAML content
            
        Returns:
            Workflow instance
        """
        try:
            with SimpleTimer(f"Parsing workflow {file_path}"):
                parsed = yaml.safe_load(yaml_content)
                
                if not parsed or not isinstance(parsed, dict):
                    # Return minimal workflow for invalid YAML
                    return cls(
                        name="Invalid Workflow",
                        file_path=file_path,
                        content=yaml_content,
                        jobs=[],
                        triggers=[]
                    )
                
                # Parse jobs
                jobs = []
                for job_name, job_config in parsed.get('jobs', {}).items():
                    if not isinstance(job_config, dict):
                        continue
                        
                    job = Job(
                        name=job_name,
                        runs_on=job_config.get('runs-on', 'ubuntu-latest'),
                        steps=job_config.get('steps', []),
                        needs=job_config.get('needs', []) if isinstance(job_config.get('needs'), list) else 
                              [job_config.get('needs')] if job_config.get('needs') else [],
                        if_condition=job_config.get('if'),
                        strategy=job_config.get('strategy')
                    )
                    jobs.append(job)
                
                # Parse triggers
                triggers = []
                on_config = parsed.get('on', {})
                
                # Handle simple string triggers like 'on: push'
                if isinstance(on_config, str):
                    triggers.append(Trigger(event=on_config))
                # Handle list of triggers like 'on: [push, pull_request]'
                elif isinstance(on_config, list):
                    for event in on_config:
                        triggers.append(Trigger(event=event))
                # Handle complex trigger configuration
                elif isinstance(on_config, dict):
                    for event, config in on_config.items():
                        if isinstance(config, dict):
                            trigger = Trigger(
                                event=event,
                                branches=config.get('branches', []),
                                paths=config.get('paths', []),
                                types=config.get('types', [])
                            )
                        else:
                            trigger = Trigger(event=event)
                        triggers.append(trigger)
                
                return cls(
                    name=parsed.get('name', f'Workflow from {file_path}'),
                    file_path=file_path,
                    content=yaml_content,
                    jobs=jobs,
                    triggers=triggers
                )
                
        except Exception as e:
            # Return minimal workflow if parsing fails
            return cls(
                name=f"Parse Error: {str(e)[:50]}...",
                file_path=file_path,
                content=yaml_content,
                jobs=[],
                triggers=[]
            )
    
    def get_job_by_name(self, name: str) -> Optional[Job]:
        """Get job by name."""
        for job in self.jobs:
            if job.name == name:
                return job
        return None
    
    def has_caching(self) -> bool:
        """Check if workflow uses any caching."""
        for job in self.jobs:
            for step in job.steps:
                if "actions/cache" in str(step.get("uses", "")):
                    return True
        return False
    
    def has_docker_build(self) -> bool:
        """Check if workflow includes Docker builds."""
        for job in self.jobs:
            for step in job.steps:
                run_command = step.get("run", "")
                if "docker build" in run_command or "docker/build-push-action" in str(step.get("uses", "")):
                    return True
        return False


@dataclass
class JobRun:
    """Represents a single job run within a workflow run."""
    
    name: str
    status: str
    conclusion: str
    started_at: datetime
    completed_at: Optional[datetime]
    runner_name: str
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Get duration of the job run."""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None


@dataclass
class WorkflowRun:
    """Represents a single workflow run."""
    
    id: str
    workflow_id: str
    name: str
    status: str
    conclusion: str
    created_at: datetime
    updated_at: datetime
    run_started_at: Optional[datetime]
    jobs: List[JobRun]
    runner_type: str = "ubuntu-latest"
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Get total duration of the workflow run."""
        if self.run_started_at and self.updated_at:
            return self.updated_at - self.run_started_at
        return None
    
    @property
    def was_successful(self) -> bool:
        """Check if workflow run was successful."""
        return self.conclusion == "success"
    
    def get_job_run(self, job_name: str) -> Optional[JobRun]:
        """Get job run by name."""
        for job_run in self.jobs:
            if job_run.name == job_name:
                return job_run
        return None


@dataclass
class AnalysisContext:
    """Context information for workflow analysis."""
    
    repository: str
    workflows: List[Workflow]
    workflow_runs: List[WorkflowRun]
    config: Config
    analysis_date: datetime = field(default_factory=datetime.now)
    
    @property
    def total_workflows(self) -> int:
        """Get total number of workflows."""
        return len(self.workflows)
    
    @property
    def total_runs(self) -> int:
        """Get total number of workflow runs."""
        return len(self.workflow_runs)
    
    @property
    def average_run_duration(self) -> Optional[timedelta]:
        """Get average duration of workflow runs."""
        durations = [run.duration for run in self.workflow_runs if run.duration]
        if not durations:
            return None
        
        total_seconds = sum(d.total_seconds() for d in durations)
        average_seconds = total_seconds / len(durations)
        return timedelta(seconds=average_seconds)
    
    @property
    def success_rate(self) -> float:
        """Get success rate of workflow runs."""
        if not self.workflow_runs:
            return 0.0
        
        successful_runs = sum(1 for run in self.workflow_runs if run.was_successful)
        return successful_runs / len(self.workflow_runs)
    
    def get_runs_for_workflow(self, workflow_id: str) -> List[WorkflowRun]:
        """Get all runs for a specific workflow."""
        return [run for run in self.workflow_runs if run.workflow_id == workflow_id] 