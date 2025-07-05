#!/usr/bin/env python
"""Test runner for GnosisCore that ensures proper imports"""
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Verify gnosiscore can be imported
try:
    import gnosiscore
    print(f"✓ GnosisCore found at: {gnosiscore.__file__ if hasattr(gnosiscore, '__file__') else 'built-in'}")
except ImportError as e:
    print(f"✗ Failed to import gnosiscore: {e}")
    sys.exit(1)

# Run pytest
import pytest

if __name__ == "__main__":
    sys.exit(pytest.main([
        "-v",
        "--tb=short",
        "--color=yes",
        "tests/"
    ]))
