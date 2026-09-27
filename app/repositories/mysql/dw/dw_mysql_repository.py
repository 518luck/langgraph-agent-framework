"""
数仓 MySQL 仓储

负责到真实数仓里执行与校验 SQL，并读取数据库环境信息
业务节点不直接写 SQL 字符串之外的东西：连接的获取与释放由接口层通过依赖注入完成
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DWMySQLRepository:
    """负责在数仓上校验、执行 SQL，并读取数据库环境信息"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_db_info(self) -> dict[str, str]:
        """读取当前数据库的方言和版本，供提示词描述数据库环境"""

        # 结果只有一行一列，scalar() 比 fetchall()[0][0] 直观
        result = await self.session.execute(text("select version()"))
        version = result.scalar()

        # dialect 来自 SQLAlchemy 当前绑定的数据库方言，例如 mysql
        dialect = self.session.bind.dialect.name
        return {"dialect": dialect, "version": version}

    async def validate(self, sql: str):
        """用 EXPLAIN 让数据库提前解析 SQL，发现语法 表名 字段名等错误"""

        sql = f"explain {sql}"
        await self.session.execute(text(sql))

    async def run(self, sql: str) -> list[dict]:
        """执行最终 SQL，并把 SQLAlchemy 行对象转换成前端更易消费的字典列表"""

        result = await self.session.execute(text(sql))
        return [dict(row) for row in result.mappings().fetchall()]
