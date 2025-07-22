#!/usr/bin/env python3
"""
Test runner script for the backup system.
Can be used locally to run tests before pushing to CI.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print("✓ PASSED")
        if result.stdout:
            print("Output:", result.stdout[:500])  # Limit output
        return True
    except subprocess.CalledProcessError as e:
        print("✗ FAILED")
        if e.stdout:
            print("Output:", e.stdout[:500])
        if e.stderr:
            print("Error:", e.stderr[:500])
        return False


def main():
    """Run all tests and checks."""
    print("File Backup System - Local Test Runner")
    print("=====================================")

    # Ensure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Use virtual environment python if available
    if os.path.exists(os.path.join(".venv", "Scripts", "python.exe")):
        python_cmd = os.path.join(".venv", "Scripts", "python.exe")
    elif os.path.exists(os.path.join(".venv", "Scripts", "python.exe")):
        python_cmd = os.path.join(".venv", "Scripts", "python.exe")
    else:
        python_cmd = "python"

    checks = [
        (f"{python_cmd} -m flake8 . --exclude=.venv", "Code Linting (flake8)"),
        (f"{python_cmd} -m black --check .", "Code Formatting (black)"),
        (f"{python_cmd} -m pytest test_files/ -v", "Unit Tests"),
        (
            f"{python_cmd} -c \"import main; print('Main module imports successfully')\"",
            "Import Test",
        ),
    ]

    results = []
    for command, description in checks:
        success = run_command(command, description)
        results.append((description, success))

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    for description, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{description:<30} {status}")

    failed_count = sum(1 for _, success in results if not success)

    if failed_count == 0:
        print("\n🎉 All checks passed! Ready to push to CI.")
        return 0
    else:
        print(f"\n❌ {failed_count} check(s) failed. Please fix before pushing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
