"use client";

import { useEffect, useState } from "react";

type Theme = "light" | "dark" | "system";

function applyTheme(theme: Theme) {
  const dark =
    theme === "dark" ||
    (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.classList.toggle("dark", dark);
}

function nextTheme(theme: Theme): Theme {
  return theme === "light" ? "dark" : theme === "dark" ? "system" : "light";
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("system");

  useEffect(() => {
    const stored = window.localStorage.getItem("math-ai-lab-theme");
    if (stored === "light" || stored === "dark" || stored === "system") {
      setTheme(stored);
      applyTheme(stored);
    }
    const onToggle = () => {
      setTheme((current) => {
        const next = nextTheme(current);
        window.localStorage.setItem("math-ai-lab-theme", next);
        applyTheme(next);
        return next;
      });
    };
    window.addEventListener("math-ai-lab-toggle-theme", onToggle);
    return () => window.removeEventListener("math-ai-lab-toggle-theme", onToggle);
  }, []);

  function cycle() {
    const next = nextTheme(theme);
    setTheme(next);
    window.localStorage.setItem("math-ai-lab-theme", next);
    applyTheme(next);
  }

  const label = theme === "light" ? "浅色" : theme === "dark" ? "深色" : "系统";

  return (
    <button
      type="button"
      onClick={cycle}
      className="rounded-lg border border-line px-2.5 py-1 text-sm text-ink hover:border-accent"
      aria-label={`主题：${label}，点击切换`}
    >
      {label}
    </button>
  );
}
