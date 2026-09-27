# LangGraph Agent Framework

可复用的智能体后端框架骨架：FastAPI 提供 SSE 流式接口，LangGraph 编排带状态的节点链路，
MySQL / Qdrant / ES / Embedding 的客户端与仓储分层已就绪，前端（React + Vite）展示进度与结果。

## 包含什么

- **分层结构**：`clients`（外部服务客户端）→ `repositories`（数据访问 + mapper）→ `services`（业务编排）→ `api`（HTTP 层）
- **Agent 层**：`app/agent/` 下的图、状态、运行时上下文、模型入口与节点
- **消息协议**：节点写 `progress`（三态）/ `result`，服务层兜底 `error`，前端按 SSE 消费
- **一条可运行的最小示例链路**：抽取关键词 → 生成 SQL → 校验 SQL → 执行（校验失败则先校正再执行）
- **全部 AGENTS.md 契约文件**：各目录的硬约定

示例数据是两张订单相关表（附在 `docker/mysql/` 里），换成自己的领域按下面的清单改即可。

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

## 换成你自己的领域

按依赖顺序改，前后不会打架：

| 步骤 | 改哪里 | 做什么 |
| --- | --- | --- |
| 1 | `docker/mysql/*.sql` | 表结构与示例数据 |
| 2 | `conf/app_config.yaml` | 连什么：host / port / database、模型 |
| 3 | `app/entities` + `app/models` | 领域实体与 ORM 模型 |
| 4 | `app/repositories` | 领域仓储（仓储 + mapper 模式） |
| 5 | `app/agent/state.py` | 这条链路要流转哪些业务数据 |
| 6 | `app/agent/context.py` | 节点要用哪些外部依赖 |
| 7 | `app/agent/nodes/` | 节点实现 |
| 8 | `app/agent/graph.py` | 重连这张图 |
| 9 | `prompts/` + `app/api/` | 提示词与路由 |

## 改代码前先读约定

各目录的 `AGENTS.md` 是硬约定，不是说明文档：

- `app/agent/AGENTS.md` —— 节点外壳模板（三态进度 + `raise`）、状态与上下文的边界、图的写法
- `app/repositories/AGENTS.md` —— 仓储与 mapper 的规矩
- `app/api/AGENTS.md` —— HTTP 层职责
- 根 `AGENTS.md` —— 交付检查与类型规则

新增节点、新增依赖、新增仓储时，先看对应目录的 `AGENTS.md` 和其中列的同步清单。
