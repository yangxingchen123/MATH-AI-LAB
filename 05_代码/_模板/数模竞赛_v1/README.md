# 数模竞赛代码模板 v1

来源：[Lupynow/math-modeling-skills](https://github.com/Lupynow/math-modeling-skills)（MIT）。
工作副本从 `.cursor/skills/math-modeling-solver/references/code-templates/` 同步到这里，方便拷进 `05_代码/<赛题>/`。

钉住的只读 pin 仍在 `vendor/math-modeling-skills/`。不要把 numpy / matplotlib 写进仓库根 `requirements.txt`。

```text
python/     AHP、GA、ODE、TOPSIS 等
matlab/     对应 MATLAB 脚本
```

使用：把需要的模板拷到 `05_代码/<赛题>/src/` 或 `matlab/`，改成本题符号后再跑。

```text
python -m pip install -r tools/modeling/requirements-contest.txt
python -m tools.modeling contest-smoke
```
