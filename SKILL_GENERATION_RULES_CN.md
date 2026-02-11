# 技能生成规则 - AI应用开发标准

**版本**: 2.0.0  
**最后更新**: 2026-02-11  
**目的**: AI可读的技能生成规范，用于创建支持多种AI Agent框架的智能技能

---

## 概述

本文档定义了创建智能技能的完整标准和要求。所有技能必须同时支持 **OpenAI Function Calling** 和 **MCP (Model Context Protocol)** 标准，以实现与各种AI Agent和框架的最大兼容性。

### 双标准支持

智能技能实现：
1. **OpenAI Function Calling** - 基于JSON Schema的函数定义
2. **MCP (Model Context Protocol)** - 工具、资源和提示接口
3. **独立运行** - 不依赖特定框架的自包含功能
4. **框架集成** - 可选的现有项目框架集成

---

## 1. 核心技能接口

### 1.1 基本协议

每个技能可以实现以下接口之一：

#### 独立技能接口
```python
class Skill:
    """独立技能基类 - 用于自包含的技能实现"""
    
    def execute(self, **kwargs) -> Any:
        """执行技能功能"""
        pass
```

#### 框架集成接口
```python
from typing import Protocol, Any
from .context import ExecutionContext

class FrameworkSkill(Protocol):
    """框架集成技能接口 - 用于现有项目框架集成"""
    
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """在框架上下文中执行技能"""
        pass
```

### 1.2 MCP兼容技能（推荐）

为了完整的MCP支持，扩展 `McpCompatibleSkill`：

```python
from mcp_base import McpCompatibleSkill
from typing import Dict, Any

class YourSkill(McpCompatibleSkill):
    
    @abstractmethod
    def get_openai_schema(self) -> Dict[str, Any]:
        """返回OpenAI Function Calling兼容的JSON Schema"""
        pass
    
    @abstractmethod
    def execute(self, ctx, **kwargs) -> Any:
        """使用给定参数执行技能"""
        pass
    
    # 可选：重写以支持MCP资源
    def get_mcp_resources(self) -> List[McpResource]:
        return []
    
    # 可选：重写以支持MCP提示
    def get_mcp_prompts(self) -> List[McpPrompt]:
        return []
```

---

## 2. OpenAI Function Calling JSON Schema

### 2.1 标准Schema结构

所有技能必须提供 `get_schema()` 或 `get_openai_schema()` 方法返回：

```python
{
    "type": "function",
    "function": {
        "name": "skill_name",              # 小写，下划线命名
        "description": "详细描述",           # 技能功能说明
        "parameters": {
            "type": "object",
            "properties": {
                "param_name": {
                    "type": "string|integer|boolean|object|array",
                    "description": "参数描述",
                    "default": None,        # 可选的默认值
                    "enum": [],            # 可选：允许的值
                    "minimum": 0,          # 可选：整数最小值
                    "maximum": 100         # 可选：整数最大值
                }
            },
            "required": ["required_param"]  # 必需参数列表
        }
    }
}
```

### 2.2 Schema最佳实践

#### 命名约定
- **技能名称**: `snake_case`，描述性（例如：`git_reader`、`daily_report`）
- **参数名称**: `snake_case`，清晰目的（例如：`include_uncommitted`、`snapshot_name`）

#### 描述指南
- **函数描述**: 1-3句话解释目的和功能
- **参数描述**: 清晰说明包括行为和约束
- **明确提及语言支持**（如果是AI技能）
- **清楚说明默认值**

#### 类型规范
- 使用适当的JSON Schema类型：`string`、`integer`、`boolean`、`object`、`array`
- 添加约束：`minimum`、`maximum`、`enum`、`pattern`
- 为可选参数设置合理的默认值

### 2.3 示例：完整Schema

