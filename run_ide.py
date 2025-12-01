# File: run_ide.py (updated)
#!/usr/bin/env python3
"""
Runner script for NovaLang IDE
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check if PyQt6 is installed
try:
    from PyQt6.QtWidgets import QApplication
    HAS_PYQT6 = True
except ImportError:
    HAS_PYQT6 = False

if not HAS_PYQT6:
    print("=" * 60)
    print("ERROR: PyQt6 is not installed!")
    print("=" * 60)
    print("Please install PyQt6 using one of these commands:")
    print("  pip install PyQt6")
    print("  pip install -r requirements.txt")
    print("=" * 60)
    sys.exit(1)

from ide.novalang_ide import main

if __name__ == "__main__":
    main()