"""Navigation model. Matches Human Interface pillars. Not Frozen Schema."""

from __future__ import annotations

from typing import Any

NAV_GROUPS: list[dict[str, Any]] = [
    {
        "id": "learn",
        "label": "学习",
        "items": [
            {"id": "knowledge", "label": "知识", "kind": "knowledge", "enabled": True},
            {"id": "problems", "label": "题目", "kind": "problem", "enabled": True},
            {"id": "methods", "label": "方法", "kind": "method", "enabled": True},
        ],
    },
    {
        "id": "research",
        "label": "研究",
        "items": [
            {"id": "research", "label": "研究", "kind": "project", "enabled": True},
            {"id": "references", "label": "参考", "kind": "references", "enabled": True},
            {"id": "outputs", "label": "成果", "kind": "outputs", "enabled": True},
            {"id": "conjectures", "label": "猜想", "kind": "conjectures", "enabled": False},
            {"id": "experiments", "label": "实验", "kind": "experiments", "enabled": False},
            {"id": "timeline", "label": "时间线", "kind": "timeline", "enabled": False},
        ],
    },
    {
        "id": "personal",
        "label": "个人",
        "items": [
            {"id": "memory", "label": "记忆", "kind": "memory", "enabled": True},
            {"id": "inbox", "label": "收件箱", "kind": "inbox", "enabled": True},
            {"id": "prompts", "label": "提示词", "kind": "prompts", "enabled": True},
        ],
    },
    {
        "id": "advanced",
        "label": "高级",
        "items": [
            {"id": "lean", "label": "Lean", "kind": "lean", "enabled": True},
            {"id": "lab", "label": "Lab", "kind": "lab", "enabled": True},
            {"id": "universe", "label": "宇宙", "kind": "universe", "enabled": True},
            {"id": "exploration", "label": "探索", "kind": "exploration", "enabled": True},
            {"id": "settings", "label": "设置", "kind": "settings", "enabled": True},
        ],
    },
]

HOME_ITEM = {"id": "home", "label": "工作台", "kind": "home", "enabled": True}

STUDIO_KINDS = {"knowledge", "problem", "method", "project", "lab"}
FILE_KINDS = {"memory", "inbox", "prompts", "references", "outputs"}


def all_nav_items() -> list[dict[str, Any]]:
    items = [HOME_ITEM]
    for group in NAV_GROUPS:
        items.extend(group["items"])
    return items
