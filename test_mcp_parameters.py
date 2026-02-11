#!/usr/bin/env python3
"""
MCP Server Parameter Testing Script

This script demonstrates how to pass parameters to the Gmail Check MCP Server
and shows all supported parameters and their usage.
"""

import json
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server import GmailCheckMcpServer

def test_parameter_passing():
    """Test parameter passing to MCP server"""
    
    print("🧪 Gmail Check MCP Server Parameter Testing")
    print("=" * 50)
    
    server = GmailCheckMcpServer()
    
    # 1. Show available tools and their parameters
    print("\n1. 📋 Available Tools and Parameters:")
    tools = server.list_tools()
    for tool in tools:
        print(f"\nTool: {tool['name']}")
        print(f"Description: {tool['description']}")
        print("\nParameters:")
        properties = tool['inputSchema']['properties']
        required = tool['inputSchema'].get('required', [])
        
        for param_name, param_info in properties.items():
            required_mark = " (REQUIRED)" if param_name in required else ""
            default = f" [default: {param_info.get('default', 'none')}]" if 'default' in param_info else ""
            print(f"  • {param_name}{required_mark}: {param_info['description']}{default}")

    # 2. Example parameter sets
    print(f"\n2. 🔧 Example Parameter Configurations:")
    
    example_configs = [
        {
            "name": "Basic Email Check",
            "description": "Simple one-time email check with minimal parameters",
            "params": {
                "username": "your_email@gmail.com",
                "app_password": "your_16_digit_app_password",
                "email_filters": {
                    "notifications@github.com": ["pull request", "issue"],
                    "billing@aws.amazon.com": ["invoice", "bill"]
                },
                "max_emails": 20,
                "days_back": 3
            }
        },
        {
            "name": "Background Monitoring",
            "description": "Continuous monitoring with custom interval",
            "params": {
                "username": "your_email@gmail.com",
                "app_password": "your_16_digit_app_password",
                "email_filters": {
                    "alerts@company.com": ["urgent", "critical", "error"],
                    "support@service.com": ["ticket", "request"]
                },
                "background_mode": True,
                "check_interval": 15,
                "max_emails": 50,
                "days_back": 1
            }
        },
        {
            "name": "Comprehensive Scan",
            "description": "Thorough email check with maximum scope",
            "params": {
                "username": "your_email@gmail.com",
                "app_password": "your_16_digit_app_password",
                "email_filters": {
                    "no-reply@bank.com": ["statement", "transaction"],
                    "updates@news.com": ["breaking", "important"],
                    "admin@domain.com": ["security", "maintenance"]
                },
                "max_emails": 200,
                "days_back": 7,
                "check_interval": 60
            }
        }
    ]
    
    for i, config in enumerate(example_configs, 1):
        print(f"\n   Example {i}: {config['name']}")
        print(f"   Description: {config['description']}")
        print(f"   Parameters:")
        print(json.dumps(config['params'], indent=6, ensure_ascii=False))

    # 3. MCP Client Integration Examples
    print(f"\n3. 🤖 MCP Client Integration Examples:")
    
    print(f"\n   A. Direct JSON-RPC Call:")
    direct_call = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "gmail_check",
            "arguments": {
                "username": "user@gmail.com",
                "app_password": "abcd efgh ijkl mnop",
                "email_filters": {
                    "notifications@github.com": ["pull request"]
                },
                "max_emails": 10,
                "days_back": 1
            }
        }
    }
    print(json.dumps(direct_call, indent=6, ensure_ascii=False))
    
    print(f"\n   B. Python MCP Client:")
    python_example = '''
from mcp import ClientSession, StdioServerParameters

async def check_gmail():
    server_params = StdioServerParameters(
        command="python3",
        args=["/path/to/mcp_server.py"]
    )
    
    async with ClientSession(server_params) as session:
        await session.initialize()
        
        # Call gmail_check with parameters
        result = await session.call_tool("gmail_check", {
            "username": "your_email@gmail.com",
            "app_password": "your_app_password",
            "email_filters": {
                "important@company.com": ["urgent", "critical"]
            },
            "max_emails": 25,
            "days_back": 2
        })
        
        return result
'''
    print(python_example)
    
    print(f"\n   C. Claude Desktop Configuration:")
    claude_config = {
        "mcpServers": {
            "gmail-check": {
                "command": "python3",
                "args": ["/path/to/mcp_server.py"],
                "env": {
                    "PYTHONPATH": "/path/to/mcp-server-gmail-check"
                }
            }
        }
    }
    print(json.dumps(claude_config, indent=6))

    # 4. Parameter Validation Rules
    print(f"\n4. ⚠️ Parameter Validation Rules:")
    
    validation_rules = [
        "• username: Must be a valid Gmail address",
        "• app_password: Must be 16-character Gmail app password",
        "• email_filters: Required object with sender->subjects mapping",
        "• check_interval: 1-1440 minutes (1 day max)",
        "• max_emails: 1-1000 emails per check",
        "• days_back: 1-30 days maximum lookback",
        "• background_mode: Boolean, false = one-time check"
    ]
    
    for rule in validation_rules:
        print(f"   {rule}")

    # 5. Common Usage Patterns
    print(f"\n5. 💡 Common Usage Patterns:")
    
    patterns = [
        {
            "pattern": "Alert Monitoring",
            "use_case": "Monitor critical system alerts",
            "config": {
                "email_filters": {"alerts@system.com": ["error", "critical", "down"]},
                "background_mode": True,
                "check_interval": 5,
                "max_emails": 20
            }
        },
        {
            "pattern": "Newsletter Digest",
            "use_case": "Check for important newsletters weekly",
            "config": {
                "email_filters": {"newsletter@tech.com": ["weekly", "important"]},
                "background_mode": False,
                "days_back": 7,
                "max_emails": 50
            }
        },
        {
            "pattern": "Support Tickets",
            "use_case": "Monitor customer support emails",
            "config": {
                "email_filters": {
                    "support@company.com": ["ticket", "urgent"],
                    "help@service.com": ["request", "problem"]
                },
                "background_mode": True,
                "check_interval": 30,
                "max_emails": 100
            }
        }
    ]
    
    for i, pattern in enumerate(patterns, 1):
        print(f"\n   Pattern {i}: {pattern['pattern']}")
        print(f"   Use Case: {pattern['use_case']}")
        print(f"   Config: {json.dumps(pattern['config'], indent=8)}")

    print(f"\n6. 🔧 Testing Commands:")
    print(f"   # Start MCP server")
    print(f"   python3 mcp_server.py")
    print(f"   ")
    print(f"   # Test server functionality")
    print(f"   python3 mcp_server.py --test")
    print(f"   ")
    print(f"   # Test with this script")
    print(f"   python3 test_mcp_parameters.py")

    print(f"\n✅ Parameter testing documentation complete!")


if __name__ == "__main__":
    test_parameter_passing()