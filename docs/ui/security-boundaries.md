# Security boundaries（本地工作台）

这是 localhost 应用，不是多用户云服务。仍然禁止「任意网页写仓库」。

## 写接口

- 仅 `POST /api/operations`
- 仅白名单 Domain Operation
- 拒绝 `root` / `path` / `file` / `command` / `cwd` / `shell`
- Origin 仅 `127.0.0.1` / `localhost` / `[::1]`（缺 Origin 视为同机）
- 对象路径由 operation + Frozen ID 在服务器解析
- Inbox 仅允许 `00_收件箱/` 下的文件名，禁止 `..`

## 读接口

- `/api/object-exists` 只回答是否存在
- `/api/search` 只读派生索引
- `/api/artifact` 只读成果文件
- `/repository` 只列白名单目录，不执行源码

## 测试

写入测试必须使用 temporary fixture workspace。禁止对真实 `01_知识库` / `02_题目库` / `12_方法库` / `00_收件箱` 做测试 persist。
