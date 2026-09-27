# ES 客户端管理器：创建并复用指向本机 Elasticsearch 的异步客户端。

import asyncio

from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class ESClientManager:
    """Elasticsearch 异步客户端的创建、复用与关闭。"""

    def __init__(self, es_config: ESConfig):
        self.es_config = es_config
        # 客户端在 init() 中创建，构造阶段不建立外部连接
        self._client: AsyncElasticsearch | None = None

    @property
    def client(self) -> AsyncElasticsearch:
        """已初始化的客户端；未调用 init() 时报错。"""
        assert self._client is not None, "ES 客户端尚未初始化，请先调用 init()"
        return self._client

    def _get_url(self):
        """拼出 ES 服务地址。"""
        return f"http://{self.es_config.host}:{self.es_config.port}"

    def init(self):
        """创建异步 ES 客户端，在应用启动阶段调用。"""
        # hosts 用列表以兼容多节点集群，单机开发只放一个
        self._client = AsyncElasticsearch(hosts=[self._get_url()])

    async def close(self):
        """关闭客户端；未初始化时什么都不做，可重复调用。"""
        if self._client is not None:
            await self._client.close()


# 全局单例，供其他模块复用同一套客户端
es_client_manager = ESClientManager(app_config.es)


if __name__ == "__main__":
    es_client_manager.init()

    async def test():
        """最小验证：建索引、批量写入 5 本书、按书名做一次全文检索。"""
        client = es_client_manager.client

        # ! ES 不允许创建同名索引；这里先删后建，仅适用于示例或测试环境
        if await client.indices.exists(index="my-books"):
            await client.indices.delete(index="my-books")

        # dynamic=False：关闭动态映射，写入字段必须符合下面的定义
        await client.indices.create(
            index="my-books",
            mappings={
                "dynamic": False,
                "properties": {
                    # text 会分词，适合全文检索
                    "name": {"type": "text"},
                    "author": {"type": "text"},
                    "release_date": {"type": "date", "format": "yyyy-MM-dd"},
                    "page_count": {"type": "integer"},
                },
            },
        )

        # operations 是“动作行 + 数据行”成对交替的格式
        # ! refresh=True 才能写完立即可搜；不加要等约 1 秒刷新，紧接着的查询可能是 0 条
        await client.bulk(
            operations=[
                {"index": {"_index": "my-books"}},
                {
                    "name": "Revelation Space",
                    "author": "Alastair Reynolds",
                    "release_date": "2000-03-15",
                    "page_count": 585,
                },
                {"index": {"_index": "my-books"}},
                {
                    "name": "1984",
                    "author": "George Orwell",
                    "release_date": "1985-06-01",
                    "page_count": 328,
                },
                {"index": {"_index": "my-books"}},
                {
                    "name": "Fahrenheit 451",
                    "author": "Ray Bradbury",
                    "release_date": "1953-10-15",
                    "page_count": 227,
                },
                {"index": {"_index": "my-books"}},
                {
                    "name": "Brave New World",
                    "author": "Aldous Huxley",
                    "release_date": "1932-06-01",
                    "page_count": 268,
                },
                {"index": {"_index": "my-books"}},
                {
                    "name": "The Handmaids Tale",
                    "author": "Margaret Atwood",
                    "release_date": "1985-06-01",
                    "page_count": 311,
                },
            ],
            refresh=True,
        )

        # match 会先用字段的分词规则处理 "brave"，因此能命中 "Brave New World"
        resp = await client.search(
            index="my-books",
            query={"match": {"name": "brave"}},
        )

        # 关注 hits.total.value 与 hits.hits[]._source
        print(resp)

        await es_client_manager.close()

    asyncio.run(test())
