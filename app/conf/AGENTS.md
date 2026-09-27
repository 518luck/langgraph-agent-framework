# app/conf

适用：配置类与配置加载工具，把 YAML 配置转换成代码可直接使用的对象。

## 必须

- 一配置一模块：`<name>_config.py` 对应 `conf/<name>.yaml`。

### 形状

- 用 `@dataclass`；字段名与 YAML 键一致，嵌套类型与 YAML 层级一致。
- 可选段落写 `list[X] | None = None`。
- 取值固定的字段用 `str, Enum`：YAML 写错取值在加载时报错。

### 加载

- 四步：`OmegaConf.load` → `OmegaConf.structured` → `merge` → `to_object`；`assert isinstance(结果, 类)` 收窄后再赋给带类型的变量。
- 进程级配置：模块顶层加载并导出单例对象。
- 任务级配置：本层只给形状，加载由调用方用传入的路径执行。
- 定位文件：`Path(__file__).parents[2] / "conf" / "<name>.yaml"`。

### 密钥

- 不落 YAML：写 `${oc.env:VAR,兜底值}`，真实值放 `.env`。

## 禁止

- 形状模块内读文件、连服务、查库：归调用方。
- 形状里写具体业务内容（表名、字段名、指标名）：只在 YAML。
- 靠启动目录或绝对路径找配置文件。
