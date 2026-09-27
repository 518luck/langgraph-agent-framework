# prompts

提示词文件放在这里，一个用途一个 `.prompt` 文件。

## 约定

- 命名用「用途」描述，例如 `classify_intent.prompt`、`generate_summary.prompt`。
- 用 `load_prompt("<文件名>")` 读取，不带扩展名；加载器在 `app/prompt/prompt_loader.py`。
- 变量用单花括号占位，例如 `{query}`；确实要输出字面花括号时写双花括号 `{{ }}`
  （`PromptTemplate` 按 f-string 解析，单个花括号会被当成变量）。
- 节点里用 `input_variables=[...]` 声明需要的变量，变量名要与占位符一致，漏传会在
  `ainvoke` 时直接报错。
- 会随项目变化的内容（表结构、字段清单、可选范围）通过变量从 state 或 context 传进来，
  不要写死在提示词里。
