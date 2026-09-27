# app/models

适用：ORM 模型，主要对应 MySQL 中的表结构。

## 必须

- 一表一模块；公共基类集中在 `base.py`，其余模型继承它。

### 定义

- 类名 `<表名驼峰>MySQL`；`__tablename__` 用真实表名。
- 字段用 `Mapped[...]` + `mapped_column(...)`；列名、类型、长度对齐建表脚本 `docker/mysql/04-meta-schema.sql`。
- 主键标 `primary_key=True`；联合主键逐列标。
- JSON 列用 `Mapped[list[...]]` + `JSON`。

### 空值

- 写入时必有值的列声明为非 Optional（`Mapped[str]`）：mapper 的 `to_entity` 才不用判空。
- 确实可为空的列才写 `Mapped[X | None]`。

## 禁止

- 写查询、写入、事务：归 repository。
- 加业务方法或计算属性。
- 引用 `entities` 或上层模块（`repositories` / `services` / `clients` / `agent`）。
- 改列名或类型后遗漏同步：建表脚本、mapper、实体字段名。
