"""
框架兼容模块

为了使Gmail Check Skill能够独立运行，提供必要的基础类和接口
"""

from typing import Protocol, Any, Dict, List
from abc import ABC, abstractmethod
import json


class ExecutionContext:
    """执行上下文，用于在技能之间共享数据"""
    
    def __init__(self):
        self._data = {}
    
    def set(self, key: str, value: Any):
        """设置数据"""
        self._data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取数据"""
        return self._data.get(key, default)
    
    def has(self, key: str) -> bool:
        """检查是否存在数据"""
        return key in self._data
    
    def remove(self, key: str) -> bool:
        """删除数据"""
        if key in self._data:
            del self._data[key]
            return True
        return False
    
    def clear(self):
        """清空所有数据"""
        self._data.clear()
    
    def keys(self) -> List[str]:
        """获取所有键"""
        return list(self._data.keys())


class Skill(Protocol):
    """技能接口，所有技能必须实现execute方法"""
    
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """执行技能"""
        ...


class McpResource:
    """MCP资源定义"""
    
    def __init__(self, uri: str, name: str, description: str, 
                 mime_type: str = "application/json", annotations: Dict = None):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type
        self.annotations = annotations or {}


class McpPrompt:
    """MCP提示定义"""
    
    def __init__(self, name: str, description: str, arguments: List[Dict] = None):
        self.name = name
        self.description = description
        self.arguments = arguments or []


class McpTool:
    """MCP工具定义"""
    
    def __init__(self, name: str, description: str, input_schema: Dict):
        self.name = name
        self.description = description
        self.input_schema = input_schema
    
    @classmethod
    def from_openai_schema(cls, openai_schema: Dict) -> 'McpTool':
        """从OpenAI Schema转换为MCP Tool"""
        function_def = openai_schema.get('function', {})
        return cls(
            name=function_def.get('name', ''),
            description=function_def.get('description', ''),
            input_schema=function_def.get('parameters', {})
        )


class McpCompatibleSkill(ABC):
    """MCP兼容技能基类"""
    
    @abstractmethod
    def get_openai_schema(self) -> Dict[str, Any]:
        """返回OpenAI Function Calling兼容的JSON Schema"""
        pass
    
    @abstractmethod
    def execute(self, ctx: ExecutionContext, **kwargs) -> Any:
        """执行技能"""
        pass
    
    def get_mcp_resources(self) -> List[McpResource]:
        """获取MCP资源列表"""
        return []
    
    def get_mcp_prompts(self) -> List[McpPrompt]:
        """获取MCP提示列表"""
        return []
    
    def get_mcp_tool(self) -> McpTool:
        """获取MCP工具定义"""
        return McpTool.from_openai_schema(self.get_openai_schema())
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """读取MCP资源"""
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": f"Resource {uri} not found"
                }
            ]
        }
    
    def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取MCP提示"""
        return {
            "description": f"Prompt {name} not found",
            "messages": []
        }