# Qt 桌面工作台

**状态：** Desktop Shell v0.1  
**传输：** 进程内读取仓库  
**禁止：** 把 Qt 写成 Frozen Schema；把 PySide6 写进根 `requirements.txt`；用窗口程序直接改 YAML

---

## 为什么是窗口

日常入口不再打开 `http://127.0.0.1:3000/`。双击 `打开工作台.bat`（或 `打开工作台.vbs`）出现 **MATH-AI-LAB** 窗口。启动脚本会用 `pythonw` 拉起窗口，关掉黑色命令行不会把工作台一起关掉。失败时会弹窗，日志在 `%TEMP%\math-ai-lab-qt-launch.log`。

数据仍来自 Markdown / YAML / Lean。Qt 只是壳。

```text
仓库 Source
    ↓
tools.studio.catalog / Validator parsers
    ↓
tools.qt_workbench（QMainWindow）
```

没有 HTTP 服务，没有端口号。

---

## 启动

```text
python -m pip install -r tools/qt_workbench/requirements.txt
python -m tools.qt_workbench launch
python -m tools.qt_workbench doctor
python -m tools.qt_workbench gpt-status
python -m tools.qt_workbench gpt-test
```

`doctor` 在未安装 PySide6 时为 **DEGRADED**，不得让 Python Core FAIL。

---

## 布局

三栏：导航（学习 / 研究 / 个人 / 高级）· 对象列表 · 正文。

- YAML `status` 与工作流目录分两行，不合成一枚徽章
- `knowledge: []` 显示「mapping 已完成，当前没有直接对象」
- **阅读**页渲染 Markdown 标题、列表和 KaTeX 公式（Typora 式阅读结果）；**源码**页才显示 `$...$` 原文
- **操作**页走同一套 Domain Operation：题目可记录 Attempt、移动工作流目录；知识 / 题目 / 方法可「新建」；收件箱可提升。先预览再确认。
- Lab「操作」可评估 sum-free 候选；探索「操作」可字面检索过程记录。这两项不写 Canonical。
- 猜想 / 实验 / 时间线保持未开放

## 在窗口里改文件

知识 / 题目 / 方法 / 研究 / 记忆 / 收件箱 / 提示词：切到 **源码**，改正文，点 **保存正文** 或 Ctrl+S。

保存走 `UpdateMarkdownBody`：先 preview，校验通过后再确认写入。YAML Front Matter 不在编辑器里出现，也不会被这次保存改掉。Lab / Lean 对照仍只读。

写入 Attempt / 新建 / 提升 / 移动目录同样只经 `tools.ui_operations`，不经通用文件 API。

设置页按「模型偏好 / 接入 GPT / 对话」三张卡片排，左侧列出这三项。顶栏有 GPT 接入状态。模型偏好写入 `.mathailab/ai-model.json`；密钥写入 `.mathailab/credentials.json`。都不是 Frozen Schema，也不经 Domain Operation。Cursor 对话仍在 Cursor 输入框旁选模型。

可选浏览器界面：`打开网页工作台.bat`。
