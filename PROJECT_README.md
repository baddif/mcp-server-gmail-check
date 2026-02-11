# Gmail Check Skill

基于SKILL_GENERATION_RULES.md规范开发的Gmail邮件检测skill，完全符合LocalDailyReport框架要求。

## 项目文件

- `gmail_check_skill.py` - 主要的skill实现
- `mcp_server.py` - MCP服务器实现，支持AI agent集成
- `ldr_compat.py` - 框架兼容模块，支持独立运行
- `test_gmail_skill.py` - 测试脚本
- `example_usage.py` - 使用示例
- `gmail_config_example.json` - 配置文件示例模板
- `gmail_config_local.json` - 本地测试配置（需自己创建，不会上传git）
- `claude_desktop_config.json` - Claude Desktop配置示例
- `install.sh` - 自动安装脚本
- `MCP_DEPLOYMENT.md` - MCP部署和使用指南
- `README_gmail_skill.md` - 详细使用文档
- `requirements.txt` - 依赖包说明
- `.gitignore` - Git忽略文件配置

## 主要功能

✅ **完全符合SKILL_GENERATION_RULES.md规范**
- 实现了`McpCompatibleSkill`基类
- 提供OpenAI Function Calling兼容的JSON Schema
- 支持MCP (Model Context Protocol)标准
- 包含完整的错误处理和返回格式

✅ **Gmail邮件检测核心功能**
- 使用Gmail App Password进行安全认证
- 支持按发件人和主题过滤邮件
- 仅下载匹配的邮件内容，保持未匹配邮件状态
- 智能缓存机制避免重复处理
- 默认30分钟检测间隔，可自定义
- 支持后台监控模式

✅ **技术特性**
- 线程安全的缓存机制
- 支持独立运行（无需完整框架）
- **完整的MCP服务器实现，可被AI agent使用**
- 完整的MCP资源和工具定义
- 符合JSON Schema规范的参数验证
- 优雅的错误处理和故障排除

## 快速开始

### 作为独立Python Skill使用

#### 1. 测试Schema（无需认证信息）

```bash
python3 test_gmail_skill.py
```

#### 2. 配置认证信息

**方法1: 创建本地配置文件（推荐）**

复制示例配置并填入真实信息：

```bash
cp gmail_config_example.json gmail_config_local.json
```

然后编辑 `gmail_config_local.json`:

```json
{
  "username": "your-email@gmail.com",
  "app_password": "your-16-char-password",
  "email_filters": {
    "sender@example.com": ["关键词1", "关键词2"]
  }
}
```

**方法2: 使用环境变量**

```bash
export GMAIL_USERNAME='your-email@gmail.com'
export GMAIL_APP_PASSWORD='your-app-password'
```

#### 3. 运行测试

```bash
python3 test_gmail_skill.py
# 会自动优先使用 gmail_config_local.json
```

### 作为MCP服务器使用（AI Agent集成）

#### 1. 快速安装

```bash
git clone https://github.com/baddif/mcp-server-gmail-check.git
cd mcp-server-gmail-check
./install.sh
```

#### 2. 配置AI Agent

**Claude Desktop配置:**

```json
{
  "mcpServers": {
    "gmail-check": {
      "command": "python3",
      "args": ["/path/to/mcp-server-gmail-check/mcp_server.py"]
    }
  }
}
```

#### 3. 在AI Agent中使用

AI可以直接调用Gmail检测功能：
- 工具名称: `gmail_check`
- 支持的资源: 缓存状态、检测结果等
- 完整的参数验证和错误处理

📖 **详细MCP部署指南**: [MCP_DEPLOYMENT.md](MCP_DEPLOYMENT.md)

### 4. 在代码中使用

```python
from gmail_check_skill import GmailCheckSkill
from ldr_compat import ExecutionContext

skill = GmailCheckSkill()
ctx = ExecutionContext()

result = skill.execute(ctx, 
    username="your-email@gmail.com",
    app_password="your-app-password", 
    email_filters={"sender@example.com": ["subject1", "subject2"]}
)
```