```python
@staticmethod
def get_schema() -> Dict[str, Any]:
    """返回OpenAI Function Calling兼容的JSON Schema"""
    return {
        "type": "function",
        "function": {
            "name": "git_reader",
            "description": "提取Git仓库的提交和变更信息。纯数据提取，不进行AI处理。为其他AI驱动的技能（如git_summary）提供结构化数据。",
            "parameters": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Git用户名/邮箱，用于过滤提交。如果未提供，自动使用从仓库配置检测到的当前Git用户。",
                        "default": None
                    },
                    "include_uncommitted": {
                        "type": "boolean",
                        "description": "是否在分析结果中包含未提交的更改（暂存和未暂存的文件）。",
                        "default": True
                    }
                },
                "required": []  # 两个参数都是可选的
            }
        }
    }
```

---

## 3. 输入参数规范

### 3.1 常见参数类型

#### 路径参数
```python
"path": {
    "type": "string",
    "description": "绝对或相对的文件/目录路径",
    "default": "."  # 当前目录
}
```

#### 布尔标志
```python
"include_uncommitted": {
    "type": "boolean",
    "description": "是否包含未提交的更改",
    "default": True
}
```

#### 语言参数（AI技能）
```python
"language": {
    "type": "string",
    "description": "输出生成的语言。仅支持'Chinese'（默认，中文）或'English'。",
    "default": "Chinese",
    "enum": ["Chinese", "English"]
}
```

#### 模板参数（AI技能）
```python
"template": {
    "type": "string",
    "description": "自定义提示模板。使用{placeholder1}、{placeholder2}作为占位符。如果未提供，使用内置模板。",
    "default": None
}
```

#### 数值参数
```python
"days": {
    "type": "integer",
    "description": "要分析的天数",
    "default": 1,
    "minimum": 1,
    "maximum": 30
}
```

### 3.2 参数设计原则

1. **合理的默认值**: 每个可选参数都应有有用的默认值
2. **清晰的约束**: 使用`enum`、`minimum`、`maximum`验证输入
3. **自我说明**: 描述应解释目的、行为和默认值
4. **最少必需**: 只有绝对必要时才将参数标记为`required`

---

## 4. MCP (Model Context Protocol) 标准支持

### 4.1 MCP组件

技能可以提供三种类型的MCP组件：

#### 工具（Tools / Functions）
- 自动从OpenAI schema生成
- 代表可执行功能

#### 资源（Resources / Data Access）
- 只读数据端点
- 基于URI的寻址
- 可选的缓存支持

#### 提示（Prompts / Templates）
- 结构化的提示模板
- 可以接受参数
- 返回格式化的消息

### 4.2 MCP工具定义

工具自动从OpenAI schema转换：

```python
from ldr.mcp.base import McpTool

def get_mcp_tool(self) -> McpTool:
    """转换为MCP工具格式"""
    openai_schema = self.get_openai_schema()
    return McpTool.from_openai_schema(openai_schema)
```

结果格式：
```json
{
    "name": "skill_name",
    "description": "技能描述",
    "inputSchema": {
        "type": "object",
        "properties": {...},
        "required": [...]
    }
}
```

### 4.3 MCP资源

定义可访问的数据源：

```python
from ldr.mcp.base import McpResource

def get_mcp_resources(self) -> List[McpResource]:
    """为此技能定义MCP资源"""
    return [
        McpResource(
            uri="skill://skill_name/resource-name",
            name="resource_name",
            description="资源描述",
            mime_type="application/json",  # 或 "text/plain"、"text/html"
            annotations={
                "cached": True  # 可选：启用缓存
            }
        )
    ]
```

#### 资源URI约定

遵循这些URI模式：
- `git://repository/*` - Git仓库数据
- `git://summary/*` - Git摘要数据
- `report://daily/*` - 日报数据
- `skill://[skill_name]/*` - 技能特定资源
- `file://[path]` - 文件系统资源
- `directory://[path]` - 目录资源

#### 常见资源类型

1. **数据资源**: 当前状态数据（JSON）
2. **状态资源**: 系统/技能状态（JSON）
3. **模板资源**: 提示模板（文本）
4. **内容资源**: 生成的内容（文本/JSON）

### 4.4 MCP提示

定义提示模板：

```python
from ldr.mcp.base import McpPrompt

def get_mcp_prompts(self) -> List[McpPrompt]:
    """为此技能定义MCP提示"""
    return [
        McpPrompt(
            name="skill_name_chinese",
            description="skill_name的中文提示",
            arguments=[
                {
                    "name": "context",
                    "description": "生成的额外上下文",
                    "required": False
                }
            ]
        )
    ]
```

