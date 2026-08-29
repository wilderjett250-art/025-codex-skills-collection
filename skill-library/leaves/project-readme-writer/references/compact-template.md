# Compact bilingual project README template

Use this as a starting structure, then replace every bracketed item with evidence from
the repository. Remove sections that do not apply.

```markdown
# 中文项目名 / English Project Name

> 一句话说明项目解决的问题和带来的结果。
>
> One sentence describing the problem solved and the useful result.

## 解决什么问题 / Problem

中文：面向谁，处理什么输入，最终得到什么结果。

English: Who it serves, what it takes as input, and what useful result it produces.

## 项目展示 / Demo

![真实运行截图](docs/demo.png)

从 `[入口文件或命令]` 开始，完成 `[关键动作]`，页面/窗口会显示 `[可观察结果]`。

Start with `[entry file or command]`, perform `[key action]`, and observe `[visible result]`.

## 高光亮点 / Highlights

- 中文亮点一：具体功能或已验证结果。
  English: Concrete feature or verified result.
- 中文亮点二：具体设计取舍或用户收益。
  English: Concrete design choice or user benefit.
- 中文亮点三：可复现的工程能力。
  English: Reproducible engineering capability.

## 技术名词 / Tech

`Python` · `FastAPI` · `ONNX Runtime` · `SQLite`

## 从 ZIP 开始复现 / Reproduce from ZIP

1. 解压 ZIP 并进入项目根目录。
2. 安装 `[真实依赖或运行时]`。
3. 执行 `[已经验证过的命令]`，或双击 `[已验证的 EXE/APK/入口文件]`。
4. 打开 `[地址/窗口/输出文件]`，确认 `[预期结果]`。

1. Extract the ZIP and enter the project root.
2. Install `[verified dependency or runtime]`.
3. Run `[verified command]`, or open `[verified EXE/APK/entry file]`.
4. Open `[address/window/output]` and confirm `[expected result]`.

## 范围与安全 / Scope and Safety

中文：只写会影响实际使用的外部服务、数据、模型许可或集成条件。

English: Mention only external services, data, model licensing, or integration conditions
that affect real use.

## 交流 / Contact

欢迎交流技术。

Open to technical exchange.
```

Rules:

- Keep the main README short enough to scan in one or two minutes.
- Keep one real visual or one explicit input -> processing -> output flow.
- Replace or remove every bracketed item before publishing.
- Do not include secrets, private paths, machine-specific credentials, or unverified
  claims.
