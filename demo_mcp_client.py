#!/usr/bin/env python3
"""
MCP Client Test - Parameter Passing Demo

This script demonstrates how to pass parameters to the Gmail Check MCP Server
using JSON-RPC protocol over stdin/stdout.
"""

import json
import subprocess
import asyncio
import sys
import os

async def test_mcp_parameter_passing():
    """Test parameter passing via MCP protocol"""
    
    print("🔌 MCP Client Parameter Passing Test")
    print("=" * 40)
    
    # Get the path to mcp_server.py
    mcp_server_path = os.path.join(os.path.dirname(__file__), "mcp_server.py")
    
    # Test cases with different parameter combinations
    test_cases = [
        {
            "name": "Minimal Parameters Test",
            "description": "Test with minimum required parameters",
            "params": {
                "username": "test@gmail.com",
                "app_password": "test_password_16ch",
                "email_filters": {
                    "test@example.com": ["test"]
                }
            }
        },
        {
            "name": "Full Parameters Test", 
            "description": "Test with all parameters specified",
            "params": {
                "username": "test@gmail.com",
                "app_password": "test_password_16ch",
                "email_filters": {
                    "notifications@github.com": ["pull request", "issue"],
                    "alerts@system.com": ["critical", "error"]
                },
                "check_interval": 15,
                "background_mode": False,
                "max_emails": 50,
                "days_back": 3
            }
        },
        {
            "name": "Background Mode Test",
            "description": "Test background monitoring configuration",
            "params": {
                "username": "monitor@gmail.com",
                "app_password": "monitor_pass_16ch",
                "email_filters": {
                    "alerts@company.com": ["urgent", "critical"]
                },
                "background_mode": True,
                "check_interval": 5,
                "max_emails": 20,
                "days_back": 1
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        print(f"   Parameters:")
        print(json.dumps(test_case['params'], indent=6, ensure_ascii=False))
        
        # Create MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": i,
            "method": "tools/call",
            "params": {
                "name": "gmail_check",
                "arguments": test_case['params']
            }
        }
        
        print(f"\n   MCP Request:")
        print(json.dumps(mcp_request, indent=6, ensure_ascii=False))
        
        # Note: In real scenario, this would send to MCP server
        # For demo purposes, we show the request structure
        print(f"   ✅ Request formatted successfully")

def simulate_mcp_communication():
    """Simulate MCP client-server communication"""
    
    print(f"\n🔄 MCP Communication Simulation")
    print("=" * 35)
    
    # Simulate initialization
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "gmail-check-client",
                "version": "1.0.0"
            }
        }
    }
    
    print(f"1. Client → Server (Initialize):")
    print(json.dumps(init_request, indent=3))
    
    init_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "serverInfo": {
                "name": "gmail-check-mcp-server",
                "version": "1.0.0"
            }
        }
    }
    
    print(f"\n2. Server → Client (Initialize Response):")
    print(json.dumps(init_response, indent=3))
    
    # Simulate tools list request
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    print(f"\n3. Client → Server (List Tools):")
    print(json.dumps(tools_request, indent=3))
    
    # Simulate tool call with parameters
    tool_call = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "gmail_check",
            "arguments": {
                "username": "user@gmail.com",
                "app_password": "real_app_password",
                "email_filters": {
                    "important@company.com": ["urgent", "action required"]
                },
                "max_emails": 25,
                "days_back": 2,
                "background_mode": False
            }
        }
    }
    
    print(f"\n4. Client → Server (Call Tool with Parameters):")
    print(json.dumps(tool_call, indent=3, ensure_ascii=False))
    
    # Simulate successful response
    success_response = {
        "jsonrpc": "2.0",
        "id": 3,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "success": True,
                        "function_name": "gmail_check",
                        "data": {
                            "emails_found": 3,
                            "emails_processed": 3,
                            "emails": [
                                {
                                    "sender": "important@company.com",
                                    "subject": "URGENT: Action Required",
                                    "received_date": "2026-02-11 10:30:00",
                                    "content": "Please review the attached document..."
                                }
                            ]
                        },
                        "metadata": {
                            "check_time": "2026-02-11T10:35:00Z",
                            "cache_hits": 0,
                            "new_emails": 3
                        }
                    }, ensure_ascii=False, indent=2)
                }
            ]
        }
    }
    
    print(f"\n5. Server → Client (Tool Response):")
    print(json.dumps(success_response, indent=3, ensure_ascii=False))

def show_parameter_examples():
    """Show practical parameter usage examples"""
    
    print(f"\n📋 Practical Parameter Examples")
    print("=" * 32)
    
    examples = [
        {
            "scenario": "GitHub Notifications",
            "description": "Monitor GitHub pull requests and issues",
            "parameters": {
                "username": "developer@gmail.com",
                "app_password": "github_app_password", 
                "email_filters": {
                    "notifications@github.com": [
                        "pull request",
                        "issue opened",
                        "mentioned you",
                        "review requested"
                    ]
                },
                "max_emails": 30,
                "days_back": 1,
                "check_interval": 30,
                "background_mode": False
            }
        },
        {
            "scenario": "System Monitoring",
            "description": "Continuous monitoring of system alerts",
            "parameters": {
                "username": "admin@company.com",
                "app_password": "system_monitor_pwd",
                "email_filters": {
                    "alerts@monitoring.com": ["critical", "error", "down"],
                    "nagios@system.com": ["host down", "service critical"],
                    "logs@server.com": ["exception", "fatal"]
                },
                "max_emails": 100,
                "days_back": 1,
                "check_interval": 5,
                "background_mode": True
            }
        },
        {
            "scenario": "Customer Support",
            "description": "Track support tickets and urgent requests",
            "parameters": {
                "username": "support@company.com",
                "app_password": "support_team_pwd",
                "email_filters": {
                    "tickets@zendesk.com": ["urgent", "high priority"],
                    "help@company.com": ["escalation", "complaint"],
                    "customers@domain.com": ["refund", "billing issue"]
                },
                "max_emails": 75,
                "days_back": 2,
                "check_interval": 15,
                "background_mode": True
            }
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['scenario']}")
        print(f"   Use Case: {example['description']}")
        print(f"   Configuration:")
        print(json.dumps(example['parameters'], indent=6, ensure_ascii=False))

def main():
    """Main function"""
    asyncio.run(test_mcp_parameter_passing())
    simulate_mcp_communication() 
    show_parameter_examples()
    
    print(f"\n" + "="*60)
    print(f"✅ MCP Parameter Passing Demo Complete!")
    print(f"📝 Key Points:")
    print(f"   • MCP Server supports 7 parameters (3 required, 4 optional)")
    print(f"   • Parameters passed via JSON-RPC 'arguments' field")
    print(f"   • All parameters validated before execution")
    print(f"   • Flexible email filtering with sender->subjects mapping")
    print(f"   • Supports both one-time and background monitoring modes")
    print(f"\n🚀 To test with real server:")
    print(f"   python3 mcp_server.py --test")

if __name__ == "__main__":
    main()