#### 提示命名约定
- `[skill]_chinese` - 中文提示
- `[skill]_english` - 英文提示  
- `[skill]_template` - 模板检索提示
- `[skill]_analysis` - 分析/生成提示

---

## 5. 技能类别和模式

### 5.1 数据提取技能

**目的**: 纯数据检索，不进行AI处理

**特征**:
- 无 `language` 参数
- 无 `template` 参数
- 专注于结构化数据输出
- 确定性结果

**示例**: `GitReaderSkill`、`FileSkill`、`DirectorySkill`

**Schema模式**:
```python
{
    "name": "data_reader",
    "description": "从源提取数据。纯数据提取，不进行AI处理。",
    "parameters": {
        "properties": {
            "source": {"type": "string", "description": "数据源路径"},
            "include_metadata": {"type": "boolean", "default": True}
        },
        "required": ["source"]
    }
}
```

### 5.2 AI驱动的分析技能

**目的**: 使用AI进行智能处理和生成

**特征**:
- 必须包含 `language` 参数，带 `enum: ["Chinese", "English"]`
- 应该包含 `template` 参数用于自定义
- 可能包含 `include_context` 用于历史数据
- 非确定性结果

**示例**: `GitSummarySkill`、`DailyReportSkill`

**Schema模式**:
```python
{
    "name": "ai_analyzer",
    "description": "分析数据并生成AI驱动的洞察。支持中文（默认）和英文，带内置模板。",
    "parameters": {
        "properties": {
            "data": {"type": "object", "description": "要分析的输入数据"},
            "language": {
                "type": "string",
                "description": "输出语言。仅支持'Chinese'（默认）或'English'。",
                "default": "Chinese",
                "enum": ["Chinese", "English"]
            },
            "template": {
                "type": "string",
                "description": "自定义提示模板。使用{data}、{language}作为占位符。",
                "default": None
            }
        },
        "required": ["data"]
    }
}
```

### 5.3 文件系统技能

**目的**: 文件和目录操作

**特征**:
- `path` 参数（必需）
- 可选的 `read` 或 `recurse` 标志
- 元数据提取
- 快照支持（可选）

**示例**: `FileSkill`、`DirectorySkill`

### 5.4 报告技能

**目的**: 生成综合报告

**特征**:
- 组合多个数据源
- 多语言支持
- 模板自定义
- 上下文感知
- 结构化输出（通常是JSON）

**示例**: `DailyReportSkill`

---

## 6. 实现要求

### 6.1 执行方法

所有技能必须实现：

```python
def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
    """
    使用给定参数执行技能
    
    Args:
        ctx: 用于存储和检索共享数据的执行上下文
        **kwargs: 匹配schema定义的参数
        
    Returns:
        技能特定的结果（dict、list、string等）
    """
    pass
```

### 6.2 返回值标准

#### 成功响应（数据技能）
```python
{
    "success": True,
    "function_name": "skill_name",
    "data": {
        # 结构化数据
    },
    "statistics": {
        # 汇总统计
    }
}
```

#### 成功响应（AI技能）
```python
{
    "success": True,
    "function_name": "skill_name",
    "result": "生成的内容...",
    "metadata": {
        "language": "Chinese",
        "template_used": "built-in",
        "timestamp": "2026-02-11T08:00:00Z"
    }
}
```

#### 错误响应
```python
{
    "success": False,
    "function_name": "skill_name",
    "error": {
        "message": "错误描述",
        "type": "execution_error|validation_error|file_not_found"
    }
}
```

### 6.3 上下文使用

使用ExecutionContext在技能之间共享数据：

```python
# 存储数据
ctx.set("skill:skill_name:key", value)

# 检索数据
value = ctx.get("skill:skill_name:key")

# 常见模式
ctx.set(f"skill:{skill_name}:result", result)
ctx.set(f"file:{path}", file_metadata)
ctx.set(f"git:summary", git_summary)
```

### 6.4 错误处理

