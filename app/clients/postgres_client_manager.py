# PostgreSQL 客户端管理器：创建、复用与关闭异步 Engine 与 Session 工厂。

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.conf.app_config import DBConfig, app_config


class PostgresClientManager:
    def __init__(self, config: DBConfig):
        # 保存数据库配置，后面拼接连接地址要用
        self.config = config
        # Engine 是数据库连接层核心对象，底层会维护连接池
        self._engine: AsyncEngine | None = None
        # session_factory 用来按需创建新的 AsyncSession
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine:
        # 断言让类型检查器收窄掉 None，同时把“忘记调用 init()”变成明确的报错
        assert self._engine is not None, "PostgreSQL Engine 尚未初始化，请先调用 init()"
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        assert self._session_factory is not None, (
            "PostgreSQL Session 工厂尚未初始化，请先调用 init()"
        )
        return self._session_factory

    def _get_url(self):
        # postgresql+asyncpg 表示：连接 PostgreSQL，并使用 asyncpg 作为异步驱动
        return f"postgresql+asyncpg://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}"

    def init(self):
        # 创建异步 Engine，相当于先把“数据库连接能力”准备好
        self._engine = create_async_engine(
            self._get_url(), pool_size=10, pool_pre_ping=True
        )
        # 基于 Engine 创建 Session 工厂，后面真正查库时再拿 session
        self._session_factory = async_sessionmaker(
            self._engine, autoflush=True, expire_on_commit=False
        )

    async def close(self):
        # 程序结束时释放连接池资源；没初始化过就什么都不做，允许重复调用
        if self._engine is not None:
            await self._engine.dispose()


# 全局单例。需要连第二套库时，照这行再加一个 manager，
# 并在 app/api/lifespan.py 里成对补 init() 与 close()
postgres_client_manager = PostgresClientManager(app_config.db)


if __name__ == "__main__":
    # 最小验证：连一下库，跑一条不依赖任何表的查询
    postgres_client_manager.init()

    async def test():
        async with postgres_client_manager.session_factory() as session:
            result = await session.execute(text("select 1"))
            print("连接正常，select 1 =", result.scalar())

    asyncio.run(test())
