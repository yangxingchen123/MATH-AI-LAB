import { resolveContentRef } from "@math-ai-lab/domain";

const BARE_ID = /(?<![\w/])([KPM]\d{4})(?![\w-])/g;

export function routeForId(id: string): string | null {
  const resolved = resolveContentRef(id);
  return resolved.status === "ok" ? (resolved.href ?? null) : null;
}

export function rewriteMarkdownIdLinks(markdown: string): string {
  return markdown.replace(
    /\[([^\]]+)\]\(((?:K|P|M)\d{4})\)/g,
    (_, label: string, id: string) => {
      const resolved = resolveContentRef(id);
      if (resolved.status === "ok" && resolved.href) {
        return `[${label}](${resolved.href})`;
      }
      if (resolved.status === "broken") {
        return `<span class="broken-ref" data-ref="${id}" title="broken reference">${label}</span>`;
      }
      return `[${label}](${id})`;
    },
  );
}

export function autolinkIdsInMarkdown(
  markdown: string,
  catalog?: ReadonlySet<string>,
): string {
  return markdown.replace(BARE_ID, (id) => {
    const resolved = resolveContentRef(id, catalog);
    if (resolved.status === "ok" && resolved.href) {
      return `[${id}](${resolved.href})`;
    }
    if (resolved.status === "broken") {
      return `<span class="broken-ref" data-ref="${id}" title="broken reference">${id}</span>`;
    }
    return id;
  });
}
