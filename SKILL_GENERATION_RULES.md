AI-SKILL & MCP GENERATION RULES (v4.1.1)

## Purpose

Definitive, executable instructions for generating AI-native skills with MCP and CLI support.

## 0. Naming Conventions

{name}: lowercase, underscore-separated (e.g., pdf_merger)
{tool_name}: MUST equal {name}
{Name}: Title Case (e.g., PDF Merger)
{class_name}: PascalCase (e.g., PdfMerger)

## 1. Directory Structure

```
{name}/
├── main.py
├── {name}_skill.py
├── Skill.md
├── requirements.txt
├── tests/
│   ├── __init__.py
│   └── test_{name}.py
├── .gitignore
└── README.md
```

## 2. Core Contracts

### 2.1 Output Schema (MANDATORY)

```
{
  "success": true,
  "data": {},
  "error": null
}
```

### 2.2 Error Schema

```
{
  "success": false,
  "data": null,
  "error": "Error message"
}
```

### 2.3 MCP Return Format (MANDATORY)

All MCP responses MUST follow:

```
{
  "content": [
    {
      "type": "text",
      "text": "<JSON string>"
    }
  ]
}
```
The MCP response MUST be a JSON-serialized string. The FastMCP framework will automatically wrap it into the required content block.

### 2.4 Input Schema (MANDATORY)

The input schema MUST be defined in:

1. main.py (Typer parameters)
2. Skill.md (JSON schema)

The parameter names, types, and required/optional status MUST match exactly across all three:
- CLI (Typer)
- MCP tool definition
- Skill.md JSON schema

## 3. Core Implementation Template

```python
# <file path="{name}_skill.py">
import sys
import logging
import inspect
from typing import Any

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)

class {class_name}:

    async def execute(self, **kwargs) -> dict:
        try:
            result = self._process(**kwargs)
            if inspect.iscoroutine(result):
                result = await result
            return {
                "success": True,
                "data": result,
                "error": None
            }
        except Exception as e:
            logger.exception("Execution failed")
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }

    def _process(self, **kwargs) -> Any:
        raise NotImplementedError
# </file>
```

## 4. Entry Point Template

```python
# <file path="main.py">
import sys
import json
import asyncio
import typer
from mcp.server.fastmcp import FastMCP
from {name}_skill import {class_name}

app = typer.Typer()
mcp = FastMCP("{Name}")
impl = {class_name}()

_is_cli = len(sys.argv) > 1

def format_mcp(result: dict):
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result)
            }
        ]
    }

@mcp.tool()
@app.command()
def {tool_name}(
    param1: str = typer.Argument(..., help="Required parameter"),
    optional_param: str = typer.Option(None, help="Optional parameter")
):
    """Tool description"""
    try:
        if asyncio.iscoroutinefunction(impl.execute):
            result = asyncio.run(impl.execute(
                param1=param1,
                optional_param=optional_param
            ))
        else:
            result = impl.execute(
                param1=param1,
                optional_param=optional_param
            )

        if _is_cli:
            typer.echo(json.dumps(result, indent=2))
        else:
            # FastMCP automatically wraps the returned string into the MCP content/text format.
            return json.dumps(result)

    except Exception as e:
        error = {
            "success": False,
            "data": None,
            "error": str(e)
        }

        if _is_cli:
            typer.echo(json.dumps(error), err=True)
            raise typer.Exit(1)
        else:
            return return json.dumps(error)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        app()
    else:
        mcp.run(transport="stdio")
# </file>
```

## 5. Parameter Rules

Required → typer.Argument(...)

Optional → typer.Option(...)

Must match schema EXACTLY

## 6. Testing Requirements

MUST include CLI test

MUST include MCP test

MUST pass pytest

## 7. Documentation Requirements

Skill.md MUST include:

- Input schema
- Output schema
- Example CLI usage
- Example MCP request/response

## 8. Mandatory Rules

- All outputs MUST follow output schema
- MCP MUST return content format
- CLI MUST output JSON
- No logs in stdout
- Logs MUST go to stderr

## 9. Optional Spec Support

```
{
  "name": "...",
  "tools": [...]
}
```

If provided, MUST be used as source of truth.

CLI output MUST be valid JSON with no additional text or formatting.

Field names in output schema MUST NOT be changed.