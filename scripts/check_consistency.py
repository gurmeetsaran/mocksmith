#!/usr/bin/env python3
"""Check consistency between pre-commit hooks, Makefile, and GitHub Actions."""

import re
import sys
from pathlib import Path

import yaml


def load_pre_commit_config():
    """Load and parse pre-commit configuration."""
    with open(".pre-commit-config.yaml") as f:
        config = yaml.safe_load(f)

    tools = {}
    for repo in config.get("repos", []):
        for hook in repo.get("hooks", []):
            hook_id = hook["id"]
            args = hook.get("args", [])

            # Map pre-commit hook IDs to tool names
            if hook_id == "black":
                tools["black"] = {"args": args, "files": "src tests"}
            elif hook_id == "isort":
                tools["isort"] = {"args": args, "files": "src tests"}
            elif hook_id == "ruff":
                tools["ruff"] = {"args": args, "files": "src tests"}
            elif hook_id == "pyright":
                tools["pyright"] = {"args": args, "files": args[-1] if args else ""}

    return tools


def load_makefile_commands():
    """Parse Makefile to extract commands."""
    with open("Makefile") as f:
        content = f.read()

    commands = {}

    # Extract lint commands
    lint_section = re.search(r"lint:\n((?:\t.*\n)+)", content)
    if lint_section:
        lint_commands = lint_section.group(1).strip().split("\n")
        for cmd in lint_commands:
            cmd = cmd.strip()
            if "ruff check" in cmd:
                commands["ruff_lint"] = cmd
            elif "pyright" in cmd:
                commands["pyright_lint"] = cmd

    # Extract format commands
    format_section = re.search(r"format:\n((?:\t.*\n)+)", content)
    if format_section:
        format_commands = format_section.group(1).strip().split("\n")
        for cmd in format_commands:
            cmd = cmd.strip()
            if "black" in cmd:
                commands["black_format"] = cmd
            elif "isort" in cmd:
                commands["isort_format"] = cmd
            elif "ruff check --fix" in cmd:
                commands["ruff_format"] = cmd

    # Extract check-all commands
    check_section = re.search(r"check-all:\n((?:\t.*\n)+)", content)
    if check_section:
        check_commands = check_section.group(1).strip().split("\n")
        for cmd in check_commands:
            cmd = cmd.strip()
            if "black --check" in cmd:
                commands["black_check"] = cmd
            elif "isort --check-only" in cmd:
                commands["isort_check"] = cmd
            elif "ruff check" in cmd and "--fix" not in cmd:
                commands["ruff_check"] = cmd
            elif "pyright" in cmd:
                commands["pyright_check"] = cmd

    return commands


def load_github_actions():
    """Parse GitHub Actions workflow files."""
    commands = {}

    workflow_file = Path(".github/workflows/code-quality.yml")
    if workflow_file.exists():
        with open(workflow_file) as f:
            workflow = yaml.safe_load(f)

        for job in workflow.get("jobs", {}).values():
            for step in job.get("steps", []):
                if "run" in step:
                    run_commands = step["run"].strip().split("\n")
                    for cmd in run_commands:
                        cmd = cmd.strip()
                        if "black --check" in cmd:
                            commands["black"] = cmd
                        elif "isort --check-only" in cmd:
                            commands["isort"] = cmd
                        elif "ruff check" in cmd:
                            commands["ruff"] = cmd
                        elif "pyright" in cmd and "poetry run" in cmd:
                            commands["pyright"] = cmd

    return commands


