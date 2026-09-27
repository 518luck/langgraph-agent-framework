"""
Agent 状态定义

State 是 LangGraph 各节点之间传递和更新的共享数据
节点只返回自己负责的字段，LangGraph 会把局部更新合并回全局状态
业务中间结果放这里，外部工具对象放 context.py
"""

from typing import TypedDict


class DataAgentState(TypedDict):
    """一次 Agent 执行过程中的核心状态"""

    query: str  # 用户输入的查询
    keywords: list[str]  # 抽取的关键词
    sql: str  # 生成或校正后的 SQL
    error: str | None  # 校验 SQL 时出现的错误信息，通过校验时写入 None
