# 基础服务

用 Docker 统一启动项目依赖的 5 个服务，避免逐个手工安装。

| 服务                      | 容器名        | 本机地址                        | 作用                            |
| ------------------------- | ------------- | ------------------------------- | ------------------------------- |
| MySQL                     | mysql         | localhost:13306                 | 元数据库 `meta` + 模拟数仓 `dw` |
| Elasticsearch             | elasticsearch | http://localhost:9200           | 字段取值的全文检索              |
| Kibana                    | kibana        | http://localhost:5601           | ES 的可视化调试界面             |
| Qdrant                    | qdrant        | http://localhost:6333/dashboard | 字段与指标的向量检索            |
| Text Embeddings Inference | embedding     | http://localhost:8081/docs      | 文本转向量的推理服务            |

## 目录说明

- `docker-compose.yaml`：5 个服务的编排定义
- `elasticsearch/Dockerfile`：在官方镜像上装 IK 中文分词器（版本需与 ES 一致）
- `mysql/`：MySQL 首次启动时自动执行的初始化脚本，按文件名顺序执行
- `embedding/`：Embedding 模型挂载目录

## 备注

- `embedding` 服务锁定 `platform: linux/amd64`，因为 TEI 的 CPU 镜像只有 amd64 版本。Apple Silicon 上会用模拟方式运行，首次启动和推理速度都会偏慢，属正常现象。
- IK 分词器与 Elasticsearch 版本必须完全一致，升级 ES 时两处要同步改：`docker-compose.yaml` 里的镜像 tag 和 `elasticsearch/Dockerfile` 里的插件版本。
- MySQL 初始化脚本只在数据目录为空（首次启动）时执行。改完 `mysql/` 下的脚本需要 `docker compose down -v` 后重启才会重新生效。
- MySQL 映射到本机 `13306`（不是默认的 3306），避免与本机或其他项目的 MySQL 冲突；用客户端连接时请填 13306，并同步改 `conf/app_config.yaml`。
