"""
Agent 图编排

使用 LangGraph 把各节点串成一条可观测的执行链路
当前只有 START -> example -> END，换成自己的流程时改三处：
注册哪些节点、怎么连边、条件边怎么判断

看图：uv run python -c "from app.agent.graph import graph; print(graph.get_graph().draw_mermaid())"
"""

import asyncio

from langgraph.constants import END, START
from langgraph.graph import StateGraph

from app.agent.context import DataAgentContext
from app.agent.nodes.example import example
from app.agent.state import DataAgentState

# 图构建器：声明共享状态与运行时上下文的 Schema，节点签名和调用方据此做类型检查
graph_builder = StateGraph(
    state_schema=DataAgentState,
    context_schema=DataAgentContext,
)

# 注册节点：名称与函数名保持一致，便于连边、看日志和看流程图
graph_builder.add_node("example", example)

# 普通边表示固定顺序。两种进阶写法：
#   并行：同一个源节点挂多条出边，多路都完成后才进汇合节点
#   分支：add_conditional_edges(source="x", path=函数, path_map={...})
graph_builder.add_edge(START, "example")
graph_builder.add_edge("example", END)

graph = graph_builder.compile()


async def demo():
    """本地调试入口：不起服务直接跑一次图，把每段进度打印到终端"""

    state = DataAgentState(query="你好")

    # 有依赖时在这里注入，例如 {"mysql_repository": MySQLRepository(...)}
    context = DataAgentContext()

    # stream_mode="custom" 接收各节点通过 runtime.stream_writer 写出的进度
    async for chunk in graph.astream(input=state, context=context, stream_mode="custom"):
        print(chunk)


if __name__ == "__main__":
    asyncio.run(demo())
