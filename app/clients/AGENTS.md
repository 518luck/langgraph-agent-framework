# app/clients

适用：各类基础服务客户端（MySQL / ES / Qdrant / Embedding）的创建、持有与关闭。

## 必须

- 一个外部服务一个文件，命名 `<service>_client_manager.py`；类名 `<Service>ClientManager`。
- 同一服务多套连接按用途命名（如 `meta_mysql_client_manager` / `dw_mysql_client_manager`）。
- 构造接收该服务的配置对象并存为属性；模块底部导出单例 `<service>_client_manager`。
- 内部状态私有（`_client` / `_engine` / `_session_factory`），类型 `X | None`，初值 `None`。
- 对外只读 property：`assert` 非空后返回；断言文案「尚未初始化，请先调用 init()」。
- `init()` 内创建连接与客户端；import 阶段不建立连接。
- `close()` 幂等；底层客户端无关闭入口则不实现。
- 底部 `if __name__ == "__main__"`：初始化后做一次最小调用自测。

## 禁止

- 业务语义、SQL、向量化、字段/指标/表信息：归仓储层（`repositories`）与服务层（`services`）。
- 客户端内硬编码地址、端口、密钥：来自项目配置入口。
- 调用方判 `None`。
- 新增客户端后遗漏接线：入口脚本的 init 与 close、构造仓储时注入。
