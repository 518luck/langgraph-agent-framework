# app/agent

适用：LangGraph 智能体工作流，例如图定义、状态、运行上下文、模型与节点。

```text
app/agent
├── AGENTS.md
├── context.py   定义运行上下文
├── graph.py     定义图
├── llm.py       定义模型
├── nodes/       定义各节点
└── state.py     定义状态
```

以上是最小结构，非必要不要新增结构

## context.py

- 只放节点执行时的外部依赖：仓储与客户端。
- 只声明字段，不实例化；实例由接口层组装注入。
- 字段名与节点 `runtime.context[...]` 的键名一致。
- 依赖随使用它的节点增加，不提前预留。
- 新增依赖后同步接口层的 `DataAgentContext(...)` 组装。

## graph.py

- 只做四件事：声明 `state_schema` / `context_schema`、`add_node` 注册、连边、`compile()`。
- 节点名与函数名一致。
- 并行用多条出边；分支用条件边，不写进节点内部。
- 条件边的 `path` 用具名函数并返回目标节点名，不用 lambda。
- `graph` 在模块级 `compile()`，供接口层 import。
- 保留 `demo()` 与 `__main__` 作为本地串联入口。
- 新增或删除节点后同步：注册、连边、`demo()` 的 state 构造。

## llm.py

- 唯一模型入口；节点只 `from app.agent.llm import llm`。
- 模型名、`base_url`、`api_key` 从配置读取。
- `temperature=0`。

## nodes/

- 一个节点一个文件，文件名与节点名一致。
- 签名固定为 `async def <node>(state: DataAgentState, runtime: Runtime[DataAgentContext])`，两个参数名不改。
- 外壳固定如下，尖括号处填入本节点内容：

```python
async def <node>(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    """<一句话职责>"""

    writer = runtime.stream_writer
    step = "<步骤名>"
    writer({"type": "progress", "step": step, "status": "running"})

    try:
        <业务逻辑>
        writer({"type": "progress", "step": step, "status": "success"})
        return {"<字段名>": <值>}
    except Exception as e:
        logger.error(f"{step} failed: {e}")
        writer({"type": "progress", "step": step, "status": "error"})
        raise
```

- 需要记录成功日志时，在 `success` 与 `return` 之间加 `logger.info(...)`。
- 只返回局部更新，不返回整份 state；失败走 `raise`，不吞异常、不靠日志继续往下走。
- 例外一 校验类节点：外部服务的“拒绝”属业务结果而非节点失败 —— 内层只捕获那一种异常，写 `success` 与 `error` 字段后返回，由条件边决定下一步；其它异常交给外层抛出：

```python
        try:
            await <外部校验调用>              # 例如某个仓储的 validate(sql)
            writer({"type": "progress", "step": step, "status": "success"})
            return {"error": None}
        # ! 只把这一个异常交给条件边；其它异常交给外层抛出
        except <该调用只会抛的异常> as e:
            writer({"type": "progress", "step": step, "status": "success"})
            return {"error": str(e)}
```

- 例外二 产出最终结果的那个节点：在 `success` 之后额外写一条 `result`，前端据此取数据：

```python
        writer({"type": "progress", "step": step, "status": "success"})
        writer({"type": "result", "data": result})
```

- 载荷只有三类：`progress`（三态）、`result`（仅产出最终结果的节点写一条）、`error`（由接口层 QueryService 兜底）。
- 读 state 用下标；依赖从 `runtime.context[...]` 取，不放进 state。
- 不 import 其它节点；不读配置、不建客户端。
- 需要模型时走 `PromptTemplate | llm | OutputParser`；结构化输出用 `JsonOutputParser`，纯文本用 `StrOutputParser`。
- 提示词一律 `load_prompt("<名字>")`，不在代码里内联长文本。

## state.py

- 只放节点间传递的业务数据：查询、关键词、召回结果、提示词上下文、SQL、错误。
- 一律 `TypedDict` + 类语法。
- 节点会写入的字段在入口处一并置空值，不用可选键。
- 面向提示词的结构单独定义（`TableInfoState` / `ColumnInfoState` / `MetricInfoState` / `DateInfoState` / `DBInfoState`），不复用实体。
- 不放仓储、客户端、模型对象。
- 实体类型只从 `app.entities` 引用。