## 参数说明

### 必需参数

| 参数 | 类型 | 说明 |
|------|------|------|
| username | string | Gmail邮箱地址 |
| app_password | string | Gmail应用专用密码（16字符） |
| email_filters | object | 邮件过滤规则 `{"发件人": ["主题关键词"]}` |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|-------|------|
| check_interval | integer | 30 | 检测间隔（分钟），范围1-1440 |
| background_mode | boolean | false | 是否后台监控模式 |
| max_emails | integer | 100 | 每次检测的最大邮件数，范围1-1000 |
| days_back | integer | 1 | 检测几天内的邮件，范围1-30 |

## 输出格式

### 成功响应

```json
{
  "success": true,
  "function_name": "gmail_check",
  "data": {
    "matched_emails": [
      {
        "sender": "sender@example.com",
        "subject": "邮件主题",
        "content": "邮件正文内容...",
        "date_received": "Mon, 10 Feb 2026 10:00:00 +0000",
        "message_id": "<message-id@example.com>",
        "matched_sender_filter": "sender@example.com",
        "matched_subject_filters": ["关键词"],
        "email_id": "唯一标识符"
      }
    ],
    "check_time": "2026-02-11T08:00:00Z",
    "total_matched": 1,
    "background_mode": false
  },
  "statistics": {
    "emails_checked": 1,
    "cache_size": 10,
    "filters_applied": 1
  }
}
```

## Gmail App Password设置

1. 登录Google账户设置
2. 选择"安全性" → "两步验证"
3. 开启两步验证
4. 选择"应用专用密码"
5. 生成新密码，选择"邮件"
6. 复制16位密码（无空格）

## 缓存机制

- 缓存文件：`.gmail_check_cache.json`
- 自动记录已处理邮件的唯一ID
- 基于邮件ID和接收时间生成哈希
- 防止重复处理相同邮件
- 支持手动清理缓存

## MCP支持

提供以下MCP资源：

- `skill://gmail_check/latest_results` - 最新检测结果
- `skill://gmail_check/cache_status` - 缓存状态信息  
- `skill://gmail_check/monitoring_status` - 监控状态信息

## 设计特点

### 符合规范

1. **Schema设计**: 完全符合OpenAI Function Calling规范
2. **错误处理**: 统一的错误返回格式
3. **参数验证**: JSON Schema约束和默认值
4. **MCP兼容**: 支持Tools、Resources、Prompts
5. **文档规范**: 详细的参数和功能描述

### 实现质量

1. **安全性**: 使用App Password，避免明文密码
2. **性能**: 智能缓存，避免重复处理
3. **稳定性**: 完整错误处理，网络异常恢复
4. **可维护性**: 模块化设计，清晰的代码结构
5. **可扩展性**: 支持多种过滤模式，可扩展功能

### 用户友好

1. **独立运行**: 无需完整框架即可测试
2. **配置灵活**: 支持环境变量、配置文件、代码配置
3. **故障排除**: 详细的错误信息和解决建议
4. **文档完整**: 包含示例、测试、故障排除指南

## 开发信息

- **遵循标准**: LocalDailyReport SKILL_GENERATION_RULES.md v1.0.0
- **兼容性**: OpenAI Function Calling + MCP (Model Context Protocol)
- **语言**: Python 3.7+
- **依赖**: 仅使用Python标准库（imaplib, email, json等）
- **许可**: 根据项目许可证

## 故障排除

### 认证问题
- 确认已开启两步验证
- 检查App Password格式（16字符无空格）
- 验证邮箱地址正确

### 连接问题
- 检查网络连接
- 确认防火墙设置
- 尝试使用VPN

### 过滤不准确
- 检查发件人邮箱地址完全匹配
- 主题匹配为包含关系（大小写不敏感）
- 查看详细日志确认过滤逻辑

---

这个skill完全按照你的需求和SKILL_GENERATION_RULES.md规范实现，提供了Gmail邮件检测的完整功能，支持后台监控、智能缓存、MCP标准等特性。