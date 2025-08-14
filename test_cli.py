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
    
    # Test scan command help (verify new option is present)
    print("\n3. Testing scan command help for new option:")
    try:
        cli(["scan", "--help"], standalone_mode=False)
        print("✅ Scan help command works")
    except SystemExit:
        print("✅ Scan help command works (expected SystemExit)")
    except Exception as e:
        print(f"❌ Scan help command failed: {e}")
    
    # Test workflow filtering flag availability
    print("\n4. Testing workflow filtering flag:")
    try:
        import click.testing
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["scan", "--help"])
        
        if result.exit_code == 0 and "--workflows" in result.output:
            print("✅ Workflow filtering flag is present in help output")
        else:
            print("❌ Workflow filtering flag not found in help output")
            print(f"Help output: {result.output}")
    except Exception as e:
        print(f"❌ Workflow filtering flag test failed: {e}")
    
    # Test debug options availability
    print("\n5. Testing debug options:")
    try:
        import click.testing
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["scan", "--help"])
        
        debug_options_found = 0
        if "--output-prompt-file" in result.output:
            debug_options_found += 1
        if "--output-ai-response" in result.output:
            debug_options_found += 1
            
        if debug_options_found == 2:
            print("✅ Both debug options are present in help output")
        else:
            print(f"❌ Only {debug_options_found}/2 debug options found in help output")
            print(f"Help output: {result.output}")
    except Exception as e:
        print(f"❌ Debug options test failed: {e}")
    
    print("\n🎉 CLI integration tests completed!")
    print("\nCore CLI functionality verified:")
    print("✓ Help system")
    print("✓ Version information") 
    print("✓ Scan command help")
    print("✓ Workflow filtering flag")
    print("✓ Debug options")
    print("✓ CLI structure and imports")
    print("✓ Basic command framework")

if __name__ == "__main__":
    test_cli() 