```python
def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
    try:
        # 验证输入
        if not validate_params(kwargs):
            return {
                "success": False,
                "error": {"message": "参数无效", "type": "validation_error"}
            }
        
        # 执行逻辑
        result = perform_operation(**kwargs)
        
        # 存储在上下文中
        ctx.set(f"skill:{self.__class__.__name__}:result", result)
        
        return {
            "success": True,
            "function_name": "skill_name",
            "data": result
        }
        
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": {"message": str(e), "type": "file_not_found"}
        }
    except Exception as e:
        return {
            "success": False,
            "error": {"message": str(e), "type": "execution_error"}
        }
```

---

## 7. 语言支持实现

### 7.1 多语言技能

对于需要语言支持的AI驱动技能：

#### Schema定义
```python
"language": {
    "type": "string",
    "description": "输出语言。仅支持'Chinese'（默认，中文）或'English'。",
    "default": "Chinese",
    "enum": ["Chinese", "English"]
}
```

#### 内置模板
```python
TEMPLATES = {
    "Chinese": """
基于以下数据生成中文摘要：
数据：{data}
要求：{requirements}
""",
    "English": """
Generate an English summary based on the following data:
Data: {data}
Requirements: {requirements}
"""
}

def get_template(self, language: str, custom_template: str = None) -> str:
    """获取指定语言的模板"""
    if custom_template:
        return custom_template
    return TEMPLATES.get(language, TEMPLATES["Chinese"])
```

#### 模板占位符

常见占位符：
- `{language}` - 目标语言
- `{data}` - 输入数据
- `{commits}` - Git提交（用于git技能）
- `{changes}` - Git更改（用于git技能）
- `{git_summary}` - Git摘要（用于报告技能）
- `{statistics}` - 统计数据
- `{context}` - 历史上下文

### 7.2 模板内部化

**最佳实践**: 在代码中内部化模板，而不是外部文件

原因：
1. 无文件I/O开销
2. 更容易部署
3. 代码版本控制
4. 无文件丢失错误

---

## 8. MCP服务器部署标准

### 8.1 MCP兼容技能必需文件

每个MCP兼容技能项目必须包含：

#### 核心实现文件
- `{skill_name}_skill.py` - 主要技能实现
- `mcp_server.py` - MCP服务器，使用stdio传输
- `skill_compat.py` - 框架兼容层

#### 配置文件
- `mcp_config.json` - MCP客户端配置模板
- `{skill_name}_config_example.json` - 配置示例
- `claude_desktop_config.json` - Claude Desktop集成配置

#### 部署文件
- `install.sh` - 自动化安装脚本
- `requirements.txt` - Python依赖
- `.gitignore` - 安全和缓存排除

#### 文档文件
- `MCP_DEPLOYMENT.md` - 部署和集成指南
- `README.md` - 项目概述和使用说明
- `{SKILL_NAME}_USAGE.md` - 详细技能文档

### 8.2 MCP服务器模板

```python
#!/usr/bin/env python3
"""
{技能名称} MCP服务器

使用: python mcp_server.py
测试: python mcp_server.py --test
"""

import json
import sys
import asyncio
from typing import Any, Dict, List

# 导入技能（带降级处理）
try:
    from {skill_name}_skill import {SkillName}Skill
    from skill_compat import ExecutionContext
except ImportError as e:
    print(f"导入失败: {e}")
    sys.exit(1)

class {SkillName}McpServer:
    """MCP服务器 for {技能名称}"""
    
    def __init__(self):
        self.skill = {SkillName}Skill()
        self.context = ExecutionContext()
    
    def get_server_info(self) -> Dict[str, Any]:
        return {
            "name": "{skill-name}-mcp-server",
            "version": "1.0.0", 
            "description": "{技能描述} 的 MCP 服务器",
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": False
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        schema = self.skill.get_openai_schema()
        return [{
            "name": schema["function"]["name"],
            "description": schema["function"]["description"],
            "inputSchema": schema["function"]["parameters"]
        }]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name != "{skill_function_name}":
            return {"error": f"未知工具: {name}"}
        
        try:
            result = self.skill.execute(self.context, **arguments)
            if result.get("success"):
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, indent=2)
                    }]
                }
            else:
                return {
                    "error": result.get("error", {}).get("message", "未知错误")
                }
        except Exception as e:
            return {"error": f"工具执行失败: {str(e)}"}
```

