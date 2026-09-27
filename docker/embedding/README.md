# Embedding 模型目录

`Qwen3-Embedding-0.6B` 的权重文件体积较大，没有提交到 Git 仓库，需要先手动下载再启动服务。

在项目根目录执行：

```bash
uv run hf download Qwen/Qwen3-Embedding-0.6B --local-dir docker/embedding/Qwen3-Embedding-0.6B
```

下载完成后，该目录下至少应包含 `config.json`、`model.safetensors`、`tokenizer.json`、`tokenizer_config.json`、`vocab.json`、`merges.txt`。

目录为空会导致 `embedding` 容器启动后无法提供向量化服务。

## 模型要点（相对旧模型 bge-large-zh-v1.5 的变化）

- 输出维度仍是 **1024**（MRL 支持 32~1024 可调），`conf/app_config.yaml` 的 `qdrant.embedding_size: 1024` 无需改动。
- **instruction-aware**：查询侧可加 `Instruct: <任务描述>\nQuery: <查询文本>` 前缀提升检索质量；通过 TEI 的 `/embed` 接口直传文本也能正常使用。
- 上下文长度 32K（旧模型 512），长文本分块策略可放宽。
- TEI 需 1.7.2 及以上版本，当前 compose 锁定的 `cpu-1.8` 镜像满足要求。
