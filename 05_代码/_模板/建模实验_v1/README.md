# 建模实验模板 v1

从本目录复制为 `05_代码/<项目名>/`。依赖锁在本项目，不进入仓库根环境。

```text
src/            Python 入口
matlab/         MATLAB 脚本（可选 Sidecar）
configs/
data/           小数据或 manifest；大数据只记 URI/hash
experiments/    实验说明
outputs/        运行产物（默认不提交）
```

正式结果必须能用记录命令重建，并在对应 `07_项目/<同名>/evidence.md` 留下 Evidence。

竞赛模板依赖（numpy / scipy / matplotlib / pandas）安装到 sidecar，不要写进仓库根 `requirements.txt`。算法模板在 `05_代码/_模板/数模竞赛_v1/`。

```text
python -m pip install -r tools/modeling/requirements-contest.txt
python -m tools.modeling contest-smoke
```
