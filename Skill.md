# Skill: Gmail Check

This `Skill.md` contains the minimal required schema and examples as required by SKILL_GENERATION_RULES.md.

## Input schema (JSON Schema)

```json
{
  "type": "object",
  "properties": {
    "username": {"type": "string"},
    "app_password": {"type": "string"},
    "email_filters": {"type": "object"},
    "check_interval": {"type": "integer"},
    "background_mode": {"type": "boolean"},
    "max_emails": {"type": "integer"},
    "days_back": {"type": "integer"},
    "time_range_hours": {"type": "integer"},
    "use_cache": {"type": "boolean"}
  },
  "required": ["username", "app_password", "email_filters"]
}
```

## Output schema

All outputs follow the canonical format:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

## Example CLI usage

```bash
python main.py --username user@gmail.com --app_password xxxxx --email_filters '{"sender@example.com": ["urgent"]}'
```

## MCP usage

The MCP tool returns a JSON string; the server wraps it as required by the MCP protocol. See `README.md` for instructions on running MCP and creating local inspector configuration from the example file.
