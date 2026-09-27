# Embedding 模型目录

`bge-large-zh-v1.5` 的权重文件体积较大，没有提交到 Git 仓库，需要先手动下载再启动服务。

在项目根目录执行：

```bash
uv run hf download BAAI/bge-large-zh-v1.5 --local-dir docker/embedding/bge-large-zh-v1.5
```

下载完成后，该目录下至少应包含 `config.json`、`tokenizer.json`、`tokenizer_config.json`、`pytorch_model.bin`、`vocab.txt`。

目录为空会导致 `embedding` 容器启动后无法提供向量化服务。
