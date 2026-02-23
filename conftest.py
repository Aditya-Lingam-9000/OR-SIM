"""conftest.py — root pytest configuration.

Adds the project root to sys.path so that `backend.*` imports work
when running pytest from any directory.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
