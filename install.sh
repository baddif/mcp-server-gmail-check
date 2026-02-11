#!/bin/bash

# Gmail Check MCP Server Installation Script
# This script sets up the Gmail Check Skill as an MCP server

set -e

echo "🚀 Gmail Check MCP Server Installation"
echo "======================================"

# Get the installation directory
INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "📁 Installation directory: $INSTALL_DIR"

# Check Python version
echo "🐍 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 is required but not found"
    exit 1
}

# Install Python dependencies (if requirements.txt exists)
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r "$INSTALL_DIR/requirements.txt" || {
        echo "⚠️  Failed to install dependencies, continuing anyway..."
    }
fi

# Test the server
echo "🧪 Testing MCP server..."
cd "$INSTALL_DIR"
python3 mcp_server.py --test || {
    echo "❌ Server test failed"
    exit 1
}

# Generate MCP configuration
echo "⚙️  Generating MCP configuration..."
MCP_CONFIG_DIR="$HOME/.config/mcp"
mkdir -p "$MCP_CONFIG_DIR"

# Update the config template with actual path
sed "s|/path/to/mcp-server-gmail-check|$INSTALL_DIR|g" "$INSTALL_DIR/mcp_config.json" > "$MCP_CONFIG_DIR/gmail-check.json"

echo "✅ Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Configure your Gmail credentials:"
echo "   cp $INSTALL_DIR/gmail_config_example.json $INSTALL_DIR/gmail_config_local.json"
echo "   # Edit gmail_config_local.json with your real credentials"
echo ""
echo "2. Test the configuration:"
echo "   cd $INSTALL_DIR && python3 test_gmail_skill.py"
echo ""
echo "3. MCP configuration saved to:"
echo "   $MCP_CONFIG_DIR/gmail-check.json"
echo ""
echo "4. Add to your MCP client configuration or Claude Desktop:"
echo "   Include the content of gmail-check.json in your MCP settings"
echo ""
echo "5. Start using the Gmail Check skill in your AI agent!"
echo ""
echo "🔧 Manual server start: cd $INSTALL_DIR && python3 mcp_server.py"
echo "📖 Documentation: $INSTALL_DIR/PROJECT_README.md"