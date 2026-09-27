"""
Agent 图编排

使用 LangGraph 把各节点串成一条可观测的执行链路
示例链路：抽取关键词 -> 生成 SQL -> 校验 SQL -> 执行（校验失败则先校正再执行）

换成自己的领域时，只需要改三处：注册哪些节点、怎么连边、条件边怎么判断
"""

import asyncio

from langgraph.constants import END, START
from langgraph.graph import StateGraph

from app.agent.context import DataAgentContext
from app.agent.nodes.correct_sql import correct_sql
from app.agent.nodes.extract_keywords import extract_keywords
from app.agent.nodes.generate_sql import generate_sql
from app.agent.nodes.run_sql import run_sql
from app.agent.nodes.validate_sql import validate_sql
from app.agent.state import DataAgentState
from app.clients.mysql_client_manager import dw_mysql_client_manager
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository

# 图构建器：声明共享状态与运行时上下文的 Schema，节点签名和调用方据此做类型检查
graph_builder = StateGraph(
    state_schema=DataAgentState,
    context_schema=DataAgentContext,
)

# 注册节点：名称与函数名保持一致，便于连边、看日志和看流程图
graph_builder.add_node("extract_keywords", extract_keywords)
graph_builder.add_node("generate_sql", generate_sql)
graph_builder.add_node("validate_sql", validate_sql)
graph_builder.add_node("correct_sql", correct_sql)
graph_builder.add_node("run_sql", run_sql)

graph_builder.add_edge(START, "extract_keywords")
graph_builder.add_edge("extract_keywords", "generate_sql")
graph_builder.add_edge("generate_sql", "validate_sql")


def route_after_validate(state: DataAgentState) -> str:
    """校验无错误则执行 SQL，有错误则先校正"""

    return "run_sql" if state["error"] is None else "correct_sql"


# 条件边：validate_sql 之后不是固定流转，按校验结果二选一
graph_builder.add_conditional_edges(
    source="validate_sql",
    path=route_after_validate,
    path_map={"run_sql": "run_sql", "correct_sql": "correct_sql"},
)
graph_builder.add_edge("correct_sql", "run_sql")
graph_builder.add_edge("run_sql", END)

graph = graph_builder.compile()


async def demo():
    """本地调试入口：不起服务直接跑一次图，把每段进度打印到终端"""

    dw_mysql_client_manager.init()

    # 入口处把节点会写入的字段先置为空值，后续节点逐步覆盖
    state = DataAgentState(query="统计华北地区的销售总额", keywords=[], sql="", error=None)

    async with dw_mysql_client_manager.session_factory() as dw_session:
        context: DataAgentContext = {"dw_mysql_repository": DWMySQLRepository(dw_session)}

        # stream_mode="custom" 接收各节点通过 runtime.stream_writer 写出的进度
        async for chunk in graph.astream(
            input=state, context=context, stream_mode="custom"
        ):
            print(chunk)

    await dw_mysql_client_manager.close()


if __name__ == "__main__":
    asyncio.run(demo())
