#!/usr/bin/env python
"""Test all example files to ensure they work correctly."""

import subprocess
import sys
from pathlib import Path


def run_example(example_file: Path) -> tuple[bool, str]:
    """Run an example file and return success status and output."""
    try:
        result = subprocess.run(
            [sys.executable, str(example_file)], capture_output=True, text=True, timeout=30
        )
        success = result.returncode == 0
        output = result.stdout if success else result.stderr
        return success, output
    except Exception as e:
        return False, str(e)


def main():
    examples_dir = Path("examples")
    example_files = [
        "dataclass_example.py",
        "pydantic_example.py",
        "dataclass_mock_example.py",
        "pydantic_mock_example.py",
    ]

    all_passed = True

    for example_file in example_files:
        file_path = examples_dir / example_file
        if not file_path.exists():
            print(f"❌ {example_file}: File not found")
            all_passed = False
            continue

        print(f"\n{'='*60}")
        print(f"Running {example_file}...")
        print("=" * 60)

        success, output = run_example(file_path)

        if success:
            print(f"✅ {example_file}: PASSED")
            if output:
                print("Output:")
                print(output)
        else:
            print(f"❌ {example_file}: FAILED")
            print("Error:")
            print(output)
            all_passed = False

    print(f"\n{'='*60}")
    if all_passed:
        print("✅ All examples passed!")
    else:
        print("❌ Some examples failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
