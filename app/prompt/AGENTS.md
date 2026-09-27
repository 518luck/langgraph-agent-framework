# app/prompt

适用：提示词文件的加载入口。

## 必须

- 只放加载逻辑：按名字读 `prompts/<名字>.prompt`，返回字符串。
- 提示词文件本身放项目根目录的 `prompts/`；命名与变量约定见 `prompts/README.md`。
- 路径按文件位置定位（`Path(__file__).parents[2]`），不依赖启动目录。
- 读文件带 `encoding="utf-8"`：提示词含中文，缺编码在部分平台会乱码。

## 禁止

- 在本层做变量替换或模板渲染：归 `PromptTemplate`。
- 在本层拼业务内容：上下文由节点从 `state` 或 `runtime.context` 取出后作为变量传入。
