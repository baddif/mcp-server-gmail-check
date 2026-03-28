# AI-SKILL & MCP GENERATION RULES (v3.1.0)

**Purpose**: Instructions for generating AI-native skills with MCP, CLI, and Metadata.
**Standard**: MCP 1.0+ | Python 3.10+ | Typer (CLI)

---

## 1. Output File Structure
When generating a skill, you MUST output these files using `<file path="...">` tags.

### 1.1 Core Implementation (`{name}_skill.py`)
Keep logic decoupled. Use `sys.stderr` for any logging to avoid corrupting MCP/CLI streams.

```python
# <file path="{name}_skill.py">
import sys
from typing import Any

class SkillImplementation:
    def execute(self, **kwargs) -> Any:
        # Core logic here
        pass
# </file>
```

### 1.2 MCP & CLI Entry Point (`main.py`)
This file serves as both the MCP Server and the CLI interface. It MUST detect whether it is running with CLI args or as an MCP server (stdio).

```python
# <file path="main.py">
import asyncio
import typer
from mcp.server.fastmcp import FastMCP
from {name}_skill import SkillImplementation

app = typer.Typer()
mcp = FastMCP("{Display_Name}")
impl = SkillImplementation()

@mcp.tool()
@app.command()
def {tool_name}(param1: str = typer.Argument(..., help="Description")):
    """Tool description for both MCP and CLI."""
    try:
        result = impl.execute(param1=param1)
        # MCP uses return; CLI uses print
        if getattr(mcp, "is_running_as_tool", False):
            return f"Success: {result}"
        typer.echo(result)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        if getattr(mcp, "is_running_as_tool", False):
            return f"Error: {e}"

if __name__ == "__main__":
    import sys
    # If arguments are provided, run as CLI; else run as MCP
    if len(sys.argv) > 1:
        app()
    else:
        mcp.run(transport='stdio')
# </file>
```

### 1.3 Metadata (`Skill.md`)
A human- and machine-readable markdown file describing the skill, CLI usage and MCP definition.

```markdown
# <file path="Skill.md">
# Skill: {Name}

## CLI Usage
`python main.py {tool_name} --param1 "value"`

## MCP Definition
```json
{
  "name": "{tool_name}",
  "parameters": {
    "type": "object",
    "properties": { "param1": { "type": "string" } }
  }
}
```
# </file>
```

### 1.4 Dependencies (`requirements.txt`)

```
# <file path="requirements.txt">
mcp>=1.0.0
typer>=0.12.0
# </file>
```

## 2. Mandatory Rules
- Dual-Mode: `main.py` MUST detect if it's being called as a CLI (with args) or as an MCP server (no args / stdio) and behave accordingly.
- Standard Streams:
  - Stdout: Reserved for MCP JSON-RPC and CLI output.
  - Stderr: Reserved for logs, warnings and debug messages.
- Documentation: Every CLI command MUST have a help string (Typer/Click style). The help string is used as a prompt for AI agents.

## 3. Deployment (Claude Desktop / Generic MCP client)
Provide a snippet for MCP client configuration (JSON) used by Claude Desktop or other MCP clients.

```json
{
  "mcpServers": {
    "{name}": {
      "command": "python",
      "args": ["/absolute/path/to/main.py"]
    }
  }
}
```

## 4. Notes & Best Practices
- Keep CLI and MCP behavior identical from a contract perspective: same parameters, same semantics.
- Avoid printing raw logs to stdout; use stderr or structured logging that writes to separate files.
- Provide examples in `Skill.md` including sample request payloads and sample responses (success and consistent error shapes).
- Include schema validation tests and at least one integration test that runs the CLI command and the MCP server's `--test` path when applicable.
