"""请求上下文：保存一次请求（或一次脚本执行）期间的上下文变量。

当前只维护 request_id，供日志模块注入到每条日志。
"""

from contextvars import ContextVar

# 默认值供命令行脚本使用：脚本不经过 FastAPI 中间件，没有人提前 set
request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="1")
