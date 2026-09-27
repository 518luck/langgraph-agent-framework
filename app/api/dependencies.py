"""
FastAPI 依赖组装

集中声明 API 层需要的依赖函数，把 Session、Repository、Client 和 Service
按职责组装起来。路由层只通过 Depends 声明自己需要什么对象，具体创建细节
都收敛在这里，避免 HTTP 处理函数直接感知底层基础设施。

新增依赖时：这里补一个 get_xxx，再在 get_query_service 的参数里注入
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.mysql_client_manager import dw_mysql_client_manager
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.services.query_service import QueryService


async def get_dw_session():
    """创建一次请求内使用的数仓 Session"""

    # yield 之后的清理逻辑由 async with 负责，FastAPI 会在请求结束后继续执行退出流程
    async with dw_mysql_client_manager.session_factory() as dw_session:
        yield dw_session


async def get_dw_mysql_repository(
    session: Annotated[AsyncSession, Depends(get_dw_session)],
) -> DWMySQLRepository:
    """基于请求级 Session 创建数仓仓储"""

    return DWMySQLRepository(session)


async def get_query_service(
    dw_mysql_repository: Annotated[
        DWMySQLRepository, Depends(get_dw_mysql_repository)
    ],
) -> QueryService:
    """组装一次查询所需的业务服务"""

    return QueryService(dw_mysql_repository=dw_mysql_repository)
