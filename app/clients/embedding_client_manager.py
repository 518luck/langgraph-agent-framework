# Embedding 客户端管理器：创建并复用指向本机 TEI 的 embedding 客户端。

import asyncio
from typing import Required, TypedDict, Unpack

from langchain.embeddings import init_embeddings
from langchain_core.embeddings import Embeddings
from pydantic import SecretStr

from app.conf.app_config import EmbeddingConfig, app_config


class EmbeddingInitKwargs(TypedDict, total=False):
    """init_embeddings 的参数表：补上库签名里 **kwargs: Any 丢掉的类型信息。"""

    # ! 键名需与 langchain-openai 的 OpenAIEmbeddings 一致，升级依赖后复核
    base_url: str
    api_key: SecretStr
    # ! 必须传 False：True 会先把文本编成 token ID 再发送，TEI 不认且不报错，只返回错误的向量
    check_embedding_ctx_length: Required[bool]


def build_embeddings(model: str, **kwargs: Unpack[EmbeddingInitKwargs]) -> Embeddings:
    """创建指向本机 TEI 的 embedding 客户端（OpenAI 兼容协议）。"""
    return init_embeddings(f"openai:{model}", **kwargs)


class EmbeddingClientManager:
    """Embedding 客户端的创建、复用与关闭。"""

    def __init__(self, config: EmbeddingConfig):
        self.config = config
        # 客户端在 init() 中创建，构造阶段不建立外部连接
        self._client: Embeddings | None = None

    @property
    def client(self) -> Embeddings:
        """已初始化的客户端；未调用 init() 时报错。"""
        assert self._client is not None, "Embedding 客户端尚未初始化，请先调用 init()"
        return self._client

    def _get_url(self):
        """拼出 Embedding 服务地址。"""
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        """创建客户端，在应用启动阶段调用。"""
        self._client = build_embeddings(
            self.config.model,
            base_url=f"{self._get_url()}/v1",
            api_key=SecretStr("not-needed"),  # TEI 不校验 key，但该字段不能为空
            check_embedding_ctx_length=False,
        )


# 全局单例，供其他模块复用同一个客户端
embedding_client_manager = EmbeddingClientManager(app_config.embedding)


if __name__ == "__main__":
    embedding_client_manager.init()
    client = embedding_client_manager.client

    async def test():
        """最小验证：对示例文本做一次向量化。"""
        query_result = await client.aembed_query("What is deep learning?")
        print("向量维度:", len(query_result))
        # 正确配置下的参考值，改参数后可对照它发现静默算错：
        # [-0.005919582676142454, 0.005813124123960733, 0.018300632014870644]
        print("前 3 个值:", query_result[:3])

    asyncio.run(test())