def check_consistency():
    """Check consistency between all configurations."""
    print("🔍 Checking consistency between pre-commit, Makefile, and GitHub Actions...\n")

    # Load configurations
    pre_commit = load_pre_commit_config()
    makefile = load_makefile_commands()
    github_actions = load_github_actions()

    issues = []

    # Check Black
    print("📝 Checking Black configuration:")
    black_precommit = "--line-length=100" in " ".join(pre_commit.get("black", {}).get("args", []))
    black_makefile_check = "black --check src tests" in makefile.get("black_check", "")
    black_github = "black --check src tests" in github_actions.get("black", "")

    print(f"  Pre-commit: {'✓' if black_precommit else '✗'} (line-length=100)")
    print(f"  Makefile check-all: {'✓' if black_makefile_check else '✗'}")
    print(f"  GitHub Actions: {'✓' if black_github else '✗'}")

    if not (black_precommit and black_makefile_check and black_github):
        issues.append("Black configuration is inconsistent")

    # Check isort
    print("\n📝 Checking isort configuration:")
    isort_precommit = "--profile=black" in " ".join(pre_commit.get("isort", {}).get("args", []))
    isort_makefile_check = "isort --check-only src tests" in makefile.get("isort_check", "")
    isort_github = "isort --check-only src tests" in github_actions.get("isort", "")

    print(f"  Pre-commit: {'✓' if isort_precommit else '✗'} (profile=black)")
    print(f"  Makefile check-all: {'✓' if isort_makefile_check else '✗'}")
    print(f"  GitHub Actions: {'✓' if isort_github else '✗'}")

    if not (isort_precommit and isort_makefile_check and isort_github):
        issues.append("isort configuration is inconsistent")

    # Check Ruff
    print("\n📝 Checking Ruff configuration:")
    ruff_precommit = "ruff" in pre_commit
    ruff_makefile_lint = "ruff check src tests" in makefile.get("ruff_lint", "")
    ruff_makefile_check = "ruff check src tests" in makefile.get("ruff_check", "")
    ruff_github = "ruff check src tests" in github_actions.get("ruff", "")

    print(f"  Pre-commit: {'✓' if ruff_precommit else '✗'}")
    print(f"  Makefile lint: {'✓' if ruff_makefile_lint else '✗'}")
    print(f"  Makefile check-all: {'✓' if ruff_makefile_check else '✗'}")
    print(f"  GitHub Actions: {'✓' if ruff_github else '✗'}")

    if not (ruff_precommit and ruff_makefile_lint and ruff_makefile_check and ruff_github):
        issues.append("Ruff configuration is inconsistent")

    # Check Pyright
    print("\n📝 Checking Pyright configuration:")
    pyright_precommit = "pyright" in pre_commit
    pyright_precommit_src_only = "src/" in " ".join(pre_commit.get("pyright", {}).get("args", []))
    pyright_makefile = "pyright" in makefile.get("pyright_lint", "")
    pyright_github = "pyright" in github_actions.get("pyright", "")

    src_msg = "(src/ only)" if pyright_precommit_src_only else "(all files)"
    print(f"  Pre-commit: {'✓' if pyright_precommit else '✗'} {src_msg}")
    print(f"  Makefile: {'✓' if pyright_makefile else '✗'} (all files)")
    print(f"  GitHub Actions: {'✓' if pyright_github else '✗'} (all files)")

    if pyright_precommit_src_only:
        issues.append(
            "Pyright in pre-commit only checks 'src/' but "
            "Makefile and GitHub Actions check all files"
        )

    # Summary
    print("\n" + "=" * 60)
    if issues:
        print("❌ Found inconsistencies:")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print("✅ All configurations are consistent!")
        return 0


def suggest_fixes():
    """Suggest fixes for common issues."""
    print("\n💡 Suggested fixes:")
    print("1. Update pre-commit pyright to check all files:")
    print("   Change: args: [--pythonversion=3.8, src/]")
    print("   To:     args: [--pythonversion=3.8]")
    print("         pass_filenames: false")
    print("\n2. Ensure all tools use the same file targets (src tests)")
    print("\n3. Run 'pre-commit autoupdate' periodically to keep hook versions current")


if __name__ == "__main__":
    exit_code = check_consistency()
    if exit_code != 0:
        suggest_fixes()
    sys.exit(exit_code)
