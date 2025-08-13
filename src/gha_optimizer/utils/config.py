"""Configuration management for GHA-Optimizer."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class Config:
    """Configuration container for GHA-Optimizer."""

    def __init__(self, config_dict: Dict[str, Any]) -> None:
        self._config = config_dict

    @property
    def github_token(self) -> Optional[str]:
        """Get GitHub token from config or environment."""
        return self._config.get("github", {}).get("token") or os.getenv("GITHUB_TOKEN")

    @property
    def github_api_url(self) -> str:
        """Get GitHub API URL."""
        return str(self._config.get("github", {}).get("api_url", "https://api.github.com"))

    @property
    def ai_provider(self) -> str:
        """Get AI provider (anthropic only)."""
        return str(self._config.get("ai", {}).get("provider", "anthropic"))

    @property
    def ai_api_key(self) -> Optional[str]:
        """Get AI API key from config or environment."""
        ai_key = self._config.get("ai", {}).get("api_key")
        if ai_key:
            return str(ai_key)

        # Try environment variable for Anthropic
        if self.ai_provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")

        return None

    @property
    def ai_model(self) -> str:
        """Get AI model name."""
        default_models = {
            "anthropic": "claude-3-sonnet-20240229",
        }
        return str(
            self._config.get("ai", {}).get(
                "model", default_models.get(self.ai_provider, "claude-3-sonnet-20240229")
            )
        )

    @property
    def max_history_days(self) -> int:
        """Get maximum days of workflow history to analyze."""
        return int(self._config.get("analysis", {}).get("max_history_days", 30))

    @property
    def confidence_threshold(self) -> float:
        """Get confidence threshold for recommendations."""
        return float(self._config.get("analysis", {}).get("confidence_threshold", 0.7))

    @property
    def parallel_requests(self) -> int:
        """Get number of parallel requests to make."""
        return int(self._config.get("analysis", {}).get("parallel_requests", 5))

    @property
    def default_output_format(self) -> str:
        """Get default output format."""
        return str(self._config.get("output", {}).get("default_format", "markdown"))

    @property
    def include_code_examples(self) -> bool:
        """Whether to include code examples in output."""
        return bool(self._config.get("output", {}).get("include_code_examples", True))

    @property
    def generate_pr_descriptions(self) -> bool:
        """Whether to generate PR descriptions."""
        return bool(self._config.get("output", {}).get("generate_pr_descriptions", True))


def load_config(config_path: Optional[Path] = None) -> Config:
    """
    Load configuration from file or create default configuration.

    Args:
        config_path: Path to configuration file (optional)

    Returns:
        Config object with loaded or default configuration

    Raises:
        FileNotFoundError: If specified config file doesn't exist
        yaml.YAMLError: If config file has invalid YAML syntax
    """
    config_dict: Dict[str, Any] = {}

    if config_path:
        # Load from specified file
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f) or {}
    else:
        # Try to load from default locations
        default_paths = [
            Path.cwd() / "config.yml",
            Path.cwd() / "gha-optimizer.yml",
            Path.home() / ".gha-optimizer" / "config.yml",
            Path.home() / ".config" / "gha-optimizer" / "config.yml",
        ]

        for path in default_paths:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    config_dict = yaml.safe_load(f) or {}
                break

    # Apply default configuration
    default_config = {
        "github": {"api_url": "https://api.github.com"},
        "ai": {"provider": "anthropic", "model": "claude-3-sonnet-20240229"},
        "analysis": {
            "max_history_days": 30,
            "confidence_threshold": 0.7,
            "parallel_requests": 5,
        },
        "output": {
            "default_format": "markdown",
            "include_code_examples": True,
            "generate_pr_descriptions": True,
        },
    }

    # Merge default with loaded config
    merged_config = _deep_merge(default_config, config_dict)

    return Config(merged_config)


def _deep_merge(default: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.

    Args:
        default: Default configuration
        override: Override configuration

    Returns:
        Merged configuration dictionary
    """
    result = default.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value

    return result
