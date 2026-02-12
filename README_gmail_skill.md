# Gmail Check Skill

这是一个用于检测Gmail邮件的Python skill，符合LocalDailyReport框架的SKILL_GENERATION_RULES.md规范。

## 功能特性

- **App Password认证**: 使用Gmail应用专用密码进行安全连接
- **邮件过滤**: 根据发件人和主题进行精确过滤
- **内容下载**: 仅下载符合条件的邮件内容
- **缓存机制**: 避免重复处理已读取的邮件
- **后台监控**: 支持定时自动检测邮件
- **MCP兼容**: 完全支持Model Context Protocol标准

## 安装依赖

```bash
# 安装所需的Python包
pip install imaplib-ssl
```

## 使用方法

### 基本用法

```python
from gmail_check_skill import GmailCheckSkill
from ldr.context import ExecutionContext

# 创建skill实例
skill = GmailCheckSkill()
ctx = ExecutionContext()

# 配置参数
params = {
    "username": "your-email@gmail.com",
    "app_password": "your-16-char-app-password",
    "email_filters": {
        "sender1@example.com": ["重要通知", "系统报告"],
        "sender2@company.com": ["项目更新", "会议安排"]
    },
    "check_interval": 30,  # 30分钟检测一次
    "background_mode": False,  # 一次性检测
    "max_emails": 100,
    "days_back": 1
}

# 执行检测
result = skill.execute(ctx, **params)
print(result)
```

### 后台监控模式

```python
# 启动后台监控
params["background_mode"] = True
result = skill.execute(ctx, **params)

# 停止监控
skill.stop_monitoring()
```

## 参数说明

### 必需参数

- **username** (string): Gmail邮箱地址
- **app_password** (string): Gmail应用专用密码（16字符，无空格）
- **email_filters** (object): 邮件过滤规则，格式：`{"发件人邮箱": ["主题关键词1", "主题关键词2"]}`

### 可选参数

- **check_interval** (integer): 检测间隔（分钟），默认30，范围1-1440
- **background_mode** (boolean): 是否后台监控模式，默认false
- **max_emails** (integer): 每次检测的最大邮件数，默认100，范围1-1000
- **days_back** (integer): 检测几天内的邮件，默认1天，范围1-30天

## 过滤规则说明

### 发件人匹配
- **完全匹配**: 发件人邮箱必须完全匹配过滤器中指定的邮箱地址
- **大小写不敏感**: `notifications@github.com` 可以匹配 `Notifications@GitHub.com`
- **显示名称忽略**: `GitHub <notifications@github.com>` 中只匹配邮箱部分 `notifications@github.com`
- **不支持部分匹配**: `notifications@github.com` 不会匹配 `github.com` 或 `notifications`

### 主题匹配
- **部分匹配**: 主题中包含指定关键词即可匹配
- **大小写不敏感**: `重要通知` 可以匹配 `【重要通知】系统维护`

## 输出格式

### 成功响应

```json
{
  "success": true,
  "function_name": "gmail_check",
  "data": {
    "matched_emails": [
      {
        "sender": "Display Name <sender@example.com>",
        "sender_email": "sender@example.com",
        "subject": "重要通知",
        "content": "邮件正文内容...",
        "date_received": "Mon, 10 Feb 2026 10:00:00 +0000",
        "message_id": "<message-id@example.com>",
        "matched_sender_filter": "sender@example.com",
        "matched_subject_filters": ["重要通知"],
        "email_id": "abc123def456"
      }
    ],
    "check_time": "2026-02-11T08:00:00Z",
    "total_matched": 1,
    "background_mode": false
  },
  "statistics": {
    "emails_checked": 1,
    "cache_size": 10,
    "filters_applied": 2
  }
}
```

#### 邮件对象字段说明

每个匹配的邮件包含以下字段：

- **`sender`** (string): 原始发件人信息，可能包含显示名称，如 `"GitHub <notifications@github.com>"`
- **`sender_email`** (string): 纯净的发件人邮箱地址，如 `"notifications@github.com"`
- **`subject`** (string): 邮件主题（已解码中文等非ASCII字符）
- **`content`** (string): 邮件正文内容（纯文本格式）
- **`date_received`** (string): 邮件接收时间（RFC 2822格式）
- **`message_id`** (string): 邮件唯一标识符
- **`matched_sender_filter`** (string): 匹配的发件人过滤器
- **`matched_subject_filters`** (array): 匹配的主题关键词列表
- **`email_id`** (string): 内部生成的邮件哈希ID（用于缓存）

### 错误响应

```json
{
  "success": false,
  "function_name": "gmail_check",
  "error": {
    "message": "Gmail connection error: Authentication failed",
    "type": "execution_error"
  }
}
```

## Gmail App Password设置

1. 登录Google账户
2. 进入"安全设置"
3. 开启"两步验证"
4. 生成"应用专用密码"
5. 选择"邮件"应用
6. 复制生成的16位密码（无空格）

## 缓存机制

- 缓存文件：`.gmail_check_cache.json`
- 存储已处理邮件的唯一标识
- 避免重复下载相同邮件
- 基于邮件ID和接收时间生成哈希值

## MCP资源

提供以下MCP资源：

- `skill://gmail_check/latest_results` - 最新检测结果
- `skill://gmail_check/cache_status` - 缓存状态信息
- `skill://gmail_check/monitoring_status` - 监控状态信息

## 示例配置

### 配置文件示例 (gmail_config.json)

```json
{
  "username": "your-email@gmail.com",
  "app_password": "abcdefghijklmnop",
  "email_filters": {
    "notifications@github.com": ["Pull Request", "Issue"],
    "alerts@server.com": ["系统告警", "服务器状态"],
    "reports@company.com": ["日报", "周报", "月报"]
  },
  "check_interval": 15,
  "background_mode": true,
  "max_emails": 50,
  "days_back": 3
}
```

### 批处理脚本示例

```python
import json
from gmail_check_skill import GmailCheckSkill
from ldr.context import ExecutionContext

# 从配置文件加载参数
with open('gmail_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 执行检测
skill = GmailCheckSkill()
ctx = ExecutionContext()
result = skill.execute(ctx, **config)

# 处理结果
if result['success']:
    emails = result['data']['matched_emails']
    for email in emails:
        print(f"发件人: {email['sender']}")
        print(f"主题: {email['subject']}")
        print(f"内容: {email['content'][:100]}...")
        print("-" * 50)
else:
    print(f"错误: {result['error']['message']}")
```

## 注意事项

1. **安全性**: 妥善保护app password，不要在代码中硬编码
2. **频率限制**: Gmail有API调用频率限制，建议检测间隔不少于5分钟
3. **网络连接**: 确保网络能够访问Gmail IMAP服务器（imap.gmail.com:993）
4. **缓存维护**: 定期清理缓存文件，避免占用过多磁盘空间
5. **错误处理**: 网络异常时会自动重试，持续错误请检查认证信息

## 故障排除

### 认证失败
- 确认Gmail账户已开启两步验证
- 检查app password是否正确（16位无空格）
- 确认账户未被锁定

### 连接超时
- 检查网络连接
- 确认防火墙未阻止IMAP连接
- 尝试增加超时时间

### 邮件过滤不准确
- 检查发件人邮箱地址是否完全匹配
- 主题匹配为包含关系，区分大小写
- 查看日志确认过滤逻辑

## 开发者信息

- 遵循LocalDailyReport框架规范
- 支持OpenAI Function Calling标准
- 完全兼容MCP (Model Context Protocol)
- 线程安全的缓存机制
- 支持优雅停机