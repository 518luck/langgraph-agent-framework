# app/repositories

适用：数据访问层，封装 MySQL / Qdrant / ES 的具体读写逻辑。

## 必须

- 按存储分子树：`mysql/`（`dw` / `meta`）、`qdrant/`、`es/`；一个数据源一个模块。
- 读写收口在本层：service 不碰 SQL 与 ORM 模型。
- 客户端与 session 由调用方注入；本层不开启、不提交事务。

### MySQL

- `dw` 只读：补齐数仓真实信息（字段类型、取值）。
- `meta` 只写：实体 → mapper → 模型 → `add_all`。
- 查询粒度按表（列信息）与按列（取值）；表名、列名只来自配置或实体。

### Mapper

- 一个实体一个 mapper；提供 `to_model` 与 `to_entity`。
- 用 `asdict` 直传构造模型：字段名与实体一致。

### Qdrant

- 一个 collection 一个模块；`collection_name` 为类常量，字段与指标分开。
- 维度取 `app_config.qdrant.embedding_size`，距离 COSINE；建集合时固定。
- `ids` / `embeddings` / `payloads` 等长同序；写入按 `batch_size` 分批。

### ES

- `index_name` 与 `index_mappings` 用 `ClassVar` 声明为类常量。
- mapping：检索字段用 `text` + 中文分词，标识字段用 `keyword`，`dynamic: false`。
- 写入用 bulk 的「操作行 + 数据行」交替结构，按 `batch_size` 分批。

## 禁止

- 业务编排与流程控制：归 service。
- 把 ORM 模型传给上层。
- `dw` 侧写入、`meta` 侧查数仓：两侧职责不混。
- 新增仓储后遗漏接线：入口脚本构造并注入 service。
