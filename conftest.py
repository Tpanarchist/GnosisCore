"""Global pytest configuration"""
import sys
import os
from pathlib import Path

# Ensure gnosiscore is importable
project_root = Path(__file__).parent.resolve()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"Test environment: Python path includes {project_root}")
