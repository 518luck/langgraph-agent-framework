"""
FastAPI 依赖组装

集中声明 API 层需要的依赖函数，把 Session、Repository、Client 和 Service
按职责组装起来。路由层只通过 Depends 声明自己需要什么对象，具体创建细节
都收敛在这里，避免 HTTP 处理函数直接感知底层基础设施。

新增依赖时：这里补一个 get_xxx，再在 get_query_service 的参数里注入；
同时在 app/agent/context.py 里加上同名字段，节点才取得到
"""



from app.clients.mysql_client_manager import mysql_client_manager
from app.services.query_service import QueryService


async def get_session():
    """创建一次请求内使用的数据库 Session"""

    # yield 之后的清理逻辑由 async with 负责，FastAPI 会在请求结束后继续执行退出流程
    async with mysql_client_manager.session_factory() as session:
        yield session


async def get_query_service() -> QueryService:
    """组装一次执行所需的业务服务

    需要给服务注入依赖时，按下面两行的写法加参数（类型 + Depends）：

        session: Annotated[AsyncSession, Depends(get_session)],

    当前示例节点不依赖外部资源，所以没有要注入的对象
    """
    return QueryService()
