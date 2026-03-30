import sys
import json
import asyncio
import typer
from typing import Optional

try:
    from mcp.server.fastmcp import FastMCP
except Exception:
    FastMCP = None  # optional; MCP mode won't be available without the package

from ldr_compat import ExecutionContext
from gmail_check_skill import GmailCheckSkill

app = typer.Typer()
mcp = FastMCP("Gmail Check") if FastMCP else None
impl = GmailCheckSkill()

_is_cli = len(sys.argv) > 1


def format_mcp(result: dict) -> str:
    # Wrap the skill result into the canonical top-level contract
    # { success: bool, data: {...}, error: null|string }
    wrapped = {
        "success": bool(result.get("success", False)),
        "data": result,
        "error": None if result.get("success") else result.get("error")
    }
    return json.dumps(wrapped, ensure_ascii=False)


@app.command()
def gmail_check(
    username: Optional[str] = typer.Option(None, help="Gmail username (email address)"),
    app_password: Optional[str] = typer.Option(None, help="Gmail app password"),
    email_filters: Optional[str] = typer.Option(None, help="JSON string of email filters"),
    background_mode: bool = typer.Option(False, help="Run in background mode"),
    check_interval: int = typer.Option(30, help="Minutes between background checks"),
    max_emails: int = typer.Option(100, help="Maximum emails to examine per check"),
    days_back: int = typer.Option(1, help="How many days back to search for emails"),
    time_range_hours: int = typer.Option(24, help="Time window in hours to restrict the search"),
    use_cache: bool = typer.Option(True, help="Whether to use cache to avoid reprocessing old messages"),
):
    """Check Gmail emails (CLI and MCP compatible)"""
    ctx = ExecutionContext()
    try:
        filters = json.loads(email_filters) if email_filters else {}
    except Exception:
        filters = {}

    try:
        result = impl.execute(
            ctx,
            username=username,
            app_password=app_password,
            email_filters=filters,
            background_mode=background_mode,
            check_interval=check_interval,
            max_emails=max_emails,
            days_back=days_back,
            time_range_hours=time_range_hours,
            use_cache=use_cache,
        )

        # Format output according to SKILL_GENERATION_RULES: top-level success/data/error
        output = format_mcp(result)
        if _is_cli:
            # CLI must print pure JSON to stdout
            typer.echo(output)
        else:
            # MCP mode: return JSON string so FastMCP can wrap it
            return output

    except Exception as e:
        error = {"success": False, "data": None, "error": str(e)}
        if _is_cli:
            typer.echo(json.dumps(error), err=True)
            raise typer.Exit(1)
        else:
            return format_mcp(error)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        app()
    else:
        if mcp:
            mcp.run(transport="stdio")
        else:
            # No FastMCP available; fall back to CLI
            app()
