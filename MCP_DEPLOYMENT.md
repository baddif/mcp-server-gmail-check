# Gmail Check MCP Server 部署指南

这个项目提供了完整的MCP (Model Context Protocol) 服务器实现，可以被各种AI agent和MCP客户端使用。

## 🎯 MCP兼容性

✅ **完全支持MCP标准**
- 实现了MCP 2024-11-05协议版本
- 提供Tools、Resources接口
- 标准JSON-RPC通信协议
- 支持stdio传输层

## 🚀 部署方式

### 方式1: 自动安装 (推荐)

```bash
# 克隆项目
git clone https://github.com/baddif/mcp-server-gmail-check.git
cd mcp-server-gmail-check

# 运行自动安装脚本
./install.sh
```

### 方式2: 手动安装

1. **克隆项目**
```bash
git clone https://github.com/baddif/mcp-server-gmail-check.git
cd mcp-server-gmail-check
```

2. **安装依赖** (可选)
```bash
pip3 install -r requirements.txt
```

3. **配置认证信息**
```bash
cp gmail_config_example.json gmail_config_local.json
# 编辑 gmail_config_local.json 填入真实的Gmail认证信息
```

4. **测试服务器**
```bash
python3 mcp_server.py --test
```

## 🔧 配置AI Agent

### Claude Desktop配置

将以下配置添加到Claude Desktop的MCP设置中：

```json
{
  "mcpServers": {
    "gmail-check": {
      "command": "python3",
      "args": [
        "/path/to/mcp-server-gmail-check/mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/mcp-server-gmail-check"
      }
    }
  }
}
```

### 其他MCP客户端

使用标准MCP客户端库连接到服务器：

```python
from mcp import ClientSession, StdioServerParameters

async def connect_to_gmail_server():
    server_params = StdioServerParameters(
        command="python3",
        args=["/path/to/mcp-server-gmail-check/mcp_server.py"]
    )
    
    async with ClientSession(server_params) as session:
        # 初始化连接
        await session.initialize()
        
        # 列出可用工具
        tools = await session.list_tools()
        print("Available tools:", tools)
        
        # 调用Gmail检查工具
        result = await session.call_tool(
            "gmail_check",
            {
                "username": "your-email@gmail.com",
                "app_password": "your-app-password",
                "email_filters": {
                    "sender@example.com": ["关键词"]
                }
            }
        )
        print("Gmail check result:", result)
```

## 🛠️ 服务器功能

### 可用工具 (Tools)

#### `gmail_check`
Gmail邮件检测和过滤工具

**参数:**
- `username` (required): Gmail邮箱地址
- `app_password` (required): Gmail应用专用密码
- `email_filters` (required): 邮件过滤规则
- `check_interval` (optional): 检测间隔(分钟), 默认30
- `background_mode` (optional): 后台模式, 默认false
- `max_emails` (optional): 最大邮件数, 默认100
- `days_back` (optional): 检查天数, 默认1

**返回:** 匹配的邮件列表和统计信息

### 可用资源 (Resources)

#### `skill://gmail_check/latest_results`
最新的Gmail检查结果

#### `skill://gmail_check/cache_status`
缓存状态和统计信息

#### `skill://gmail_check/monitoring_status`
后台监控状态信息

## 🔐 安全注意事项

1. **保护认证信息**: 
   - 使用`gmail_config_local.json`存储真实认证信息
   - 该文件已在`.gitignore`中被排除
   - 不要在代码中硬编码密码

2. **Gmail App Password**:
   - 必须开启两步验证
   - 使用应用专用密码，不是普通密码
   - 16字符无空格格式

3. **网络访问**:
   - 需要访问`imap.gmail.com:993`
   - 确保防火墙允许IMAP连接

## 🧪 测试和调试

### 测试MCP服务器
```bash
python3 mcp_server.py --test
```

### 测试Gmail功能
```bash
python3 test_gmail_skill.py
```

### 调试模式
服务器会输出详细的调试信息，包括:
- 邮件匹配过程
- 中文字符解码
- 缓存操作
- 错误详情

## 🔄 更新和维护

### 更新代码
```bash
git pull origin main
```

### 清理缓存
```bash
rm .gmail_check_cache.json
```

### 查看日志
服务器运行时会输出实时日志信息

## 🤝 兼容的AI Agent

这个MCP服务器可以与以下AI agent和客户端配合使用：

- **Claude Desktop** - Anthropic的桌面应用
- **任何MCP兼容客户端** - 使用标准MCP协议
- **自定义AI Agent** - 通过MCP库集成
- **VS Code扩展** - 支持MCP的开发工具

## 📖 更多信息

- [项目文档](PROJECT_README.md)
- [详细使用指南](README_gmail_skill.md)
- [MCP协议规范](https://spec.modelcontextprotocol.io/)
- [GitHub仓库](https://github.com/baddif/mcp-server-gmail-check)

## 🆘 故障排除

### 常见问题

1. **连接失败**
   - 检查网络连接
   - 验证Gmail认证信息
   - 确认防火墙设置

2. **MCP客户端无法连接**
   - 检查Python路径是否正确
   - 验证MCP配置文件格式
   - 查看服务器日志输出

3. **邮件匹配问题**
   - 检查邮件过滤器配置
   - 查看调试日志
   - 验证邮件时间范围

### 获取帮助

如果遇到问题，请：
1. 查看项目文档
2. 运行测试脚本确认功能
3. 在GitHub仓库提交Issue