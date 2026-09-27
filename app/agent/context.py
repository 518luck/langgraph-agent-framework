"""
Agent 运行时上下文

存放节点执行时需要的外部依赖（仓储、客户端等），由接口层组装后注入
只声明字段不实例化：节点只关心“我能拿到什么”，不关心“对象从哪来”
字段名即节点里 runtime.context[...] 的键名
"""

from typing import TypedDict

from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository


class DataAgentContext(TypedDict):
    """LangGraph Runtime 中传递的上下文对象"""

    # 数仓仓储：SQL 校验与执行都面向它
    dw_mysql_repository: DWMySQLRepository
