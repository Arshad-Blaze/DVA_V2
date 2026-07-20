#!/usr/bin/env python3
"""Dependency checker — validates installed package versions against requirements."""
import sys
import importlib.metadata

REQUIRED = {
    "nicegui": ("1.4.0", None),
    "polars": ("0.20.0", None),
    "duckdb": ("0.9.0", None),
    "pyarrow": ("14.0.0", None),
}

def check_dependencies():
    all_ok = True
    print("Checking dependencies...")
    print()
    
    for pkg, (min_ver, max_ver) in REQUIRED.items():
        try:
            ver = importlib.metadata.version(pkg)
            ok = True
            msg = f"  {pkg}: installed {ver}"
            if min_ver and ver < min_ver:
                msg += f" (below minimum {min_ver})"
                ok = False
            if max_ver and ver > max_ver:
                msg += f" (exceeds maximum {max_ver})"
                ok = False
            if ok:
                msg += " ✓"
            else:
                all_ok = False
            print(msg)
        except importlib.metadata.PackageNotFoundError:
            print(f"  {pkg}: NOT INSTALLED ✗")
            all_ok = False
    
    python_ver = sys.version_info
    print(f"\n  Python: {sys.version.split()[0]}")
    if python_ver.major < 3 or (python_ver.major == 3 and python_ver.minor < 12):
        print("    ✗ Python 3.12+ required")
        all_ok = False
    else:
        print("    ✓")
    
    print()
    if all_ok:
        print("All dependencies satisfied ✓")
        return 0
    else:
        print("Some dependencies need attention ✗")
        return 1

if __name__ == "__main__":
    sys.exit(check_dependencies())
