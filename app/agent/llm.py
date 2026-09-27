from langchain.chat_models import init_chat_model

# .env 由 app.conf.app_config 在自己的模块顶层加载，早于这里的配置读取
from app.conf.app_config import app_config

# 统一从配置读取模型三件套，节点只复用 llm，不重复初始化模型连接
llm = init_chat_model(
    model=app_config.llm.model_name,
    # 硅基流动等服务兼容 OpenAI 协议时，可以使用 openai provider 接入
    model_provider="openai",
    base_url=app_config.llm.base_url,
    api_key=app_config.llm.api_key,
    # 召回扩展、SQL 生成更看重稳定性，所以这里关闭随机发散
    temperature=0,
)

if __name__ == "__main__":
    # 单独运行本文件时，用一个最小请求验证模型名、密钥和 base_url 是否配置正确
    print(llm.invoke("你好").content)
