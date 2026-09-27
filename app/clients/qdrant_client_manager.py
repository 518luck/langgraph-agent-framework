# Qdrant 客户端管理器：创建并复用指向本机 Qdrant 的异步客户端。

import asyncio
import random

from qdrant_client import AsyncQdrantClient, models

from app.conf.app_config import QdrantConfig, app_config


class QdrantClientManager:
    """Qdrant 异步客户端的创建、复用与关闭。"""

    def __init__(self, qdrant_config: QdrantConfig):
        self.qdrant_config = qdrant_config
        # 客户端在 init() 中创建，构造阶段不建立外部连接
        self._client: AsyncQdrantClient | None = None

    @property
    def client(self) -> AsyncQdrantClient:
        """已初始化的客户端；未调用 init() 时报错。"""
        assert self._client is not None, "Qdrant 客户端尚未初始化，请先调用 init()"
        return self._client

    def _get_url(self):
        """拼出 Qdrant 服务地址。"""
        return f"http://{self.qdrant_config.host}:{self.qdrant_config.port}"

    def init(self):
        """创建异步客户端，在应用启动阶段调用。"""
        self._client = AsyncQdrantClient(url=self._get_url())

    async def close(self):
        """关闭客户端；未初始化时什么都不做，可重复调用。"""
        if self._client is not None:
            await self._client.close()


# 全局单例，供其他模块复用同一套客户端
qdrant_client_manager = QdrantClientManager(app_config.qdrant)


if __name__ == "__main__":
    qdrant_client_manager.init()

    async def test():
        """最小验证：建集合、写入 100 个随机点、做一次相似度检索。"""
        client = qdrant_client_manager.client

        # 集合不存在才创建，避免重复运行时冲突
        if not await client.collection_exists("my_collection"):
            await client.create_collection(
                collection_name="my_collection",
                # 10 维 + 余弦距离；演示用，真实项目维度需与 embedding 模型一致
                vectors_config=models.VectorParams(
                    size=10,
                    distance=models.Distance.COSINE,
                ),
            )

        await client.upsert(
            collection_name="my_collection",
            points=[
                models.PointStruct(
                    id=i,
                    vector=[random.random() for _ in range(10)],
                )
                for i in range(100)
            ],
        )

        # top-10，只保留分数不低于 0.8 的结果
        res = await client.query_points(
            collection_name="my_collection",
            query=[random.random() for _ in range(10)],  # type: ignore
            limit=10,
            score_threshold=0.8,
        )
        print(res)

    asyncio.run(test())
