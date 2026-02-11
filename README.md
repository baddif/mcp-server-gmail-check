# Gmail Check MCP Server

🔧 **AI-Powered Gmail Integration for MCP (Model Context Protocol)**

A comprehensive skill for checking Gmail emails with advanced filtering, caching, and AI agent integration. Supports both standalone operation and MCP server mode for use with Claude Desktop and other AI agents.

## ✨ Features

- 🔍 **Smart Email Filtering** - Filter by sender, subject (partial match), date range, and read status
- 📧 **Full Content Download** - Download email headers, body content, and metadata  
- 💾 **Intelligent Caching** - 30-minute cache with hash-based deduplication
- 🤖 **MCP Compatible** - Full Model Context Protocol support for AI agents
- 🌐 **Multi-Language** - Supports Chinese and English interfaces
- 🔐 **Secure Auth** - Gmail app password authentication
- ⚡ **High Performance** - Optimized IMAP operations with connection reuse

## 🚀 Quick Start

### Option 1: One-Click Installation (Recommended)

```bash
# Clone and install
git clone https://github.com/baddif/mcp-server-gmail-check.git
cd mcp-server-gmail-check
bash install.sh

# Check installation
python3 version.py --info
```

### Option 2: Manual Installation

```bash
# 1. Clone repository
git clone https://github.com/baddif/mcp-server-gmail-check.git
cd mcp-server-gmail-check

# 2. Install Python dependencies
pip3 install -r requirements.txt

# 3. Configure Gmail credentials
cp gmail_config_example.json gmail_config_local.json
# Edit gmail_config_local.json with your credentials

# 4. Test installation
python3 test_gmail_skill.py

# 5. Check version
python3 version.py --version
```

## 🔄 Version Control & Updates

### Check Current Version

```bash
# Show version information
python3 version.py --info

# Show version string only
python3 version.py --version

# Check for available updates
python3 version.py --check-updates

# Get version data as JSON
python3 version.py --json
```

### Automatic Updates

#### One-Click Update (Recommended)
```bash
# Automatic update with backup
./update.sh

# Check for updates without applying
./update.sh --check

# Show update help
./update.sh --help
```

#### Manual Update Process
```bash
# 1. Backup your configuration
cp gmail_config_local.json gmail_config_backup.json

# 2. Check for uncommitted changes
git status

# 3. Pull latest changes
git pull origin main

# 4. Update dependencies
pip3 install -r requirements.txt --upgrade

# 5. Test installation
python3 mcp_server.py --test

# 6. Restore configuration if needed
# (your gmail_config_local.json is preserved automatically)
```

### Version Information

- **Current Version**: v1.1.0 (2026-02-12)
- **MCP Compatibility**: 2024-11-05
- **Python Requirement**: 3.7+
- **Update Method**: Git-based with automatic dependency management

### What's New in v1.1.0

- ⏱️ **Enhanced Time Control**: `time_range_hours` parameter for precise timing (1-720 hours)
- 💾 **Cache Management**: `use_cache` parameter for flexible cache control
- 🔄 **Version Control**: Automatic update system with configuration backup
- 📚 **Improved Documentation**: Comprehensive parameter guides and examples

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

### Backup & Recovery

The update script automatically backs up:
- `gmail_config_local.json` - Your private Gmail credentials
- `claude_desktop_config.json` - Claude Desktop configuration
- Any custom configuration files

Backups are stored in timestamped folders: `backup_YYYYMMDD_HHMMSS/`

### Update Troubleshooting

**Update Script Fails**
```bash
# Check Git repository status
git status

# Manual update
git fetch origin main
git pull origin main
```

**Dependencies Issues**
```bash
# Force reinstall dependencies
pip3 install -r requirements.txt --force-reinstall

# Check Python version
python3 --version
```

**Configuration Lost**
```bash
# Restore from backup (replace with your backup folder)
cp backup_20260212_143000/gmail_config_local.json .
```

## ⚙️ Configuration

### Gmail App Password Setup

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and generate password
3. **Configure credentials** in `gmail_config_local.json`:

```json
{
    "username": "your_email@gmail.com",
    "password": "your_16_digit_app_password",
    "imap_server": "imap.gmail.com",
    "imap_port": 993
}
```

### Configuration Files

- `gmail_config_example.json` - Public template (safe to commit)
- `gmail_config_local.json` - Your private config (gitignored)

## 📖 Usage Examples

### Standalone Python Usage

```python
from gmail_check_skill import GmailCheckSkill
from ldr_compat import ExecutionContext

# Initialize skill
skill = GmailCheckSkill()
ctx = ExecutionContext()

# Check recent emails
result = skill.execute(ctx, 
    sender_filter="notifications@github.com",
    max_emails=10,
    download_content=True
)

print(f"Found {len(result['data']['emails'])} emails")
```

### MCP Server Integration

