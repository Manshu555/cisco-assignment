"""
Pytest configuration.

Putting the project root on sys.path here means the test modules can simply
`import eligibility` / `import cli`, instead of each repeating a
`sys.path.insert(...)` preamble. pytest imports this file before collecting
tests, and `pytest.ini` pins the rootdir so it is found from any working
directory.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
