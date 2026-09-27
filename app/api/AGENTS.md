# app/api

适用：对外 HTTP 接口层，例如路由、请求响应结构、依赖组装与应用生命周期。

## 必须

- 一业务主题一个 router 模块，由根目录 `main.py` 统一挂载。
- 路由只做三件事：解析请求体、声明依赖、返回响应。
- 组装细节收敛在 `dependencies.py`：路由只写 `Annotated[XxxService, Depends(get_xxx_service)]`。
- 应用级资源（客户端、连接池、Session 工厂）在 `lifespan.py` 里初始化与释放，不放进请求级依赖。
- 请求级资源（数据库 Session 等）用带 `yield` 的依赖项，请求结束后自动归还。
- 流式响应用 `StreamingResponse(..., media_type="text/event-stream")`，每条消息以 `data: ` 开头、空行结束。

### 新增依赖时的同步清单

- `dependencies.py` 补 `get_xxx`，并在 `get_query_service` 的参数里注入。
- `lifespan.py` 补对应客户端的 `init()` 与 `close()`。
- `app/agent/context.py` 补同名字段：节点才能从 `runtime.context[...]` 取到它。

## 禁止

- 路由函数里写业务编排（创建 State / Context、调用图、拼 SSE 文本）。
- 路由函数直接创建 Repository 或客户端。
- 把 ORM 模型或底层客户端对象直接塞进响应。