### 8.3 安装脚本模板

```bash
#!/bin/bash
# {技能名称} MCP服务器安装脚本

echo "🚀 {技能名称} MCP服务器安装"
echo "=============================="

INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
echo "📁 安装目录: $INSTALL_DIR"

# 检查Python
python3 --version || {
    echo "❌ 需要Python 3"
    exit 1
}

# 安装依赖
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    pip3 install -r "$INSTALL_DIR/requirements.txt"
fi

# 测试服务器
echo "🧪 测试MCP服务器..."
cd "$INSTALL_DIR"
python3 mcp_server.py --test || {
    echo "❌ 服务器测试失败"
    exit 1
}

echo "✅ 安装完成！"
echo "📋 下一步:"
echo "1. 配置凭据: cp {skill_name}_config_example.json {skill_name}_config_local.json"
echo "2. 测试配置: python3 test_{skill_name}.py"
echo "3. 添加到AI代理的MCP设置"
```

---

## 9. 文件结构和命名

### 9.1 标准项目结构
```
{skill-name}/
├── 核心实现
│   ├── {skill_name}_skill.py          # 主要技能实现
│   ├── mcp_server.py                  # MCP协议服务器
│   └── skill_compat.py                # 框架兼容层
├── 测试和验证
│   ├── test_{skill_name}.py           # 测试脚本
│   └── test_mcp_server.py             # MCP服务器测试
├── 配置
│   ├── {skill_name}_config_example.json # 公开配置模板
│   ├── {skill_name}_config_local.json   # 私有配置（gitignored）
│   ├── mcp_config.json                  # MCP客户端配置
│   └── claude_desktop_config.json      # Claude Desktop集成
├── 部署
│   ├── install.sh                      # 安装脚本
│   ├── requirements.txt                # Python依赖
│   └── .gitignore                      # 安全排除规则
└── 文档
    ├── README.md                       # 项目概述
    ├── MCP_DEPLOYMENT.md               # MCP集成指南
    └── {SKILL_NAME}_USAGE.md           # 详细使用指南
```

### 9.2 框架无关组织

对于可能集成到现有框架（如LocalDailyReport）的技能，也支持：

```
framework/skills/
├── __init__.py
├── base.py                    # 基本技能协议
├── registry.py                # 技能注册表
├── specs/                     # 规范
│   └── skill_template.yaml    # 新技能模板
├── {skill_name}_skill.py      # 单个技能文件
└── {skill_name}/              # 可选：技能特定模块
    ├── __init__.py
    └── helpers.py
```

### 8.2 技能文件模板

文件: `{skill_name}_skill.py`

```python
"""
{Skill Name} - {简要描述}

描述:
    {技能功能的详细描述}
    
特性:
    - 特性1
    - 特性2
    
MCP支持:
    - 工具: {tool_name}
    - 资源: {count}个资源
    - 提示: {count}个提示
"""

from typing import Any, Dict, List
from ldr.mcp.base import McpCompatibleSkill, McpResource, McpPrompt
from ldr.context import ExecutionContext


class {SkillName}Skill(McpCompatibleSkill):
    """
    {Skill Name} 技能
    
    {详细描述}
    """
    
    @staticmethod
    def get_schema() -> Dict[str, Any]:
        """返回OpenAI Function Calling兼容的JSON Schema"""
        return {
            "type": "function",
            "function": {
                "name": "{skill_name}",
                "description": "{描述}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        # 参数在这里
                    },
                    "required": []
                }
            }
        }
    
    def get_openai_schema(self) -> Dict[str, Any]:
        """返回OpenAI Function Calling兼容的JSON Schema"""
        return self.get_schema()
    
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """
        执行技能
        
        Args:
            ctx: 执行上下文
            **kwargs: 技能参数
            
        Returns:
            技能结果
        """
        # 实现在这里
        pass
    
    def get_mcp_resources(self) -> List[McpResource]:
        """定义MCP资源"""
        return [
            # 资源在这里
        ]
    
    def get_mcp_prompts(self) -> List[McpPrompt]:
        """定义MCP提示"""
        return [
            # 提示在这里
        ]
```

