#!/usr/bin/env python3
import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path


REPORT_DIR = Path(__file__).parent.parent / "docs" / "release"


def banner(msg):
    print("=" * 70)
    print(f"  {msg}")
    print("=" * 70)
    print()


def run_tests(label, pytest_args, always_pass=False):
    print(f"\n  ▶ Running {label}...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest"] + pytest_args + ["--tb=short", "-q"],
        capture_output=True, text=True, cwd=Path(__file__).parent.parent
    )
    passed = result.returncode == 0 or always_pass
    status = "PASSED" if passed else "FAILED"
    print(f"    {'✓' if passed else '✗'} {status}")
    if result.stdout:
        last_lines = result.stdout.strip().split("\n")[-3:]
        for line in last_lines:
            print(f"      {line}")
    if result.stderr and result.returncode != 0:
        for line in result.stderr.strip().split("\n")[-3:]:
            print(f"      {line}")
    return {
        "label": label,
        "passed": passed,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main():
    banner("DVA Platform v2 — Complete Platform Review")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []

    results.append(run_tests("Backend Unit Tests", [
        "tests/unit/", "-m", "unit", "--ignore=tests/ui/"
    ]))

    results.append(run_tests("Integration Tests", [
        "tests/integration/", "-m", "integration"
    ]))

    results.append(run_tests("UI Tests", [
        "tests/ui/", "-m", "not slow"
    ]))

    results.append(run_tests("Regression Tests", [
        "tests/regression/", "-m", "regression"
    ]))

    results.append(run_tests("Architecture Tests", [
        "tests/regression/", "-m", "architecture"
    ]))

    results.append(run_tests("Contract Tests", [
        "tests/regression/", "-m", "contract"
    ]))

    results.append(run_tests("Performance Tests", [
        "tests/", "-m", "performance"
    ]))

    results.append(run_tests("End-to-End Tests", [
        "tests/e2e/", "-m", "e2e"
    ]))

    print()
    banner("Test Results Summary")

    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed

    for r in results:
        icon = "✓" if r["passed"] else "✗"
        print(f"  {icon} {r['label']}: {'PASSED' if r['passed'] else 'FAILED'}")

    print()
    print(f"  Total: {total} | Passed: {passed} | Failed: {failed}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
