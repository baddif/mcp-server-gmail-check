#!/usr/bin/env python3
"""
MCP Server for Gmail Check Skill

This script provides a Model Context Protocol (MCP) server implementation
that exposes the Gmail Check Skill as MCP tools, resources, and prompts.

Usage:
    python mcp_server.py
    
The server will start and listen for MCP requests, making the Gmail Check Skill
available to AI agents and other MCP clients.
"""

import json
import sys
import asyncio
from typing import Any, Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the skill and compatibility layer
try:
    from gmail_check_skill import GmailCheckSkill
    from ldr_compat import ExecutionContext
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)


class GmailCheckMcpServer:
    """MCP Server for Gmail Check Skill"""
    
    def __init__(self):
        self.skill = GmailCheckSkill()
        self.context = ExecutionContext()
        
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "name": "gmail-check-mcp-server",
            "version": "1.0.0",
            "description": "MCP server for Gmail email checking and filtering",
            "author": "Gmail Check Skill",
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": False
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        schema = self.skill.get_openai_schema()
        
        # Convert OpenAI schema to MCP tool format
        mcp_tool = {
            "name": schema["function"]["name"],
            "description": schema["function"]["description"],
            "inputSchema": schema["function"]["parameters"]
        }
        
        return [mcp_tool]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool"""
        if name != "gmail_check":
            return {
                "error": f"Unknown tool: {name}",
                "success": False
            }
        
        try:
            result = self.skill.execute(self.context, **arguments)
            
            # Convert skill result to MCP response format
            if result.get("success"):
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False, indent=2)
                        }
                    ]
                }
            else:
                return {
                    "error": result.get("error", {}).get("message", "Unknown error"),
                    "success": False
                }
                
        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}")
            return {
                "error": f"Tool execution failed: {str(e)}",
                "success": False
            }
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        resources = self.skill.get_mcp_resources()
        
        return [
            {
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mime_type
            }
            for resource in resources
        ]
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource"""
        try:
            resource_data = self.skill.read_resource(uri)
            return resource_data
        except Exception as e:
            logger.error(f"Resource read error: {str(e)}")
            return {
                "error": f"Failed to read resource: {str(e)}"
            }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request"""
        method = request.get("method", "")
        params = request.get("params", {})
        
        try:
            if method == "initialize":
                return {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": self.get_server_info()
                }
            
            elif method == "tools/list":
                return {
                    "tools": self.list_tools()
                }
            
            elif method == "tools/call":
                name = params.get("name", "")
                arguments = params.get("arguments", {})
                return self.call_tool(name, arguments)
            
            elif method == "resources/list":
                return {
                    "resources": self.list_resources()
                }
            
            elif method == "resources/read":
                uri = params.get("uri", "")
                return self.read_resource(uri)
            
            else:
                return {
                    "error": f"Unknown method: {method}",
                    "code": -32601
                }
                
        except Exception as e:
            logger.error(f"Request handling error: {str(e)}")
            return {
                "error": f"Internal server error: {str(e)}",
                "code": -32603
            }


class StdioTransport:
    """Standard I/O transport for MCP communication"""
    
    def __init__(self, server: GmailCheckMcpServer):
        self.server = server
    
    async def run(self):
        """Run the stdio transport"""
        logger.info("Starting Gmail Check MCP Server...")
        logger.info("Listening for requests on stdin...")
        
        try:
            while True:
                # Read line from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Parse JSON request
                    request = json.loads(line)
                    
                    # Handle request
                    response = self.server.handle_request(request)
                    
                    # Add ID if present in request
                    if "id" in request:
                        response["id"] = request["id"]
                    
                    # Send response
                    response_json = json.dumps(response, ensure_ascii=False)
                    print(response_json, flush=True)
                    
                except json.JSONDecodeError as e:
                    error_response = {
                        "error": f"Invalid JSON: {str(e)}",
                        "code": -32700
                    }
                    if "id" in locals():
                        error_response["id"] = None
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
        finally:
            logger.info("Gmail Check MCP Server stopped")


def test_server():
    """Test the MCP server with sample requests"""
    print("Testing Gmail Check MCP Server...")
    
    server = GmailCheckMcpServer()
    
    # Test server info
    print("\n1. Server Info:")
    print(json.dumps(server.get_server_info(), indent=2))
    
    # Test tools list
    print("\n2. Available Tools:")
    print(json.dumps(server.list_tools(), indent=2, ensure_ascii=False))
    
    # Test resources list
    print("\n3. Available Resources:")
    print(json.dumps(server.list_resources(), indent=2, ensure_ascii=False))
    
    # Test resource read
    print("\n4. Test Resource Read:")
    resource_result = server.read_resource("skill://gmail_check/cache_status")
    print(json.dumps(resource_result, indent=2, ensure_ascii=False))
    
    print("\n✅ MCP Server test completed!")


async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_server()
        return
    
    # Create server and transport
    server = GmailCheckMcpServer()
    transport = StdioTransport(server)
    
    # Run the server
    await transport.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server startup failed: {str(e)}")
        sys.exit(1)