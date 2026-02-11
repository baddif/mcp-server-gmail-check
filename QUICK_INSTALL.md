# 🚀 Quick Install Guide

## GitHub Repository
```bash
https://github.com/baddif/mcp-server-gmail-check
```

## One-Command Installation

```bash
git clone https://github.com/baddif/mcp-server-gmail-check.git && cd mcp-server-gmail-check && bash install.sh
```

## Manual Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/baddif/mcp-server-gmail-check.git
cd mcp-server-gmail-check
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Configure Gmail
```bash
# Copy configuration template
cp gmail_config_example.json gmail_config_local.json

# Edit with your Gmail credentials
nano gmail_config_local.json
```

**Gmail Configuration:**
```json
{
    "username": "your_email@gmail.com",
    "password": "your_16_digit_app_password",
    "imap_server": "imap.gmail.com", 
    "imap_port": 993
}
```

### 4. Test Installation
```bash
python3 test_gmail_skill.py
```

### 5. Start MCP Server (for AI agents)
```bash
python3 mcp_server.py
```

## Claude Desktop Integration

Add to `~/.config/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gmail-check": {
      "command": "python3",
      "args": ["/full/path/to/mcp-server-gmail-check/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/full/path/to/mcp-server-gmail-check"
      }
    }
  }
}
```

## Quick Test Commands

```bash
# Test standalone
python3 -c "
from gmail_check_skill import GmailCheckSkill
from ldr_compat import ExecutionContext
skill = GmailCheckSkill()
ctx = ExecutionContext()
result = skill.execute(ctx, max_emails=5)
print(f'Found {len(result[\"data\"][\"emails\"])} emails')
"

# Test MCP server
python3 mcp_server.py --test
```

## Need Help?

- 📖 **Full Documentation**: See `README.md`
- 🐛 **Issues**: https://github.com/baddif/mcp-server-gmail-check/issues
- 💡 **Discussions**: https://github.com/baddif/mcp-server-gmail-check/discussions

---

**✅ Ready to integrate with any AI agent!**