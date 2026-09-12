export type NavHref = string | null;

export interface NavItem {
  id: string;
  label: string;
  href: NavHref;
  phase: "ready" | "later";
}

export interface NavGroup {
  id: "learn" | "research" | "personal" | "advanced";
  label: string;
  items: NavItem[];
}

export const HOME_NAV: NavItem = {
  id: "home",
  label: "工作台",
  href: "/",
  phase: "ready",
};

export const NAV_GROUPS: NavGroup[] = [
  {
    id: "learn",
    label: "学习",
    items: [
      { id: "knowledge", label: "知识", href: "/knowledge", phase: "ready" },
      { id: "problems", label: "题目", href: "/problems", phase: "ready" },
      { id: "methods", label: "方法", href: "/methods", phase: "ready" },
    ],
  },
  {
    id: "research",
    label: "研究",
    items: [
      { id: "research", label: "研究", href: "/research", phase: "ready" },
      { id: "references", label: "参考", href: "/references", phase: "ready" },
      { id: "outputs", label: "成果", href: "/outputs", phase: "ready" },
      { id: "conjectures", label: "猜想", href: null, phase: "later" },
      { id: "experiments", label: "实验", href: null, phase: "later" },
      { id: "timeline", label: "时间线", href: null, phase: "later" },
    ],
  },
  {
    id: "personal",
    label: "个人",
    items: [
      { id: "memory", label: "记忆", href: "/memory", phase: "ready" },
      { id: "inbox", label: "收件箱", href: "/inbox", phase: "ready" },
      { id: "prompts", label: "提示词", href: "/prompts", phase: "ready" },
    ],
  },
  {
    id: "advanced",
    label: "高级",
    items: [
      { id: "lean", label: "Lean", href: "/lean", phase: "ready" },
      { id: "lab", label: "Lab", href: "/lab", phase: "ready" },
      { id: "universe", label: "宇宙", href: "/universe", phase: "ready" },
      { id: "explore", label: "探索", href: "/explore", phase: "ready" },
      { id: "repository", label: "仓库", href: "/repository", phase: "ready" },
      { id: "diagnostics", label: "诊断", href: "/advanced/diagnostics", phase: "ready" },
      { id: "settings", label: "设置", href: "/settings", phase: "ready" },
    ],
  },
];

export function allNavItems(): NavItem[] {
  return [HOME_NAV, ...NAV_GROUPS.flatMap((group) => group.items)];
}

export function isActivePath(pathname: string, href: string): boolean {
  if (href === "/") {
    return pathname === "/";
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}