#### Start MCP Server
```bash
# Start MCP server for AI agent integration
python3 mcp_server.py

# Test MCP server
python3 mcp_server.py --test
```

#### Claude Desktop Integration
Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gmail-check": {
      "command": "python3",
      "args": ["/path/to/mcp-server-gmail-check/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/mcp-server-gmail-check"
      }
    }
  }
}
```

#### Generic MCP Client
```python
from mcp import ClientSession, StdioServerParameters

async def use_gmail_skill():
    server_params = StdioServerParameters(
        command="python3",
        args=["/path/to/mcp-server-gmail-check/mcp_server.py"]
    )
    
    async with ClientSession(server_params) as session:
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        
        # Check emails
        result = await session.call_tool("gmail_check", {
            "sender_filter": "important@company.com",
            "days_back": 7,
            "download_content": True
        })
        
        return result
```

## 🔧 Function Parameters

The Gmail Check MCP Server **完全支持参数传递**！以下是所有可用参数：

### 📋 Complete Parameter List

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `username` | string | ✅ YES | - | Gmail username (email address) |
| `app_password` | string | ✅ YES | - | Gmail 16-digit app password |
| `email_filters` | object | ✅ YES | - | Email filters: `{"sender": ["subject1", "subject2"]}` |
| `check_interval` | integer | ❌ No | 30 | Check interval in minutes (1-1440) |
| `background_mode` | boolean | ❌ No | false | Continuous monitoring mode |
| `max_emails` | integer | ❌ No | 100 | Max emails per check (1-1000) |
| `days_back` | integer | ❌ No | 1 | Days to look back (1-30) |
| `time_range_hours` | integer | ❌ No | 24 | Time range in hours from current time (1-720, overrides days_back) |
| `use_cache` | boolean | ❌ No | true | Whether to use cache to avoid re-processing emails |

### 🎯 Parameter Usage Examples

#### Basic Email Check
```json
{
  "username": "your_email@gmail.com",
  "app_password": "your_16_digit_app_password",
  "email_filters": {
    "notifications@github.com": ["pull request", "issue"],
    "billing@aws.amazon.com": ["invoice", "bill"]
  },
  "max_emails": 20,
  "days_back": 3
}
```

#### Background Monitoring
```json
{
  "username": "monitor@gmail.com", 
  "app_password": "monitoring_password",
  "email_filters": {
    "alerts@company.com": ["urgent", "critical", "error"],
    "support@service.com": ["ticket", "request"]
  },
  "background_mode": true,
  "check_interval": 15,
  "max_emails": 50,
  "days_back": 1
}
```

#### Comprehensive Scan
```json
{
  "username": "admin@domain.com",
  "app_password": "admin_app_password", 
  "email_filters": {
    "security@bank.com": ["alert", "fraud"],
    "notifications@system.com": ["down", "maintenance"],
    "reports@analytics.com": ["weekly", "monthly"]
  },
  "max_emails": 200,
  "days_back": 7,
  "check_interval": 60
}
```

#### Precise Time Range Check
```json
{
  "username": "monitor@company.com",
  "app_password": "precise_monitoring_pwd",
  "email_filters": {
    "alerts@system.com": ["critical", "error"]
  },
  "time_range_hours": 6,
  "use_cache": false,
  "max_emails": 50
}
```

#### Cache-Disabled Full Scan
```json
{
  "username": "audit@company.com", 
  "app_password": "audit_app_password",
  "email_filters": {
    "compliance@bank.com": ["violation", "audit"],
    "security@company.com": ["breach", "incident"]
  },
  "time_range_hours": 72,
  "use_cache": false,
  "max_emails": 500
}
```

### 🤖 MCP Client Integration with Parameters

#### Direct JSON-RPC Call
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "gmail_check",
    "arguments": {
      "username": "user@gmail.com",
      "app_password": "your_app_password",
      "email_filters": {
        "important@company.com": ["urgent", "action required"]
      },
      "max_emails": 25,
      "days_back": 2
    }
  }
}
```

#### Python MCP Client
```python
async def check_emails_with_params():
    server_params = StdioServerParameters(
        command="python3",
        args=["/path/to/mcp_server.py"]
    )
    
    async with ClientSession(server_params) as session:
        await session.initialize()
        
        # Call with custom parameters
        result = await session.call_tool("gmail_check", {
            "username": "your_email@gmail.com",
            "app_password": "your_app_password",
            "email_filters": {
                "github@notifications.com": ["mentioned", "review"],
                "alerts@system.com": ["critical", "down"]
            },
            "max_emails": 30,
            "days_back": 3,
            "background_mode": False
        })
        
        return result
```

#### Claude Desktop with Parameters
When using Claude Desktop, you can specify parameters in your conversation:

