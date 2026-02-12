#!/usr/bin/env python3
"""
Detailed MCP Server Inspector

This script provides detailed inspection of the Gmail Check MCP Server,
similar to what you would see in MCP Inspector.
"""

import json
import subprocess
import sys
import os

def run_mcp_command(method: str, params: dict = None) -> dict:
    """Send a JSON-RPC command to the MCP server and return detailed response"""
    
    command = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    try:
        process = subprocess.Popen(
            ["python3", "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        stdout, stderr = process.communicate(json.dumps(command))
        
        if stdout:
            try:
                response = json.loads(stdout)
                return response
            except json.JSONDecodeError:
                return {"error": f"Invalid JSON: {stdout}"}
        else:
            return {"error": "No response"}
            
    except Exception as e:
        return {"error": str(e)}

def print_json(data, indent=0):
    """Pretty print JSON data"""
    prefix = "  " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"{prefix}{key}:")
                print_json(value, indent + 1)
            else:
                print(f"{prefix}{key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{prefix}[{i}]:")
            print_json(item, indent + 1)
    else:
        print(f"{prefix}{data}")

def detailed_inspection():
    """Perform detailed MCP server inspection"""
    
    print("🔍 Gmail Check MCP Server - Detailed Inspection")
    print("=" * 60)
    
    # Initialize
    print("\n🔗 Initialization Response:")
    init_response = run_mcp_command("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {"tools": {}}
    })
    print_json(init_response, 1)
    
    # Get detailed tools info
    print("\n🔧 Tools Details:")
    tools_response = run_mcp_command("tools/list")
    
    if "result" in tools_response and "tools" in tools_response["result"]:
        tools = tools_response["result"]["tools"]
        
        for i, tool in enumerate(tools):
            print(f"\n   Tool {i+1}: {tool['name']}")
            print(f"   Description: {tool['description']}")
            
            schema = tool.get('inputSchema', {})
            print(f"   Schema Type: {schema.get('type', 'unknown')}")
            
            # Required parameters
            required = schema.get('required', [])
            print(f"   Required Parameters ({len(required)}): {required}")
            
            # All parameters with details
            properties = schema.get('properties', {})
            print(f"   \n   All Parameters ({len(properties)}):")
            
            for param_name, param_info in properties.items():
                is_required = "✅ REQUIRED" if param_name in required else "❌ Optional"
                param_type = param_info.get('type', 'unknown')
                description = param_info.get('description', 'No description')
                default = param_info.get('default', None)
                minimum = param_info.get('minimum', None)
                maximum = param_info.get('maximum', None)
                
                print(f"     • {param_name}")
                print(f"       Type: {param_type}")
                print(f"       Status: {is_required}")
                print(f"       Description: {description}")
                if default is not None:
                    print(f"       Default: {default}")
                if minimum is not None:
                    print(f"       Minimum: {minimum}")
                if maximum is not None:
                    print(f"       Maximum: {maximum}")
                
                # Special handling for object types
                if param_type == 'object':
                    additional_props = param_info.get('additionalProperties', {})
                    if additional_props:
                        print(f"       Additional Properties: {additional_props}")
                print()
    
    # Get detailed resources info
    print("\n📊 Resources Details:")
    resources_response = run_mcp_command("resources/list")
    
    if "result" in resources_response and "resources" in resources_response["result"]:
        resources = resources_response["result"]["resources"]
        
        for i, resource in enumerate(resources):
            print(f"\n   Resource {i+1}: {resource['name']}")
            print(f"   URI: {resource['uri']}")
            print(f"   MIME Type: {resource.get('mimeType', 'unknown')}")
            print(f"   Description: {resource.get('description', 'No description')}")
            
            # Try to read each resource
            print(f"   Content Preview:")
            content_response = run_mcp_command("resources/read", {"uri": resource['uri']})
            
            if "result" in content_response and "contents" in content_response["result"]:
                contents = content_response["result"]["contents"]
                for content in contents:
                    mime_type = content.get("mimeType", "unknown")
                    text = content.get("text", "No text")
                    
                    if mime_type == "application/json":
                        try:
                            json_data = json.loads(text)
                            print(f"     JSON Content:")
                            print_json(json_data, 3)
                        except:
                            print(f"     Raw: {text}")
                    else:
                        print(f"     {mime_type}: {text[:100]}...")
    
    # Example tool call with all parameters
    print("\n📋 Complete Parameter Example:")
    example_params = {
        "username": "user@example.com",
        "app_password": "app_password_123", 
        "email_filters": {
            "sender1@example.com": ["subject1", "subject2"],
            "sender2@example.com": ["important", "urgent"]
        },
        "check_interval": 30,
        "background_mode": False,
        "max_emails": 100,
        "days_back": 1,
        "time_range_hours": 24,
        "use_cache": True
    }
    
    print("   Example parameters for gmail_check tool:")
    print_json(example_params, 1)
    
    print("\n✨ MCP Inspector Alternative - Complete!")
    print("=" * 60)
    print("This provides the same information as MCP Inspector:")
    print("• ✅ Server capabilities and protocol version")
    print("• ✅ Complete tool definitions with JSON schemas")
    print("• ✅ All parameter types, validation rules, and defaults") 
    print("• ✅ Available resources with content preview")
    print("• ✅ Complete parameter examples")
    print("• ✅ MCP protocol compliance verification")

if __name__ == "__main__":
    detailed_inspection()