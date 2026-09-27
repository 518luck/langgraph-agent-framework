"""
生成 SQL 节点

把用户问题和关键词交给大模型，生成一条候选 SQL 并写回 state["sql"]
只负责生成，不负责校验和执行
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


async def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """根据用户问题和关键词生成候选 SQL"""

    writer = runtime.stream_writer
    step = "生成SQL"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        query = state["query"]
        keywords = state["keywords"]

        prompt = PromptTemplate(
            template=load_prompt("generate_sql"),
            input_variables=["query", "keywords"],
        )
        # 生成 SQL 只需要一段纯文本，所以这里使用 StrOutputParser
        chain = prompt | llm | StrOutputParser()

        result = await chain.ainvoke({"query": query, "keywords": "、".join(keywords)})

        logger.info(f"生成的SQL：{result}")
        writer({"type": "progress", "step": step, "status": "success"})
        return {"sql": result}
    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise
