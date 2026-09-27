# langgraph-agent-framework

FastAPI + LangGraph 智能体后端骨架。复制本目录开始新项目：框架已就绪，业务按各目录的 AGENTS.md 往里填。

每层目录下都有一份 AGENTS.md，写的是该层放什么、有哪些约定。看某层的文件时，把同目录的那份一起看。

## 架构

一次请求怎么走：

```text
POST /api/query
  -> main.py                  创建 app、挂载路由、注册 lifespan 与 request_id 中间件
  -> app/api/routers/         路由：解析请求体、声明依赖、返回流式响应
  -> app/api/dependencies.py  依赖树：Session -> Repository -> Service
  -> app/services/            业务编排：造 State/Context、跑图、包成 SSE、兜底异常
  -> app/agent/graph.py       图：注册节点、连边、条件分支
  -> app/agent/nodes/         节点：读 state、用 runtime.context、写进度、返回局部更新
  <- SSE 逐段回传（progress / result / error），前端按事件渲染
```

依赖从哪来（三层生命周期，不要混）：

```text
应用级   lifespan    客户端、连接池、Session 工厂      启动时一次
请求级   Depends     Session、Repository、Service     每个请求
执行级   Context     节点要用的工具对象                每次图执行
```

数据放哪（三个通道的边界）：

```text
State     节点之间流动的业务数据，会被累加、被观测、参与分支判断
Context   节点执行时用的工具对象，只读，不参与合并
Stream    给前端的进度与结果：progress（三态）/ result / error
```

## 文件清单

**根目录**

| 文件 | 职责 |
| --- | --- |
| `main.py` | FastAPI 入口：创建应用、挂载路由、注册 lifespan 与 request_id 中间件 |
| `pyproject.toml` | 依赖与工具配置；`package = false`（应用本身不装进环境） |
| `conf/app_config.yaml` | 服务地址、模型、日志开关；密钥走根目录 `.env` |
| `prompts/` | 提示词文件；命名与变量约定见该目录 README.md |
| `docker/` | 基础服务编排与初始化脚本，见该目录 README.md |
| `frontend/` | 聊天界面：SSE 消费 + 步骤条 + 结果表格 |

**app/api —— 对外 HTTP 层**

| 文件 | 职责 |
| --- | --- |
| `routers/query_router.py` | 查询接口：接请求、声明依赖、返回 `StreamingResponse` |
| `schemas/query_schema.py` | 请求体模型（Pydantic） |
| `dependencies.py` | 依赖组装：Session → Repository → Service |
| `lifespan.py` | 应用级资源：启动 init 客户端、关闭 close |
| `AGENTS.md` | 本层约定：路由只做三件事、新增依赖的同步清单 |

**app/services —— 业务编排层**

| 文件 | 职责 |
| --- | --- |
| `query_service.py` | 造 State/Context → `graph.astream` → 包 SSE；异常兜底成 `error` 事件 |
| `AGENTS.md` | 本层约定 |

**app/agent —— 智能体层**

| 文件 | 职责 |
| --- | --- |
| `graph.py` | 图定义：注册节点、连边、条件边、`compile()` |
| `state.py` | 共享状态 Schema（业务数据） |
| `context.py` | 运行时依赖 Schema（工具对象） |
| `llm.py` | 唯一模型入口，从配置读模型名 / base_url / api_key |
| `nodes/` | 一节点一文件；外壳与载荷约定见本目录 AGENTS.md |
| `AGENTS.md` | 节点外壳模板（三态进度 + `raise`）、状态与上下文的边界 |

**app/ 其余目录 —— 基础设施层**

| 目录 | 职责 |
| --- | --- |
| `clients/` | 外部服务客户端：创建、持有、关闭；init 一次全应用复用 |
| `repositories/` | 数据访问：按存储分子树，读写收口在本层，mapper 负责实体 ↔ 模型 |
| `entities/` | 业务实体（`@dataclass`），字段名与落库 / 索引侧一致 |
| `models/` | ORM 模型（SQLAlchemy 声明式） |
| `conf/` | 把 `conf/*.yaml` 读成带类型校验的对象 |
| `core/` | 日志（自动注入 request_id）与请求上下文（ContextVar） |
| `prompt/` | `load_prompt(名字)`：读 `prompts/<名字>.prompt` |
| `scripts/` | 命令行入口脚本：只做装配与调度 |
| 各目录 `AGENTS.md` | 本层约定；改代码前先读对应目录的这一份 |

## 新增一个能力的清单

按依赖顺序做，前后不会打架：

1. 配置：`conf/app_config.yaml` 加项 → `app/conf/app_config.py` 加对应字段
2. 数据：`app/entities/` + `app/models/` + `app/repositories/`（含 mapper）
3. 状态与依赖：`app/agent/state.py` 加流转字段、`app/agent/context.py` 加该节点要用的依赖
4. 节点：`app/agent/nodes/` 写节点（照外壳模板），需要模型时用 `app/agent/llm.py` 的 `llm`
5. 图：`app/agent/graph.py` 注册节点、连边、条件边
6. 装配：`app/api/dependencies.py` 注入新依赖、`app/api/lifespan.py` 补客户端 init / close

## AGENTS.md 编写规则

- 目标：极简操作契约，非项目文档。
- 只输出 Markdown 文件内容；不解释、不总结、不寒暄。
- 能推断的不写：README、package.json、pyproject.toml、Makefile、lint/format/test 配置、目录结构。改写成「遵循 <路径/工具默认>」。例外：骨架根文件保留本节的架构与文件清单，供新项目导航。
- 不写：项目介绍、背景、原因、通用最佳实践、重复配置。
- 不写软词：请、建议、可以、注意、应该、尽量。
- 用祈使句/清单/键值对。
- 无内容则省略该节，不硬凑。
- 不确定写 TODO 或留空，禁止编造。
- 分两层：根文件写全项目通用的规则；目录级文件只写本目录的规则。
- 目录级文件要能单独复制走：不写「见同目录其它文件」；复制到新项目后仍成立。
- 必须/禁止 内用总分：顶层只写本层通用规则；某能力或某文件的细则按名字分小节。

## 注释约束：

- 函数/类/模块首行一句话概括用途。
- 默认普通注释，不加 `>` / `!`。
- 仅必要时：`> ` 标重点逻辑；`! ` 标坑/危险/约束/安全。

## 交流

- 讲 Python 用 JS/TS 类比。

## 交付

- 改完代码跑：`uv run python -m app.agent.graph`、`uvx pyright app/ main.py`、`uvx ruff check app main.py`
- 后端起服务：`uv run fastapi dev main.py`；前端：`cd frontend && pnpm dev`
- 检查与格式化配置遵循 `pyproject.toml`；TODO：补 `reportUnnecessaryCast = "warning"`

## 类型

- 断言优先 `assert isinstance`：运行时校验 + 类型收窄。
- `cast` 仅用于库边界信息丢失处；单表达式；不 cast 到 `Any`；写明理由。

## TypedDict

- 形式：class 语法；非必要不用函数式 `TypedDict("X", {...})`。
- 数据形状（LLM 结构化输出、JSON、Agent 状态）：`total=True`；可选字段 `NotRequired[T]`。
- 函数参数（`**kwargs: Unpack[T]`）：`total=False`；必传参数 `Required[T]`。
- 样板：`app/clients/embedding_client_manager.py` 的 `EmbeddingInitKwargs`。
