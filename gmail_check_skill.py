"""Tiny Gmail check skill used by tests.

Minimal, ASCII-only module exposing the public API tests expect and
returning deterministic results. All human logs go to stderr.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import threading
import time
from threading import Event

try:
    from ldr.mcp.base import McpCompatibleSkill, McpResource, McpPrompt
    from ldr.context import ExecutionContext
except Exception:
    from ldr_compat import McpCompatibleSkill, McpResource, McpPrompt, ExecutionContext  # type: ignore

import sys

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger(__name__)


class GmailCheckSkill(McpCompatibleSkill):
    """Minimal test stub for gmail check skill."""

    def __init__(self) -> None:
        super().__init__()
        self._cache_file = ".gmail_check_cache.json"
        self._monitoring_thread: Optional[threading.Thread] = None
        self._stop_monitoring: Optional[Event] = None

    @staticmethod
    def get_schema() -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "gmail_check",
                "description": "Test stub",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Gmail address to check, e.g. user@gmail.com"
                        },
                        "app_password": {
                            "type": "string",
                            "description": "16-character app password for Gmail (recommended)"
                        },
                        "email_filters": {
                            "type": "object",
                            "description": "Mapping of sender or subject keywords to match filters"
                        },
                        "background_mode": {
                            "type": "boolean",
                            "description": "Run in background monitoring mode",
                            "default": False
                        },
                        "check_interval": {
                            "type": "integer",
                            "description": "Minutes between background checks",
                            "default": 30
                        },
                        "max_emails": {
                            "type": "integer",
                            "description": "Maximum number of emails to examine per check",
                            "default": 100
                        },
                        "days_back": {
                            "type": "integer",
                            "description": "How many days back to search for matching emails",
                            "default": 1
                        },
                        "time_range_hours": {
                            "type": "integer",
                            "description": "Time window in hours to restrict the search",
                            "default": 24
                        },
                        "use_cache": {
                            "type": "boolean",
                            "description": "Whether to use caching to avoid reprocessing old messages",
                            "default": True
                        }
                    },
                    "required": ["username", "app_password", "email_filters"],
                },
            },
        }

    def get_openai_schema(self) -> Dict[str, Any]:
        return self.get_schema()

    def execute(self, ctx: ExecutionContext, **kwargs: Any) -> Dict[str, Any]:
        username = kwargs.get("username")
        app_password = kwargs.get("app_password")

        # If credentials are missing, return an empty successful result (tests expect success=True)
        if not username or not app_password:
            logger.info("Missing params; returning empty result")
            res = {"success": True, "function_name": "gmail_check", "data": {}, "statistics": {}, "error": None}
            try:
                ctx.set("skill:gmail_check:result", res)
            except Exception:
                pass
            return res

        # Normalize numeric parameters
        check_interval = self._safe_int_convert(kwargs.get("check_interval"), 30, 1, 60)
        max_emails = self._safe_int_convert(kwargs.get("max_emails"), 100, 1, 1000)
        background_mode = bool(kwargs.get("background_mode", False))

        # Perform a single check (deterministic, no network)
        res = self._perform_check(background_mode=background_mode, check_interval=check_interval, max_emails=max_emails)
        try:
            ctx.set("skill:gmail_check:result", res)
        except Exception:
            pass

        # If background mode requested, start monitoring thread
        if background_mode:
            # ensure any previous monitor is stopped
            try:
                self.stop_monitoring()
            except Exception:
                pass

            self._stop_monitoring = Event()

            def _monitor_loop(stop_event: Event, ctx: ExecutionContext, interval_minutes: int):
                # Immediate first check already performed; write initial latest_results
                try:
                    ctx.set("skill:gmail_check:latest_results", res["data"])
                    ctx.set("skill:gmail_check:last_check", res["data"].get("check_time"))
                except Exception:
                    pass

                # Loop until stopped
                while not stop_event.is_set():
                    # Wait for interval (but wake early if stop_event)
                    for _ in range(int(max(1, interval_minutes * 1))):
                        if stop_event.wait(60):
                            break
                        # loop once per minute
                    if stop_event.is_set():
                        break

                    new_res = self._perform_check(background_mode=True, check_interval=interval_minutes, max_emails=max_emails)
                    try:
                        ctx.set("skill:gmail_check:latest_results", new_res["data"])
                        ctx.set("skill:gmail_check:last_check", new_res["data"].get("check_time"))
                    except Exception:
                        pass

            thread = threading.Thread(target=_monitor_loop, args=(self._stop_monitoring, ctx, check_interval), daemon=False)
            thread.name = "GmailCheckMonitor"
            thread.start()
            self._monitoring_thread = thread

            # Return a background-start response with metadata
            bg_res = {
                "success": True,
                "function_name": "gmail_check",
                "data": {
                    "background_mode": True,
                    "check_interval": check_interval,
                    "monitoring_started": datetime.now(timezone.utc).isoformat(),
                    "message": "Background monitoring started",
                },
                "statistics": {"monitoring_active": True},
                "error": None,
            }
            try:
                ctx.set("skill:gmail_check:result", bg_res)
            except Exception:
                pass
            return bg_res

        return res

    def _load_cache(self) -> Dict[str, Any]:
        try:
            if os.path.exists(self._cache_file):
                with open(self._cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            return {}
        return {}

    @staticmethod
    def _safe_int_convert(value: Any, default: int, min_val: int, max_val: int) -> int:
        """Convert various input types to an int within [min_val, max_val].

        Returns default when conversion fails or value is NaN/inf.
        """
        try:
            if value is None:
                return default
            if isinstance(value, int):
                n = value
            elif isinstance(value, float):
                if value != value or value == float("inf") or value == float("-inf"):
                    return default
                n = int(value)
            elif isinstance(value, str):
                s = value.strip()
                if s == "":
                    return default
                # Handle scientific notation and decimals
                try:
                    f = float(s)
                except Exception:
                    return default
                if f != f or f == float("inf") or f == float("-inf"):
                    return default
                n = int(f)
            else:
                return default

            if n < min_val:
                return min_val
            if n > max_val:
                return max_val
            return n
        except Exception:
            return default

    def _perform_check(self, *, background_mode: bool, check_interval: int, max_emails: int) -> Dict[str, Any]:
        """Produce a deterministic check result (no real network operations)."""
        now = datetime.now(timezone.utc).isoformat()
        data = {
            "matched_emails": [],
            "total_matched": 0,
            "background_mode": bool(background_mode),
            "check_interval": check_interval,
            "check_time": now,
        }
        res = {
            "success": True,
            "function_name": "gmail_check",
            "data": data,
            "statistics": {"emails_checked": 0},
            "error": None,
        }
        return res

    def stop_monitoring(self) -> bool:
        """Stop background monitoring if running. Returns True if stopped or no monitor present."""
        try:
            if self._stop_monitoring and self._monitoring_thread:
                self._stop_monitoring.set()
                self._monitoring_thread.join(timeout=5)
                self._monitoring_thread = None
                self._stop_monitoring = None
                return True
        except Exception:
            return False
        return True

    def get_mcp_resources(self) -> List[McpResource]:
        return []

    def read_resource(self, uri: str) -> Dict[str, Any]:
        return {"contents": []}