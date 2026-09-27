"""
查询服务

把 API 层传入的自然语言问题转换成一次 LangGraph 工作流执行：
创建初始 State、组装 Runtime Context、消费 graph.astream 的流式输出，
并统一包装成 SSE 文本返回给路由层。

这里也是 API 层的最后兜底：节点负责告诉前端“哪一步失败”，
本服务负责告诉前端“失败原因是什么”
"""

import json

from app.agent.context import DataAgentContext
from app.agent.graph import graph
from app.agent.state import DataAgentState
from app.core.log import logger


class QueryService:
    """封装一次执行所需的业务编排逻辑

    需要依赖时在 __init__ 里接收，由 app/api/dependencies.py 注入
    """

    def __init__(self):
        pass

    async def query(self, query: str):
        """执行一次工作流，并逐段产出 SSE 消息"""

        # State 只放会被图节点读写和合并的业务数据；节点会写入的字段在入口处一并置空值
        state = DataAgentState(query=query)

        # Context 保存本次图执行需要复用的外部依赖，节点通过 runtime.context 读取
        # 有依赖时在这里塞进去，例如 DataAgentContext(mysql_repository=self.mysql_repository)
        context = DataAgentContext()

        try:
            # stream_mode="custom" 对应节点内部 writer(...) 写出的进度消息
            async for chunk in graph.astream(
                input=state, context=context, stream_mode="custom"
            ):
                # SSE 要求每条消息以 data: 开头，并以两个换行符结束
                # ensure_ascii=False 保留中文，default=str 兜底处理 Decimal、日期等类型
                yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n"
        # ! 流式边界：响应头已经发出，无法再改状态码，所以任何异常都必须转成 error 事件
        except Exception as e:  # noqa: BLE001
            logger.exception("Agent 执行失败")
            error = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error, ensure_ascii=False, default=str)}\n\n"
