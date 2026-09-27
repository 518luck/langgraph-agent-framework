import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.conf.app_config import DBConfig, app_config


class MySQLClientManager:
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
        assert self._engine is not None, "MySQL Engine 尚未初始化，请先调用 init()"
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        assert self._session_factory is not None, (
            "MySQL Session 工厂尚未初始化，请先调用 init()"
        )
        return self._session_factory

    def _get_url(self):
        # mysql+asyncmy 表示：连接 MySQL，并使用 asyncmy 作为异步驱动
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?charset=utf8mb4"

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


# 一套连元数据库，一套连数仓模拟库
meta_mysql_client_manager = MySQLClientManager(app_config.db_meta)
dw_mysql_client_manager = MySQLClientManager(app_config.db_dw)

if __name__ == "__main__":
    # 这里演示的是数仓库查询，所以先初始化 dw 这一套客户端
    dw_mysql_client_manager.init()

    async def test():
        # 通过 session_factory 创建一次数据库会话
        async with dw_mysql_client_manager.session_factory() as session:
            sql = "select * from fact_order limit 10"
            # text(sql) 表示把原生 SQL 语句交给 SQLAlchemy 执行
            result = await session.execute(text(sql))

            # mappings().fetchall() 会把结果转成“按列名访问”的行对象列表
            rows = result.mappings().fetchall()

            # 下面三行只是为了帮助观察返回结果的结构
            print(type(rows))
            print(type(rows[0]))
            print(rows[0]["order_id"])

    asyncio.run(test())
