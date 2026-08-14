#!/usr/bin/env python3
"""Environment validation — checks system prerequisites for DVA."""
import sys
import os
from pathlib import Path

CHECKS = []

def check(name, fn):
    CHECKS.append((name, fn))

def run_checks():
    print("DVA Platform — Environment Validation")
    print("=" * 50)
    print()
    
    all_pass = True
    for name, fn in CHECKS:
        try:
            result = fn()
            if result is True:
                print(f"  ✓ {name}")
            else:
                print(f"  ✗ {name}: {result}")
                all_pass = False
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            all_pass = False
    
    print()
    if all_pass:
        print("Environment validation PASSED ✓")
        return 0
    else:
        print("Environment validation FAILED ✗")
        return 1

check("Python version", lambda: sys.version_info >= (3, 12) or f"Python 3.12+ required, found {sys.version}")

check("Home directory writable", lambda: os.access(Path.home(), os.W_OK) or "Home directory not writable")

dva_dir = Path.home() / ".dva"
check("DVA config directory", lambda: (dva_dir.exists() or dva_dir.mkdir(parents=True, exist_ok=True) or True) or True)

check("Temp directory writable", lambda: os.access("/tmp" if sys.platform != "win32" else os.environ.get("TEMP", "C:\\Temp"), os.W_OK) or "Temp directory not writable")

if __name__ == "__main__":
    sys.exit(run_checks())
