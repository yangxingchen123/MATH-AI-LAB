"use client";

import { renderDocument } from "@math-ai-lab/math-renderer";
import { useEffect, useMemo, useRef } from "react";
import { useToc } from "../features/shell/toc-context";

export function MarkdownView({
  source,
  syncToc = true,
  knownIds,
}: {
  source: string;
  syncToc?: boolean;
  knownIds?: string[];
}) {
  const rendered = useMemo(
    () => renderDocument(source, { knownIds }),
    [source, knownIds],
  );
  const { setHeadings } = useToc();
  const root = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!syncToc) return;
    setHeadings(rendered.headings);
    return () => setHeadings([]);
  }, [rendered.headings, setHeadings, syncToc]);

  useEffect(() => {
    const node = root.current;
    if (!node) return;

    const onToggle = (event: Event) => {
      const button = event.currentTarget as HTMLButtonElement;
      const src = button.parentElement?.querySelector(".math-error-src");
      if (!src) return;
      const hidden = src.hasAttribute("hidden");
      if (hidden) src.removeAttribute("hidden");
      else src.setAttribute("hidden", "");
      button.setAttribute("aria-expanded", hidden ? "true" : "false");
    };

    const onCopy = async (event: Event) => {
      const button = event.currentTarget as HTMLButtonElement;
      const tex = button.getAttribute("data-tex") || button.getAttribute("data-code") || "";
      if (!tex) return;
      await navigator.clipboard.writeText(tex);
      const prev = button.textContent;
      button.textContent = "已复制";
      window.setTimeout(() => {
        button.textContent = prev;
      }, 1000);
    };

    const errorButtons = node.querySelectorAll<HTMLButtonElement>(".math-error-toggle");
    const copyButtons = node.querySelectorAll<HTMLButtonElement>(".math-copy");
    errorButtons.forEach((button) => button.addEventListener("click", onToggle));
    copyButtons.forEach((button) => button.addEventListener("click", onCopy));

    const pres = node.querySelectorAll("pre");
    const added: HTMLButtonElement[] = [];
    pres.forEach((pre) => {
      if (pre.querySelector(".code-copy")) return;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "code-copy";
      button.textContent = "复制代码";
      button.setAttribute("data-code", pre.textContent ?? "");
      pre.prepend(button);
      button.addEventListener("click", onCopy);
      added.push(button);
    });

    return () => {
      errorButtons.forEach((button) => button.removeEventListener("click", onToggle));
      copyButtons.forEach((button) => button.removeEventListener("click", onCopy));
      added.forEach((button) => button.removeEventListener("click", onCopy));
    };
  }, [rendered.html]);

  return (
    <div
      ref={root}
      className="markdown-body"
      dangerouslySetInnerHTML={{ __html: rendered.html }}
    />
  );
}
