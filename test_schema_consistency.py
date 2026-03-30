from gmail_check_skill import GmailCheckSkill


def test_schema_has_required_fields():
    skill = GmailCheckSkill()
    schema = skill.get_openai_schema()
    assert 'function' in schema
    func = schema['function']
    assert 'parameters' in func
    params = func['parameters']
    required = params.get('required', [])
    for key in ['username', 'app_password', 'email_filters']:
        assert key in params['properties']
        assert key in required
