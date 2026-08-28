# Contest pipeline report

- generated: 2026-08-25
- status: INCOMPLETE
- paper_complete: False

本报告不是完稿论文。自动步骤可以复跑实验和检索候选数据；交卷内容必须人工完成。

## Auto steps
- `scaffold`: PASS — 07/05/04 present
- `dossier_check`: PASS — ok
- `select`: PASS — eligible=['energy_balance_soc']
- `find_data`: PASS — open=9 review=2
- `experiment:soc`: SUCCEEDED — energy_balance_soc
- `experiment:soc_sensitivity`: SUCCEEDED — energy_balance_soc_sensitivity
- `experiment:soc_piecewise`: SUCCEEDED — energy_balance_soc_piecewise
- `latex_draft`: PASS — 美赛2026-A.tex
- `publish_pdf`: BLOCKED — requires explicit user authorization

## Human gates (not automated)
- 核对题面 OCR / 官方 PDF，不得补写乱码句
- 核开放数据许可证后 ingest，再估参（替换 ASM-0006 假定瓦数）
- 电压 / Peukert 仅在有开放 I–V 或多倍率数据时扩展，不自动写入
- 人工改写 MCM 英文论文（Summary Sheet、引用、AI Use Report、≤25 页）
- 人工审核；未授权不得发布 08_成果输出 PDF，不得写入 Knowledge
