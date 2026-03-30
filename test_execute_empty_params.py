from gmail_check_skill import GmailCheckSkill
from ldr_compat import ExecutionContext


def test_execute_missing_credentials_returns_empty_result():
    skill = GmailCheckSkill()
    ctx = ExecutionContext()
    result = skill.execute(ctx, username=None, app_password=None, email_filters={})
    assert isinstance(result, dict)
    assert 'success' in result
    assert 'data' in result
    assert 'error' in result
    # For missing credentials we expect success True (empty result) and error to be None
    assert result['success'] is True
    assert result['error'] is None