### 8.3 命名约定

- **类名**: `{SkillName}Skill` (PascalCase + "Skill"后缀)
- **文件名**: `{skill_name}_skill.py` (snake_case + "_skill"后缀)
- **函数名**: `{skill_name}` (snake_case，匹配文件前缀)

示例：
- `GitReaderSkill` → `git_reader_skill.py` → `git_reader`
- `DailyReportSkill` → `daily_report_skill.py` → `daily_report`
- `FileSkill` → `file_skill.py` → `file`

---

## 9. 注册和发现

### 9.1 技能注册表

将新技能添加到 `ldr/skills/registry.py`：

```python
from .{skill_name}_skill import {SkillName}Skill

SKILL_REGISTRY = {
    "{skill_name}": {SkillName}Skill,
    # ... 其他技能
}
```

### 9.2 自动发现

技能由MCP服务器自动发现：

```python
from ldr.skills import registry

# 获取所有注册的技能
all_skills = registry.SKILL_REGISTRY

# 实例化技能
skill_class = all_skills["git_reader"]
skill_instance = skill_class()
```

---

## 10. 最佳实践和指南

### 10.1 通用指南

1. **单一职责**: 每个技能应该把一件事做好
2. **清晰命名**: 名称应该是描述性和明确的
3. **全面文档**: 包括文档字符串和schema描述
4. **错误处理**: 始终优雅地处理错误
5. **上下文使用**: 使用上下文在技能之间共享数据
6. **可测试性**: 编写具有清晰输入/输出的可测试代码

### 10.2 Schema设计

1. **描述性**: 描述应解释目的和行为
2. **完整**: 包括所有约束和默认值
3. **已验证**: 使用JSON Schema特性进行验证
4. **可发现**: AI应该能够仅从schema理解能力

### 10.3 MCP设计

1. **有意义的资源**: 只暴露真正有用的数据
2. **逻辑URI**: 始终遵循URI约定
3. **缓存静态数据**: 对不变的资源使用缓存
4. **有用的提示**: 提供有价值的提示模板

### 10.4 性能

1. **延迟加载**: 仅在需要时加载资源
2. **缓存**: 缓存昂贵的计算
3. **异步支持**: 考虑I/O的异步操作
4. **内存管理**: 清理大对象

### 10.5 安全

1. **路径验证**: 验证和清理文件路径
2. **输入验证**: 验证所有用户输入
3. **错误消息**: 不要泄露敏感信息
4. **资源访问**: 控制对敏感资源的访问

---

## 11. 现有技能示例

### 11.1 GitReaderSkill（数据提取）

**目的**: 提取Git仓库数据  
**类别**: 数据提取  
**MCP支持**: 工具 + 资源

```python
{
    "name": "git_reader",
    "description": "提取Git仓库的提交和变更信息。纯数据提取，不进行AI处理。",
    "parameters": {
        "properties": {
            "username": {
                "type": "string",
                "description": "Git用户名/邮箱，用于过滤提交。如果未提供，使用当前Git用户",
                "default": None
            },
            "include_uncommitted": {
                "type": "boolean",
                "description": "是否包含未提交的更改",
                "default": True
            }
        },
        "required": []
    }
}
```

**MCP资源**:
- `git://repository/commits`
- `git://repository/changes`
- `git://repository/status`

### 11.2 GitSummarySkill（AI分析）

**目的**: AI驱动的Git活动摘要  
**类别**: AI分析  
**MCP支持**: 工具 + 资源 + 提示

```python
{
    "name": "git_summary",
    "description": "分析Git仓库活动并生成AI驱动的工作摘要。支持中文（默认）和英文，带内置模板。",
    "parameters": {
        "properties": {
            "username": {"type": "string", "default": None},
            "include_uncommitted": {"type": "boolean", "default": True},
            "template": {
                "type": "string",
                "description": "自定义提示模板。使用{commits}、{changes}、{language}作为占位符。",
                "default": None
            },
            "language": {
                "type": "string",
                "description": "摘要语言。仅支持'Chinese'（默认）或'English'。",
                "default": "Chinese",
                "enum": ["Chinese", "English"]
            }
        },
        "required": []
    }
}
```

