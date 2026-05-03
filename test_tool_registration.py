"""
测试qwen-agent工具注册
"""

from qwen_agent.tools import BaseTool


# 方法1: 使用BaseTool类
class ExcSqlTool(BaseTool):
    @property
    def name(self):
        return 'ExcSql'
    
    @property
    def description(self):
        return '执行SQL查询,支持自然语言描述'
    
    @property
    def parameters(self):
        return {
            'type': 'object',
            'properties': {
                'query_description': {
                    'type': 'string',
                    'description': '自然语言描述的查询需求'
                }
            },
            'required': ['query_description']
        }
    
    def call(self, params: str, **kwargs) -> str:
        """执行SQL查询"""
        query_description = params.get('query_description', '') if isinstance(params, dict) else params
        return f"SQL查询结果: {query_description}"


# 测试
if __name__ == '__main__':
    tool = ExcSqlTool()
    print(f"工具名称: {tool.name}")
    print(f"工具描述: {tool.description}")
    print(f"工具参数: {tool.parameters}")
    result = tool.call({'query_description': '测试查询'})
    print(f"执行结果: {result}")
