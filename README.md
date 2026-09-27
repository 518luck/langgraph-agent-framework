# LangGraph Agent Framework

可复用的智能体后端骨架：FastAPI 提供 SSE 流式接口，LangGraph 编排带状态的节点链路，
MySQL / Qdrant / ES / Embedding 的客户端与分层结构已就绪，前端（React + Vite）展示进度与结果。

## 骨架里有什么

- **分层结构**：`clients`（外部服务客户端）→ `repositories`（数据访问 + mapper）→ `services`（业务编排）→ `api`（HTTP 层）
- **Agent 层**：`app/agent/` 下的图、状态、运行时上下文、模型入口与节点
- **消息协议**：节点写 `progress`（三态）/ `result`，服务层兜底 `error`，前端按 SSE 消费
- **一个占位节点**：`app/agent/nodes/example.py` 演示节点外壳（三态进度 + 异常抛出）。照它写节点，写完删掉
- **各目录的 AGENTS.md**：硬约定，改代码前先读
- **架构图与文件清单**：见根目录 `AGENTS.md`

骨架里没有业务代码，也没有示例数据 —— 这是有意的：填业务比删业务省事。按下面的清单开始填。

## 快速开始

```bash
# 1. 起基础设施（用不到的服务可以从 docker-compose.yaml 里删掉）
cd docker && docker compose up -d

# 2. 装依赖
uv sync

# 3. 配置密钥
cp .env.example .env      # 填 LLM_API_KEY

# 4. 起后端
uv run fastapi dev main.py          # http://127.0.0.1:8000/docs

# 5. 起前端（可选）
cd frontend && pnpm install && pnpm dev   # http://localhost:5173
```

不起服务也可以直接跑图，进度打印到终端：

```bash
uv run python -m app.agent.graph
```

## 填业务的顺序

按依赖顺序改，前后不会打架（与根 `AGENTS.md` 的清单一致）：

| 步骤 | 改哪里 | 做什么 |
| --- | --- | --- |
| 1 | `docker/mysql/*.sql` | 建表与初始化数据（只在首次启动执行，改完要 `docker compose down -v` 再起） |
| 2 | `conf/app_config.yaml` | 连什么：host / port / database、模型 |
| 3 | `app/entities` + `app/models` | 业务实体与 ORM 模型 |
| 4 | `app/repositories` | 领域仓储（仓储 + mapper 模式） |
| 5 | `app/agent/state.py` | 这条链路要流转哪些业务数据 |
| 6 | `app/agent/context.py` | 节点要用哪些外部依赖 |
| 7 | `app/agent/nodes/` | 节点实现（照 `example.py` 的外壳） |
| 8 | `app/agent/graph.py` | 注册节点、连边、条件边 |
| 9 | `prompts/` + `app/api/` | 提示词与路由 |

## 交付前自查

```bash
uv run python -m app.agent.graph      # 图能跑
uvx pyright app/ main.py              # 类型检查
uvx ruff check app main.py            # 代码检查
```