**MCP资源**:
- `git://summary/latest`
- `git://summary/template`

**MCP提示**:
- `git_summary_chinese`
- `git_summary_english`

### 11.3 FileSkill（文件系统）

**目的**: 读取文件并提取元数据  
**类别**: 文件系统  
**MCP支持**: 工具 + 资源

```python
{
    "name": "file",
    "description": "读取文件内容并提取元数据信息。",
    "parameters": {
        "properties": {
            "path": {
                "type": "string",
                "description": "绝对或相对文件路径"
            },
            "read": {
                "type": "boolean",
                "description": "是否读取文件内容",
                "default": False
            }
        },
        "required": ["path"]
    }
}
```

**MCP资源**:
- `skill://file/file-content`

---

## 12. 验证检查清单

创建新技能时使用此检查清单：

### Schema验证
- [ ] Schema有 `type: "function"` 包装器
- [ ] Function有 `name`、`description`、`parameters`
- [ ] 所有参数都有 `type` 和 `description`
- [ ] 可选参数有 `default` 值
- [ ] 必需参数列在 `required` 数组中
- [ ] 语言参数包含 `enum: ["Chinese", "English"]`（如果是AI技能）
- [ ] 模板参数解释占位符（如果是AI技能）

### 实现验证
- [ ] 类扩展 `McpCompatibleSkill`
- [ ] 实现 `get_openai_schema()` 方法
- [ ] 实现 `execute(ctx, **kwargs)` 方法
- [ ] 使用try/except进行适当的错误处理
- [ ] 返回带有 `success` 字段的结构化响应
- [ ] 使用上下文进行数据共享：`ctx.set()`、`ctx.get()`

### MCP验证
- [ ] 资源遵循URI约定
- [ ] 资源描述清晰
- [ ] 提示遵循命名约定
- [ ] 如果定义了资源，实现 `read_resource()`
- [ ] 如果定义了提示，实现 `get_prompt()`

### 文件结构验证
- [ ] 文件命名为 `{skill_name}_skill.py`
- [ ] 类命名为 `{SkillName}Skill`
- [ ] 函数命名为 `{skill_name}`
- [ ] 添加到 `registry.py`
- [ ] 全面的文档字符串

### 测试验证
- [ ] Schema验证测试
- [ ] 使用有效输入的执行测试
- [ ] 错误处理测试
- [ ] MCP兼容性测试

---

## 13. 常见问题排查

### 问题：Schema未被识别

**问题**: AI代理找不到或解析技能schema  
**解决方案**: 
- 验证 `get_schema()` 或 `get_openai_schema()` 方法存在
- 确保返回值匹配OpenAI Function Calling格式
- 检查schema字典中的语法错误

### 问题：参数验证失败

**问题**: 技能接收到意外的参数值  
**解决方案**:
- 在 `execute()` 方法中添加输入验证
- 使用JSON Schema约束：`minimum`、`maximum`、`enum`
- 提供清晰的错误消息

### 问题：MCP资源不可用

**问题**: 无法通过MCP访问资源  
**解决方案**:
- 验证 `get_mcp_resources()` 返回 `McpResource` 对象列表
- 实现 `read_resource()` 方法
- 检查URI格式是否符合约定

### 问题：语言支持不工作

**问题**: AI生成的内容语言错误  
**解决方案**:
- 确保 `language` 参数有 `enum: ["Chinese", "English"]`
- 实现特定语言的模板
- 正确传递语言参数给AI客户端

---

## 14. 迁移指南

### 从简单技能到MCP兼容技能

**步骤1**: 添加MCP基类
```python
# 之前
class MySkill:
    pass

# 之后
from ldr.mcp.base import McpCompatibleSkill

class MySkill(McpCompatibleSkill):
    pass
```

**步骤2**: 重命名schema方法（如果需要）
```python
# 之前
@staticmethod
def get_schema():
    ...

# 之后
def get_openai_schema(self):
    return self.get_schema()  # 仍然可以使用静态方法
```