```
"Check my Gmail for:
- GitHub notifications about pull requests from last 2 days  
- System alerts containing 'critical' or 'error' from last week
- Maximum 50 emails
- Username: developer@company.com
- Use background mode for continuous monitoring"
```

### ⚡ Quick Test Commands

```bash
# Test parameter validation
python3 test_mcp_parameters.py

# Simulate MCP client with parameters  
python3 demo_mcp_client.py

# Test real MCP server
echo '{"method":"tools/call","params":{"name":"gmail_check","arguments":{"username":"test@gmail.com","app_password":"test123","email_filters":{"test@example.com":["test"]}}}}' | python3 mcp_server.py
```
```

## 🏗️ Project Structure

```
mcp-server-gmail-check/
├── 📧 Core Implementation
│   ├── gmail_check_skill.py      # Main Gmail skill
│   ├── mcp_server.py             # MCP protocol server  
│   └── ldr_compat.py             # Framework compatibility
├── 🧪 Testing & Validation
│   ├── test_gmail_skill.py       # Comprehensive tests
│   ├── test_mcp_parameters.py    # Parameter validation tests
│   └── test_mcp_server.py        # MCP server tests
├── ⚙️ Configuration
│   ├── gmail_config_example.json # Public template
│   ├── gmail_config_local.json   # Private config (gitignored)
│   └── claude_desktop_config.json # Claude Desktop setup
├── 🚀 Deployment & Updates
│   ├── install.sh               # One-click installation
│   ├── update.sh                # Automatic update script
│   ├── version.py               # Version management system
│   ├── requirements.txt         # Python dependencies
│   └── .gitignore              # Security exclusions
└── 📚 Documentation
    ├── README.md               # This file
    ├── CHANGELOG.md            # Version history & updates
    ├── MCP_DEPLOYMENT.md       # MCP integration guide
    └── SKILL_GENERATION_RULES.md # Development standards
```

## 🔒 Security Features

- ✅ **App Password Auth** - Uses Gmail app passwords, not main password
- ✅ **Config Isolation** - Private credentials separated from code
- ✅ **Git Security** - Sensitive files automatically gitignored
- ✅ **Input Validation** - All parameters validated and sanitized
- ✅ **Error Handling** - Secure error messages without credential leaks

## 🚀 Performance Optimizations

- ⚡ **Connection Reuse** - Persistent IMAP connections
- 💾 **Smart Caching** - 30-minute cache with hash-based deduplication  
- 🔍 **Efficient Search** - Server-side IMAP SEARCH commands
- 📊 **Batch Processing** - Bulk email operations
- 🧹 **Memory Management** - Automatic cleanup and connection management

## 🔍 Troubleshooting

### Common Issues

**Authentication Failed**
```bash
# Check credentials
python3 -c "
import json
with open('gmail_config_local.json') as f:
    config = json.load(f)
print('Username:', config['username'])
print('Password length:', len(config['password']))
"
```

**No Emails Found**
- Check date range with `days_back` parameter
- Verify sender/subject filters are correct
- Ensure Gmail IMAP is enabled

**MCP Server Issues**
```bash
# Test MCP server functionality
python3 mcp_server.py --test

# Check MCP configuration
echo '{"method":"initialize","params":{},"id":1}' | python3 mcp_server.py
```

### Debug Mode

Enable detailed debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug output
result = skill.execute(ctx, sender_filter="test@example.com")
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow coding standards** in `SKILL_GENERATION_RULES.md`
4. **Add tests**: Update `test_gmail_skill.py`
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open Pull Request**

## 📋 Development Standards

This project follows the **AI-Powered Application Standards v2.0.0**:

- ✅ OpenAI Function Calling compatible
- ✅ Model Context Protocol (MCP) support
- ✅ Framework-agnostic design
- ✅ Comprehensive error handling
- ✅ Multi-language support
- ✅ Security-first configuration

See `SKILL_GENERATION_RULES.md` for detailed development guidelines.

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [Claude Desktop](https://claude.ai/desktop) - AI assistant with MCP support
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling) - Function calling standard

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/baddif/mcp-server-gmail-check/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/baddif/mcp-server-gmail-check/discussions)
- 📖 **Documentation**: See `MCP_DEPLOYMENT.md` for advanced setup
- 🔄 **Updates**: Use `./update.sh` for automatic updates or check `CHANGELOG.md`
- 📊 **Version Info**: Run `python3 version.py --info` for current version details

### Getting Help

**Before reporting issues, please:**
1. Check your version: `python3 version.py --version`
2. Try updating: `./update.sh --check`
3. Review [CHANGELOG.md](CHANGELOG.md) for known issues
4. Test basic functionality: `python3 mcp_server.py --test`

**Include in bug reports:**
- Version information (`python3 version.py --json`)
- Error messages and logs
- Configuration (without credentials)
- Steps to reproduce the issue

---

**Made with ❤️ for the AI-powered future**
