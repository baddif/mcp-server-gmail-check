"""
Gmail Check Skill - Gmail邮件检测和内容获取

This skill provides Gmail email checking functionality using app password authentication.
Supports email filtering, content downloading, and caching to avoid duplicate processing.
"""

import imaplib
import email
import json
import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
import hashlib
import os
from pathlib import Path

# 尝试从框架导入，如果失败则使用兼容模块
try:
    from ldr.mcp.base import McpCompatibleSkill, McpResource, McpPrompt
    from ldr.context import ExecutionContext
except ImportError:
    from ldr_compat import McpCompatibleSkill, McpResource, McpPrompt, ExecutionContext


class GmailCheckSkill(McpCompatibleSkill):
    """
    Gmail Check Skill Implementation
    
    Purpose: Check Gmail emails using app password and filter by sender and subject
    Category: Data Extraction
    
    Features:
    - App password authentication
    - Email filtering by sender and subject patterns
    - Content downloading for matched emails
    - Cache management to avoid duplicate processing
    - Configurable check intervals
    - Background monitoring support
    """
    
    def __init__(self):
        super().__init__()
        self._cache_file = ".gmail_check_cache.json"
        self._cache_lock = threading.Lock()
        self._monitoring_thread = None
        self._stop_monitoring = threading.Event()
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """Return OpenAI Function Calling compatible JSON Schema"""
        return {
            "type": "function",
            "function": {
                "name": "gmail_check",
                "description": "Check Gmail emails using app password authentication. Filter emails by sender and subject, download content for matches, and cache processed emails to avoid duplicates. Supports background monitoring with configurable intervals.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "Gmail username (email address) for authentication"
                        },
                        "app_password": {
                            "type": "string",
                            "description": "Gmail app password (16-character password without spaces) for authentication"
                        },
                        "email_filters": {
                            "type": "object",
                            "description": "JSON object defining email filters. Structure: {'sender_email': ['subject1', 'subject2', ...]}. Each sender can have multiple subject patterns to match.",
                            "additionalProperties": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "check_interval": {
                            "type": "integer",
                            "description": "Interval in minutes for checking emails. Default is 30 minutes.",
                            "default": 30,
                            "minimum": 1,
                            "maximum": 1440
                        },
                        "background_mode": {
                            "type": "boolean",
                            "description": "Whether to run in background monitoring mode. If true, starts continuous monitoring. If false, performs one-time check.",
                            "default": False
                        },
                        "max_emails": {
                            "type": "integer",
                            "description": "Maximum number of emails to check per run. Default is 100.",
                            "default": 100,
                            "minimum": 1,
                            "maximum": 1000
                        },
                        "days_back": {
                            "type": "integer",
                            "description": "Number of days back to check for emails. Default is 1 day.",
                            "default": 1,
                            "minimum": 1,
                            "maximum": 30
                        },
                        "time_range_hours": {
                            "type": "integer",
                            "description": "Time range in hours to check for emails from current time. Default is 24 hours (last day). Overrides days_back if specified.",
                            "default": 24,
                            "minimum": 1,
                            "maximum": 720
                        },
                        "use_cache": {
                            "type": "boolean",
                            "description": "Whether to use cache to avoid retrieving previously processed emails. If true, only new emails will be returned. If false, all matching emails in time range will be returned. Default is true.",
                            "default": True
                        }
                    },
                    "required": ["username", "app_password", "email_filters"]
                }
            }
        }
    
    def get_openai_schema(self) -> Dict[str, Any]:
        """Return OpenAI schema"""
        return self.get_schema()
    
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """
        Execute the Gmail check skill
        
        Args:
            ctx: Execution context
            **kwargs: Skill parameters
            
        Returns:
            Result dictionary with matched emails and their content
        """
        try:
            # Extract parameters
            username = kwargs.get("username")
            app_password = kwargs.get("app_password")
            email_filters = kwargs.get("email_filters", {})
            check_interval = kwargs.get("check_interval", 30)
            background_mode = kwargs.get("background_mode", False)
            max_emails = kwargs.get("max_emails", 100)
            days_back = kwargs.get("days_back", 1)
            time_range_hours = kwargs.get("time_range_hours", 24)
            use_cache = kwargs.get("use_cache", True)
            
            # Validate required parameters
            if not username or not app_password or not email_filters:
                return {
                    "success": False,
                    "function_name": "gmail_check",
                    "error": {
                        "message": "Missing required parameters: username, app_password, or email_filters",
                        "type": "validation_error"
                    }
                }
            
            # Load cache (always load for potential updating)
            processed_emails = self._load_cache() if use_cache else {}
            
            if background_mode:
                # Start background monitoring
                result = self._start_background_monitoring(
                    ctx, username, app_password, email_filters, 
                    check_interval, max_emails, days_back,
                    time_range_hours, use_cache
                )
            else:
                # Perform one-time check
                matched_emails = self._check_emails(
                    username, app_password, email_filters, 
                    processed_emails, max_emails, days_back,
                    time_range_hours, use_cache
                )
                
                # Save updated cache (always save after processing, regardless of use_cache setting)
                self._save_cache(processed_emails)
                
                result = {
                    "success": True,
                    "function_name": "gmail_check",
                    "data": {
                        "matched_emails": matched_emails,
                        "check_time": datetime.now(timezone.utc).isoformat(),
                        "total_matched": len(matched_emails),
                        "background_mode": False
                    },
                    "statistics": {
                        "emails_checked": len(matched_emails),
                        "cache_size": len(processed_emails),
                        "filters_applied": len(email_filters),
                        "time_range_hours": time_range_hours,
                        "cache_enabled": use_cache,
                        "search_period": f"{time_range_hours} hours" if time_range_hours is not None else f"{days_back} days"
                    }
                }
            
            # Store in context
            ctx.set("skill:gmail_check:result", result)
            ctx.set("skill:gmail_check:last_check", datetime.now(timezone.utc).isoformat())
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "function_name": "gmail_check",
                "error": {
                    "message": str(e),
                    "type": "execution_error"
                }
            }
    
    def _check_emails(self, username: str, app_password: str, email_filters: Dict[str, List[str]], 
                     processed_emails: Dict[str, str], max_emails: int, days_back: int, 
                     time_range_hours: int = None, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Check emails and return matched content"""
        matched_emails = []
        
        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
            mail.login(username, app_password)
            mail.select('inbox')
            
            # Calculate date range - use time_range_hours if provided, otherwise use days_back
            if time_range_hours is not None:
                since_datetime = datetime.now() - timedelta(hours=time_range_hours)
                since_date = since_datetime.strftime("%d-%b-%Y")
                print(f"📅 Using time range: {time_range_hours} hours ({since_datetime.strftime('%Y-%m-%d %H:%M:%S')})")
            else:
                since_datetime = datetime.now() - timedelta(days=days_back)
                since_date = since_datetime.strftime("%d-%b-%Y")
                print(f"📅 Using days back: {days_back} days ({since_datetime.strftime('%Y-%m-%d')})")
            
            print(f"💾 Cache usage: {'Enabled' if use_cache else 'Disabled'} - {len(processed_emails)} emails in cache")
            
            # Search for emails within date range
            search_criteria = f'(SINCE {since_date})'
            _, message_numbers = mail.search(None, search_criteria)
            
            if not message_numbers[0]:
                print(f"调试: 在 {since_date} 之后没有找到任何邮件")
                return matched_emails
            
            message_list = message_numbers[0].split()
            print(f"调试: 找到 {len(message_list)} 封邮件需要检查")
            
            # Limit number of emails to check
            if len(message_list) > max_emails:
                message_list = message_list[-max_emails:]  # Get most recent emails
                print(f"调试: 限制为最近的 {len(message_list)} 封邮件")
            
            for i, num in enumerate(message_list, 1):
                try:
                    print(f"调试: 处理第 {i}/{len(message_list)} 封邮件 (ID: {num.decode()})")
                    
                    # Fetch email headers first for filtering
                    _, msg_data = mail.fetch(num, '(RFC822.HEADER)')
                    email_message = email.message_from_bytes(msg_data[0][1])
                    
                    # Extract email metadata
                    sender = email_message['From']
                    subject_raw = email_message['Subject'] or ''
                    message_id = email_message['Message-ID']
                    date_received = email_message['Date']
                    
                    # Decode subject if it's encoded (for Chinese/non-ASCII characters)
                    subject = self._decode_header(subject_raw) if subject_raw else ''
                    
                    print(f"  发件人: {sender}")
                    print(f"  主题(原始): {subject_raw}")
                    print(f"  主题(解码): {subject}")
                    print(f"  日期: {date_received}")
                    
                    # Create unique email identifier
                    email_id = hashlib.md5(f"{message_id}{date_received}".encode()).hexdigest()
                    
                    # Skip if already processed (only when cache is enabled)
                    if use_cache and email_id in processed_emails:
                        print(f"  ⏩ 跳过: 已处理过的邮件 (缓存)")
                        continue
                    elif not use_cache:
                        print(f"  🔄 处理: 忽略缓存状态")
                    else:
                        print(f"  🆕 新邮件: 未在缓存中找到")
                    
                    # Check if email matches filters
                    match_found = False
                    matched_sender = None
                    matched_subjects = []
                    
                    print(f"  检查过滤器...")
                    for filter_sender, filter_subjects in email_filters.items():
                        print(f"    检查发件人过滤器: {filter_sender}")
                        if self._match_sender(sender, filter_sender):
                            print(f"      ✅ 发件人匹配!")
                            matched_sender = filter_sender
                            for subject_pattern in filter_subjects:
                                print(f"      检查主题关键词: '{subject_pattern}'")
                                if self._match_subject(subject, subject_pattern):
                                    print(f"        ✅ 主题匹配!")
                                    matched_subjects.append(subject_pattern)
                                    match_found = True
                                else:
                                    print(f"        ❌ 主题不匹配")
                        else:
                            print(f"      ❌ 发件人不匹配")
                    
                    if match_found:
                        # Fetch full email content
                        _, full_msg_data = mail.fetch(num, '(RFC822)')
                        full_email_message = email.message_from_bytes(full_msg_data[0][1])
                        
                        # Extract email content
                        content = self._extract_email_content(full_email_message)
                        
                        matched_email = {
                            "sender": sender,
                            "subject": subject,
                            "content": content,
                            "date_received": date_received,
                            "message_id": message_id,
                            "matched_sender_filter": matched_sender,
                            "matched_subject_filters": matched_subjects,
                            "email_id": email_id
                        }
                        
                        matched_emails.append(matched_email)
                        
                        # Mark as processed
                        processed_emails[email_id] = datetime.now(timezone.utc).isoformat()
                
                except Exception as e:
                    # Log individual email processing errors but continue
                    print(f"Error processing email {num}: {str(e)}")
                    continue
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            raise Exception(f"Gmail connection error: {str(e)}")
        
        return matched_emails
    
    def _match_sender(self, sender: str, filter_sender: str) -> bool:
        """Check if sender matches filter"""
        if not sender:
            return False
        
        # Extract email from "Name <email@domain.com>" format
        if '<' in sender and '>' in sender:
            email_part = sender.split('<')[1].split('>')[0].strip()
        else:
            email_part = sender.strip()
        
        result = email_part.lower() == filter_sender.lower()
        print(f"        发件人匹配调试: '{email_part}' vs '{filter_sender}' = {result}")
        return result
    
    def _match_subject(self, subject: str, subject_pattern: str) -> bool:
        """Check if subject matches pattern (case-insensitive substring match)"""
        if not subject:
            return False
        
        result = subject_pattern.lower() in subject.lower()
        print(f"          主题匹配调试: '{subject}' 包含 '{subject_pattern}' = {result}")
        return result
    
    def _decode_header(self, header_value: str) -> str:
        """Decode email header (for Chinese/non-ASCII characters)"""
        try:
            decoded_parts = email.header.decode_header(header_value)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        # Try common encodings for Chinese
                        for enc in ['utf-8', 'gb2312', 'gbk', 'big5']:
                            try:
                                decoded_string += part.decode(enc)
                                break
                            except:
                                continue
                        else:
                            # Fallback to UTF-8 with error handling
                            decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            return decoded_string
        except Exception as e:
            print(f"          解码头部失败: {str(e)}, 使用原始值")
            return header_value
    
    def _extract_email_content(self, email_message) -> str:
        """Extract text content from email message"""
        content = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Get text content
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        content += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        content += str(part.get_payload())
                elif content_type == "text/html" and "attachment" not in content_disposition and not content:
                    # Use HTML content if no plain text available
                    try:
                        html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        # Simple HTML tag removal
                        import re
                        content += re.sub('<[^<]+?>', '', html_content)
                    except:
                        content += str(part.get_payload())
        else:
            # Single part message
            try:
                content = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                content = str(email_message.get_payload())
        
        return content.strip()
    
    def _load_cache(self) -> Dict[str, str]:
        """Load processed emails cache"""
        try:
            if os.path.exists(self._cache_file):
                with open(self._cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {str(e)}")
        
        return {}
    
    def _save_cache(self, processed_emails: Dict[str, str]):
        """Save processed emails cache"""
        try:
            with self._cache_lock:
                with open(self._cache_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_emails, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {str(e)}")
    
    def _start_background_monitoring(self, ctx: ExecutionContext, username: str, app_password: str, 
                                   email_filters: Dict[str, List[str]], check_interval: int,
                                   max_emails: int, days_back: int, time_range_hours: int = None,
                                   use_cache: bool = True) -> Dict[str, Any]:
        """Start background email monitoring"""
        
        def monitoring_loop():
            processed_emails = self._load_cache() if use_cache else {}
            
            # Perform first check immediately
            try:
                matched_emails = self._check_emails(
                    username, app_password, email_filters, 
                    processed_emails, max_emails, days_back,
                    time_range_hours, use_cache
                )
                
                if matched_emails:
                    # Save updated cache
                    self._save_cache(processed_emails)
                    
                    # Update context with new results
                    result_data = {
                        "matched_emails": matched_emails,
                        "check_time": datetime.now(timezone.utc).isoformat(),
                        "total_matched": len(matched_emails),
                        "background_mode": True
                    }
                    ctx.set("skill:gmail_check:latest_results", result_data)
                    ctx.set("skill:gmail_check:last_check", datetime.now(timezone.utc).isoformat())
                
            except Exception as e:
                print(f"Background monitoring error (initial check): {str(e)}")
            
            # Continue with periodic checks
            while not self._stop_monitoring.is_set():
                # Wait for next check
                if self._stop_monitoring.wait(check_interval * 60):
                    break  # Exit if stop event is set during wait
                
                try:
                    matched_emails = self._check_emails(
                        username, app_password, email_filters, 
                        processed_emails, max_emails, days_back,
                        time_range_hours, use_cache
                    )
                    
                    if matched_emails:
                        # Save updated cache
                        self._save_cache(processed_emails)
                        
                        # Update context with new results
                        result_data = {
                            "matched_emails": matched_emails,
                            "check_time": datetime.now(timezone.utc).isoformat(),
                            "total_matched": len(matched_emails),
                            "background_mode": True
                        }
                        ctx.set("skill:gmail_check:latest_results", result_data)
                        ctx.set("skill:gmail_check:last_check", datetime.now(timezone.utc).isoformat())
                    
                except Exception as e:
                    print(f"Background monitoring error: {str(e)}")
        
        # Stop existing monitoring if running
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._stop_monitoring.set()
            self._monitoring_thread.join()
        
        # Start new monitoring thread
        self._stop_monitoring.clear()
        self._monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self._monitoring_thread.start()
        
        return {
            "success": True,
            "function_name": "gmail_check",
            "data": {
                "background_mode": True,
                "check_interval": check_interval,
                "monitoring_started": datetime.now(timezone.utc).isoformat(),
                "message": f"Background monitoring started with {check_interval} minute intervals"
            },
            "statistics": {
                "monitoring_active": True,
                "check_interval_minutes": check_interval,
                "filters_count": len(email_filters)
            }
        }
    
    def stop_monitoring(self) -> bool:
        """Stop background monitoring"""
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._stop_monitoring.set()
            self._monitoring_thread.join(timeout=5)
            return True
        return False
    
    def get_mcp_resources(self) -> List[McpResource]:
        """Define MCP Resources"""
        return [
            McpResource(
                uri="skill://gmail_check/latest_results",
                name="gmail_check_latest_results",
                description="Latest Gmail check results with matched emails",
                mime_type="application/json"
            ),
            McpResource(
                uri="skill://gmail_check/cache_status",
                name="gmail_check_cache_status",
                description="Gmail check cache status and statistics",
                mime_type="application/json"
            ),
            McpResource(
                uri="skill://gmail_check/monitoring_status",
                name="gmail_check_monitoring_status",
                description="Background monitoring status and configuration",
                mime_type="application/json"
            )
        ]
    
    def get_mcp_prompts(self) -> List[McpPrompt]:
        """Define MCP Prompts"""
        return []
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read MCP resource"""
        if uri == "skill://gmail_check/latest_results":
            # Return latest check results
            processed_emails = self._load_cache()
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps({
                            "cache_entries": len(processed_emails),
                            "last_cache_update": max(processed_emails.values()) if processed_emails else None,
                            "cache_file": self._cache_file
                        }, ensure_ascii=False, indent=2)
                    }
                ]
            }
        elif uri == "skill://gmail_check/cache_status":
            # Return cache status
            processed_emails = self._load_cache()
            cache_stats = {
                "total_processed_emails": len(processed_emails),
                "cache_file_exists": os.path.exists(self._cache_file),
                "cache_file_size": os.path.getsize(self._cache_file) if os.path.exists(self._cache_file) else 0,
                "oldest_entry": min(processed_emails.values()) if processed_emails else None,
                "newest_entry": max(processed_emails.values()) if processed_emails else None
            }
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(cache_stats, ensure_ascii=False, indent=2)
                    }
                ]
            }
        elif uri == "skill://gmail_check/monitoring_status":
            # Return monitoring status
            monitoring_status = {
                "monitoring_active": self._monitoring_thread and self._monitoring_thread.is_alive(),
                "thread_name": self._monitoring_thread.name if self._monitoring_thread else None,
                "stop_event_set": self._stop_monitoring.is_set()
            }
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(monitoring_status, ensure_ascii=False, indent=2)
                    }
                ]
            }
        
        return super().read_resource(uri)