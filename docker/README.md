# 基础服务

用 Docker 统一启动项目依赖的 5 个服务，避免逐个手工安装。

| 服务                      | 容器名        | 本机地址                        | 作用                            |
| ------------------------- | ------------- | ------------------------------- | ------------------------------- |
| PostgreSQL                | 自动命名      | localhost:15432                 | 业务数据库 `app`                 |
| Elasticsearch             | elasticsearch | http://localhost:9200           | 文本全文检索（可选）            |
| Kibana                    | kibana        | http://localhost:5601           | ES 的可视化调试界面             |
| Qdrant                    | qdrant        | http://localhost:6333/dashboard | 向量检索（可选）                |
| Text Embeddings Inference | embedding     | http://localhost:8081/docs      | 文本转向量的推理服务            |

## 目录说明

- `docker-compose.yaml`：5 个服务的编排定义
- `elasticsearch/Dockerfile`：在官方镜像上装 IK 中文分词器（版本需与 ES 一致）
- `postgres/`：PostgreSQL 首次启动时自动执行的初始化脚本，按文件名顺序执行
- `embedding/`：Embedding 模型挂载目录

## 备注

- `embedding` 服务锁定 `platform: linux/amd64`，因为 TEI 的 CPU 镜像只有 amd64 版本。Apple Silicon 上会用模拟方式运行，首次启动和推理速度都会偏慢，属正常现象。
- IK 分词器与 Elasticsearch 版本必须完全一致，升级 ES 时两处要同步改：`docker-compose.yaml` 里的镜像 tag 和 `elasticsearch/Dockerfile` 里的插件版本。
- PostgreSQL 初始化脚本只在数据目录为空（首次启动）时执行。改完 `postgres/` 下的脚本需要 `docker compose down -v` 后重启才会重新生效。
- `postgres` 服务不写死 `container_name`：compose 按「项目名-服务名-序号」自动命名（如 `agent-framework-postgres-1`），本模板复制到多个项目同时启动也不会撞名。
- PostgreSQL 映射到本机 `15432`（不是默认的 5432），避免与本机或其他项目的 PostgreSQL 冲突；用客户端连接时请填 15432，并同步改 `conf/app_config.yaml`。
