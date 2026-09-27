# 应用配置入口：把 conf/app_config.yaml 读成带类型校验的 AppConfig 对象。

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from omegaconf import OmegaConf

# ! 必须在下面解析 ${oc.env:LLM_API_KEY} 之前加载 .env：
#   本模块一被 import，插值就固化成当时的取值，晚调用只会拿到兜底值，调用时报 401。
#   路径按文件位置定位，避免依赖启动目录。
load_dotenv(Path(__file__).parents[2] / ".env")


@dataclass
class File:
    """文件日志配置，对应 logging.file。"""

    enable: bool
    level: str
    path: str
    rotation: str
    retention: str


@dataclass
class Console:
    """控制台日志配置，对应 logging.console。"""

    enable: bool
    level: str


@dataclass
class LoggingConfig:
    """日志总配置，组合 file 与 console。"""

    file: File
    console: Console


@dataclass
class DBConfig:
    """数据库连接配置，db_meta 与 db_dw 共用。"""

    host: str
    port: int
    user: str
    password: str
    database: str


@dataclass
class QdrantConfig:
    """Qdrant 连接配置。"""

    host: str
    port: int
    embedding_size: int


@dataclass
class EmbeddingConfig:
    """Embedding 服务连接配置，对应 YAML 的 embedding。"""

    host: str
    port: int
    model: str


@dataclass
class ESConfig:
    """Elasticsearch 连接配置。"""

    host: str
    port: int
    index_name: str


@dataclass
class LLMConfig:
    """大模型连接配置。"""

    model_name: str
    api_key: str
    base_url: str


@dataclass
class AppConfig:
    """配置总入口，字段名与 app_config.yaml 顶层一致。"""

    logging: LoggingConfig
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig
    llm: LLMConfig


# 回到项目根目录再定位配置文件（本文件在 app/conf/ 下，故用 parents[2]）
config_file = Path(__file__).parents[2] / "conf" / "app_config.yaml"

context = OmegaConf.load(config_file)
schema = OmegaConf.structured(AppConfig)
# > 合并“结构”与“值”：类型不符或字段缺失在这一步直接报错
result = OmegaConf.to_object(OmegaConf.merge(schema, context))
assert isinstance(result, AppConfig), f"配置加载失败: {type(result)}"
app_config: AppConfig = result

if __name__ == "__main__":
    # 验证配置能否正常读取
    print(app_config.es.host)
