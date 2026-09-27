"""
查询接口的请求体结构

集中声明 /api/query 接收的数据形状，字段类型由 FastAPI 直接做请求校验
"""

from pydantic import BaseModel


class QuerySchema(BaseModel):
    """声明 /api/query 请求体里的字段形状"""

    # 前端请求体中的 query 字段，用来承载用户输入的自然语言问题
    query: str
