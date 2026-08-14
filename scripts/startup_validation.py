#!/usr/bin/env python3
"""Startup validation — validates system before launching DVA UI."""
import sys
from pathlib import Path

def main():
    print("DVA Platform — Startup Validation")
    print("=" * 50)
    print()
    
    errors = []
    
    # Check Python version
    if sys.version_info < (3, 12):
        errors.append(f"Python 3.12+ required (found {sys.version_info.major}.{sys.version_info.minor})")
    
    # Check critical imports
    try:
        import nicegui
        print(f"  ✓ NiceGUI {nicegui.__version__}")
    except ImportError:
        errors.append("NiceGUI not installed")
    
    try:
        import polars
        print(f"  ✓ Polars {polars.__version__}")
    except ImportError:
        errors.append("Polars not installed")
    
    # Check home directory
    home = Path.home()
    dva_dir = home / ".dva"
    try:
        dva_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ DVA config directory: {dva_dir}")
    except PermissionError:
        errors.append(f"Cannot create DVA config directory at {dva_dir}")
    
    # Check port availability
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("0.0.0.0", 8080))
        sock.close()
        print("  ✓ Port 8080 available")
    except OSError:
        errors.append("Port 8080 is already in use")
    
    print()
    if errors:
        print("Startup validation FAILED:")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    else:
        print("Startup validation PASSED")
        print("Ready to launch DVA Platform.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
