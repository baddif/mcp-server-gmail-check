import os
import pytest

if os.getenv("RUN_LIVE_TESTS") != "1":
    pytest.skip("Integration tests skipped (set RUN_LIVE_TESTS=1 to enable)", allow_module_level=True)

# Real test code lives in top-level test_background_mode.py; this wrapper only enables it under env flag.
from .... import test_background_mode as _bg

