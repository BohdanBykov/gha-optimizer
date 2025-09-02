#!/usr/bin/env python3
"""
Update documentation version to match package version.

This script ensures that documentation files reference the correct version
and provides a GitHub repository link for version-specific documentation.
"""

import re
import sys
from pathlib import Path
from datetime import datetime


def get_package_version() -> str:
    """Get version from pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(r'version = "([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    
    return match.group(1)


def update_optimization_patterns_version(version: str) -> None:
    """Update the optimization patterns documentation with current version."""
    docs_path = Path(__file__).parent.parent / "src" / "gha_optimizer" / "docs" / "optimization-patterns.md"
    
    with open(docs_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Update version line
    content = re.sub(
        r'\*\*Version:\*\* [^\n]+',
        f'**Version:** {version}',
        content
    )
    
    # Update last updated date
    current_date = datetime.now().strftime("%B %Y")
    content = re.sub(
        r'\*\*Last Updated:\*\* [^\n]+',
        f'**Last Updated:** {current_date}',
        content
    )
    
    with open(docs_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ Updated {docs_path} to version {version}")


def main() -> None:
    """Main function to update documentation versions."""
    try:
        version = get_package_version()
        print(f"📦 Current package version: {version}")
        
        update_optimization_patterns_version(version)
        
        print(f"""
🎯 Documentation Versioning Complete

Version {version} documentation is now ready. When users run:
  gha-optimizer scan owner/repo

The AI analyzer will:
1. Load docs/optimization-patterns.md 
2. Verify version matches tool version ({version})
3. Use version-specific patterns and guidelines
4. Reference: https://github.com/BohdanBykov/gha-optimizer/blob/v{version}/docs/optimization-patterns.md

This ensures consistent, version-aligned recommendations.
""")
        
    except Exception as e:
        print(f"❌ Error updating documentation versions: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
