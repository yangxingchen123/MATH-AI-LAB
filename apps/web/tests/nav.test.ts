import { describe, expect, it } from "vitest";
import { NAV_GROUPS, allNavItems, isActivePath } from "../features/shell/nav";

describe("Human Interface v1 navigation", () => {
  it("groups surfaces into 学习 / 研究 / 个人 / 高级", () => {
    expect(NAV_GROUPS.map((group) => group.id)).toEqual([
      "learn",
      "research",
      "personal",
      "advanced",
    ]);
    expect(NAV_GROUPS.map((group) => group.label)).toEqual([
      "学习",
      "研究",
      "个人",
      "高级",
    ]);
    expect(NAV_GROUPS[0]?.items.map((item) => item.label)).toEqual([
      "知识",
      "题目",
      "方法",
    ]);
    expect(NAV_GROUPS[1]?.items.map((item) => item.label)).toEqual([
      "研究",
      "参考",
      "成果",
      "猜想",
      "实验",
      "时间线",
    ]);
    expect(NAV_GROUPS[2]?.items.map((item) => item.label)).toEqual([
      "记忆",
      "收件箱",
      "提示词",
    ]);
    expect(NAV_GROUPS[3]?.items.map((item) => item.id)).toEqual([
      "lean",
      "lab",
      "universe",
      "explore",
      "repository",
      "diagnostics",
      "settings",
    ]);
  });

  it("keeps Human Interface v1 surfaces ready and Research Intelligence disabled", () => {
    const later = allNavItems().filter((item) => item.phase === "later");
    expect(later.map((item) => item.id)).toEqual(["conjectures", "experiments", "timeline"]);
    expect(later.every((item) => item.href === null)).toBe(true);
    const ready = allNavItems().filter((item) => item.phase === "ready");
    expect(ready.every((item) => item.href)).toBe(true);
  });

  it("marks nested object routes as active", () => {
    expect(isActivePath("/knowledge/K0001", "/knowledge")).toBe(true);
    expect(isActivePath("/explore/reasoning", "/explore")).toBe(true);
    expect(isActivePath("/problems", "/")).toBe(false);
  });
});