**步骤3**: 添加MCP资源（可选）
```python
def get_mcp_resources(self):
    return [
        McpResource(
            uri="skill://my_skill/data",
            name="my_skill_data",
            description="我的技能数据"
        )
    ]
```

**步骤4**: 添加MCP提示（可选，用于AI技能）
```python
def get_mcp_prompts(self):
    return [
        McpPrompt(
            name="my_skill_prompt",
            description="我的技能提示"
        )
    ]
```

---

## 15. Schema导出和MCP服务器

### 15.1 Schema导出

所有技能可以导出到 `mcp_schema_export.json`：

```python
# 从单个技能生成schema导出
python -c "from {skill_name}_skill import {SkillName}Skill; skill = {SkillName}Skill(); import json; print(json.dumps(skill.get_openai_schema(), indent=2))"
```

### 15.2 MCP服务器集成

技能通过专用MCP服务器可用：

```bash
# 启动单个技能MCP服务器
python mcp_server.py

# 测试MCP服务器功能
python mcp_server.py --test
```

### 15.3 MCP客户端集成

```python
from {skill_name}_skill import {SkillName}McpServer

server = {SkillName}McpServer()

# 列出所有工具
tools = server.list_tools()

# 调用工具
result = server.call_tool("{skill_function_name}", {"param1": "value1"})

# 读取资源
data = server.read_resource("skill://resource/data")
```

---

## 16. 部署考虑

### 16.1 独立技能执行

技能可以独立执行：

```python
from ldr.skills.git_reader_skill import GitReaderSkill
from ldr.context import ExecutionContext

skill = GitReaderSkill()
ctx = ExecutionContext()
result = skill.execute(ctx, path=".", days=1)
```

### 16.2 工作流集成

技能在YAML工作流中使用：

```yaml
name: my_workflow
steps:
  - name: read_git
    skill: git_reader
    params:
      include_uncommitted: true
  
  - name: generate_summary
    skill: git_summary
    params:
      language: Chinese
```

### 16.3 MCP服务器部署

技能通过MCP服务器暴露：

```bash
# Docker部署
docker run -p 8001:8001 local-daily-report python start_mcp_server.py

# Systemd服务
systemctl start local-daily-report-mcp
```

---

## 附录A：完整技能模板

请参阅 `ldr/skills/specs/skill_template.yaml` 获取基本模板。

完整实现模板请参考英文版文档中的详细示例。

---

## 附录B：JSON Schema参考

JSON Schema类型和约束的快速参考：

### 基本类型
- `string` - 文本数据
- `integer` - 整数
- `number` - 小数
- `boolean` - true/false
- `object` - JSON对象
- `array` - JSON数组
- `null` - 空值

### 字符串约束
- `minLength` - 最小字符串长度
- `maxLength` - 最大字符串长度
- `pattern` - 正则表达式模式
- `format` - 格式类型（email、uri、date-time等）
- `enum` - 允许的值

### 数字约束
- `minimum` - 最小值（包含）
- `maximum` - 最大值（包含）
- `exclusiveMinimum` - 最小值（不包含）
- `exclusiveMaximum` - 最大值（不包含）
- `multipleOf` - 值必须是此数的倍数

---

## 附录C：参考资料

### 官方文档
- OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling
- JSON Schema: https://json-schema.org/
- Model Context Protocol: https://modelcontextprotocol.io/

### AI智能应用文档
- 主README: `/README.md`
- MCP集成指南: `/MCP_DEPLOYMENT.md`
- 安装指南: `/install.sh`
- 使用文档: `/{SKILL_NAME}_USAGE.md`

### 示例实现
- Gmail检查技能: `/gmail_check_skill.py`
- MCP服务器模板: `/mcp_server.py`
- 配置管理: `/skill_compat.py`
- 测试框架: `/test_gmail_skill.py`

---

## 文档结束

本文档旨在供AI系统阅读和理解，用于自动化技能生成。提供了所有标准、约定和示例，以确保一致、高质量的技能开发，支持多种AI代理平台。

有关问题或说明，请参考示例实现或MCP部署文档。

**最后更新**: 2026-02-11  
**文档版本**: 2.0.0  
**目标应用**: AI智能技能和代理
