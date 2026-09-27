"""
示例节点

照这个外壳写自己的节点，写完删掉本文件，并在 graph.py 里换成你的节点
三段进度（running / success / error）与最后的 raise 是硬约定，详见同目录的 AGENTS.md
"""

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def example(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """示例节点：读 state、用 runtime.context、写进度、返回局部更新"""

    writer = runtime.stream_writer
    step = "示例步骤"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        # 1. 读 state：query = state["query"]
        # 2. 取依赖：repo = runtime.context["xxx_repository"]
        # 3. 干活：调模型（from app.agent.llm import llm）、查库、做计算
        logger.info(f"示例节点收到问题：{state['query']}")

        writer({"type": "progress", "step": step, "status": "success"})
        # 4. 只返回本节点负责的字段，LangGraph 会合并回全局 state
        return {}
    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise
