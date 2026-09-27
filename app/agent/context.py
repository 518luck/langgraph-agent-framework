"""
Agent 运行时上下文

存放节点执行时需要的外部依赖（仓储、客户端等），由接口层组装后注入
只声明字段不实例化：节点只关心“我能拿到什么”，不关心“对象从哪来”

字段名即节点里 runtime.context[...] 的键名，必须与 app/api/dependencies.py
里注入的字段名一致
"""

from typing import TypedDict


class DataAgentContext(TypedDict):
    """LangGraph Runtime 中传递的上下文对象"""

    # 按需补充。示例：
    #   postgres_repository: PostgresRepository
    #   embedding_client: Embeddings
