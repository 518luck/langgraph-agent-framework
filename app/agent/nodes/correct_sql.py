"""
SQL 修正节点

在 SQL 校验失败后，结合原问题、原 SQL 与数据库报错做最小必要修正
只有 validate_sql 写入错误信息时，LangGraph 才会进入这个分支
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


async def correct_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """根据校验错误修正 SQL"""

    writer = runtime.stream_writer
    step = "校正SQL"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        # 原问题一起带上：避免模型只根据报错修语法却改丢业务语义
        query = state["query"]
        # sql 是待修正的候选 SQL，error 是数据库 explain 返回的具体错误信息
        sql = state["sql"]
        error = state["error"]

        prompt = PromptTemplate(
            template=load_prompt("correct_sql"),
            input_variables=["query", "sql", "error"],
        )
        # 修正后的输出仍然是一条纯 SQL 文本，用来覆盖 state["sql"]
        chain = prompt | llm | StrOutputParser()

        result = await chain.ainvoke({"query": query, "sql": sql, "error": error})

        logger.info(f"校正后的SQL：{result}")
        writer({"type": "progress", "step": step, "status": "success"})
        return {"sql": result}
    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise
