#!/usr/bin/env python3
"""
Simple test script to verify the CLI interface works.
Run this to test the basic CLI functionality before installation.
"""

import sys
from pathlib import Path

# Add src to Python path for testing
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from gha_optimizer.cli.main import cli


def test_cli():
    """Test basic CLI functionality."""
    print("Testing GHA-Optimizer CLI...")
    
    # Test help command
    print("\n1. Testing help command:")
    try:
        cli(["--help"], standalone_mode=False)
        print("✅ Help command works")
    except SystemExit:
        print("✅ Help command works (expected SystemExit)")
    except Exception as e:
        print(f"❌ Help command failed: {e}")
    
    # Test version command
    print("\n2. Testing version command:")
    try:
        cli(["--version"], standalone_mode=False)
        print("✅ Version command works")
    except SystemExit:
        print("✅ Version command works (expected SystemExit)")
    except Exception as e:
        print(f"❌ Version command failed: {e}")
    
    # Test scan command help
    print("\n3. Testing scan command help:")
    try:
        cli(["scan", "--help"], standalone_mode=False)
        print("✅ Scan help works")
    except SystemExit:
        print("✅ Scan help works (expected SystemExit)")
    except Exception as e:
        print(f"❌ Scan help failed: {e}")
    
    # Test scan command with invalid repo (should show error gracefully)
    print("\n4. Testing scan with invalid repository format:")
    try:
        cli(["scan", "invalid-repo"], standalone_mode=False)
        print("✅ Error handling works")
    except SystemExit:
        print("❌ Unexpected SystemExit on error")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("\n🎉 CLI basic functionality test completed!")
    print("\nTo install and use:")
    print("1. pip install -e .")
    print("2. gha-optimizer --help")
    print("3. gha-optimizer scan microsoft/vscode")


if __name__ == "__main__":
    test_cli() 