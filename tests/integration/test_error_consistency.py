import os
import pytest

if os.getenv("RUN_LIVE_TESTS") != "1":
    pytest.skip("Integration tests skipped (set RUN_LIVE_TESTS=1 to enable)", allow_module_level=True)

import sys
import json
from typing import Dict, Any
from datetime import datetime

# add repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gmail_check_skill import GmailCheckSkill
from ldr_compat import ExecutionContext

def test_error_scenarios_integration():
    skill = GmailCheckSkill()
    ctx = ExecutionContext()

    # replicate the original tests but avoid writing files into repo root
    results = {}

    result1 = skill.execute(ctx, username="", app_password="", email_filters={"from": ["test@example.com"]})
    results['missing_auth'] = result1

    result2 = skill.execute(ctx, username="testuser@gmail.com", app_password="test_password", email_filters={})
    results['empty_filters'] = result2

    result3 = skill.execute(ctx, username="testuser@gmail.com", app_password="test_password", email_filters=None)
    results['none_filters'] = result3

    result4 = skill.execute(ctx, username="invalid@gmail.com", app_password="wrong_password", email_filters={"from": ["test@example.com"]})
    results['invalid_auth'] = result4

    result5 = skill.execute(ctx, username="", app_password="", email_filters={"from": ["test@example.com"]}, background_mode=True)
    results['background_no_auth'] = result5

    # basic assertions about structure
    for key, res in results.items():
        assert isinstance(res, dict)
        assert 'success' in res and 'data' in res and 'error' in res


