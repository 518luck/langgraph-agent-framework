"""
Agent 状态定义

State 是 LangGraph 各节点之间传递和更新的共享数据
节点只返回自己负责的那部分字段，LangGraph 会把局部更新合并回全局状态

业务中间结果放这里，外部工具对象放 context.py
"""

from typing import TypedDict


class DataAgentState(TypedDict):
    """一次 Agent 执行过程中的核心状态"""

    query: str  # 用户输入的查询

    # 按需补充：节点之间要流转的中间结果都加在这里，并在入口处一并置空值
    # 例如：keywords: list[str]、table_infos: list[TableInfoState]、error: str | None
