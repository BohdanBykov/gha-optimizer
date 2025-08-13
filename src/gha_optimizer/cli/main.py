#!/usr/bin/env python3
"""
GHA-Optimizer CLI - Main command-line interface

Commands:
- scan: Analyze workflows, check patterns, and generate optimization report
- apply: Open pull requests based on scan findings
"""

import sys
from pathlib import Path
from typing import Optional

import click

from .. import __version__
from ..utils.config import load_config
from ..utils.logger import setup_logger


@click.group()
@click.version_option(version=__version__, prog_name="gha-optimizer")
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to configuration file",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
@click.pass_context
def cli(ctx: click.Context, config: Optional[Path], verbose: bool) -> None:
    """
    GHA-Optimizer: AI-Powered GitHub Actions Workflow Optimization Tool

    Analyze GitHub Actions workflows and get actionable optimization recommendations
    with quantified impact metrics.

    \b
    Examples:
        gha-optimizer scan microsoft/vscode
        gha-optimizer apply microsoft/vscode --priority high
    """
    # Set up logging
    logger = setup_logger(verbose=verbose)

    # Load configuration
    try:
        app_config = load_config(config)
        ctx.ensure_object(dict)
        ctx.obj["config"] = app_config
        ctx.obj["logger"] = logger
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)


@cli.command()
@click.argument("repository")
@click.option(
    "--token",
    envvar="GITHUB_TOKEN",
    help="GitHub personal access token",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file for detailed report",
)
@click.option(
    "--format",
    type=click.Choice(["markdown", "html", "json"]),
    default="markdown",
    help="Output format for the report",
)
@click.option(
    "--max-history-days",
    type=int,
    default=30,
    help="Maximum days of workflow history to analyze",
)
@click.option(
    "--output-prompt-file",
    type=click.Path(path_type=Path),
    help="Debug: Save AI prompt to file without making API call",
)
@click.pass_context
def scan(
    ctx: click.Context,
    repository: str,
    token: Optional[str],
    output: Optional[Path],
    format: str,
    max_history_days: int,
    output_prompt_file: Optional[Path],
) -> None:
    """
    Analyze GitHub repository workflows and generate optimization report.

    Scans workflows, checks for optimization patterns, analyzes run statistics,
    and generates a comprehensive report with improvement recommendations.

    REPOSITORY: GitHub repository in format 'owner/repo'

    \b
    Examples:
        gha-optimizer scan microsoft/vscode
        gha-optimizer scan --output report.html microsoft/vscode
    """
    logger = ctx.obj["logger"]
    config = ctx.obj["config"]

    click.echo(f"🔍 Analyzing repository: {repository}")

    # Import here to avoid circular imports
    from ..commands.scan import ScanCommand

    try:
        scan_cmd = ScanCommand(config=config, logger=logger)
        result = scan_cmd.execute(
            repository=repository,
            github_token=token,
            output_file=output,
            output_format=format,
            max_history_days=max_history_days,
            output_prompt_file=output_prompt_file,
        )

        if result.success:
            click.echo(f"✅ Analysis completed!")
            click.echo(f"📈 Found {len(result.recommendations)} optimization opportunities")
            click.echo(f"💰 Potential monthly savings: ${result.estimated_savings:.0f}")
            click.echo(f"⏱️  Potential time savings: {result.time_savings:.1f} minutes per run")

            if output:
                click.echo(f"📄 Detailed report saved to: {output}")
        else:
            click.echo(f"❌ Analysis failed: {result.error}", err=True)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Scan command failed: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("repository")
@click.option(
    "--token",
    envvar="GITHUB_TOKEN",
    help="GitHub personal access token",
)
@click.option(
    "--priority",
    type=click.Choice(["high", "medium", "low", "all"]),
    default="high",
    help="Priority level of optimizations to apply",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be applied without creating PRs",
)
@click.pass_context
def apply(
    ctx: click.Context,
    repository: str,
    token: Optional[str],
    priority: str,
    dry_run: bool,
) -> None:
    """
    Open pull requests with optimizations based on scan findings.

    Creates GitHub pull requests with workflow optimizations
    based on previously identified improvement opportunities.

    REPOSITORY: GitHub repository in format 'owner/repo'

    \b
    Examples:
        gha-optimizer apply microsoft/vscode
        gha-optimizer apply --priority all --dry-run microsoft/vscode
    """
    logger = ctx.obj["logger"]
    config = ctx.obj["config"]

    if dry_run:
        click.echo(f"🧪 Dry run: Showing optimizations for {repository}")
    else:
        click.echo(f"🚀 Creating pull requests for {repository}")

    # Import here to avoid circular imports
    from ..commands.apply import ApplyCommand

    try:
        apply_cmd = ApplyCommand(config=config, logger=logger)
        result = apply_cmd.execute(
            repository=repository,
            github_token=token,
            priority=priority,
            dry_run=dry_run,
        )

        if result.success:
            if dry_run:
                click.echo(f"✅ Would create {len(result.pull_requests)} pull requests")
                click.echo(f"💰 Estimated monthly savings: ${result.estimated_savings:.0f}")
            else:
                click.echo(f"✅ Created {len(result.pull_requests)} pull requests")
                for pr_url in result.pull_requests:
                    click.echo(f"🔗 {pr_url}")
        else:
            click.echo(f"❌ Apply failed: {result.error}", err=True)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Apply command failed: {e}")
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI application."""
    cli()


if __name__ == "__main__":
    main()
