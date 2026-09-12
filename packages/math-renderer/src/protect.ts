export interface ProtectedText {
  text: string;
  bags: string[];
}

const FENCE = /```[\s\S]*?```/g;
const INLINE = /`[^`\n]+`/g;

export function protectCode(source: string): ProtectedText {
  const bags: string[] = [];
  const hold = (match: string): string => {
    const token = `@@CODE${bags.length}@@`;
    bags.push(match);
    return token;
  };
  const text = source.replace(FENCE, hold).replace(INLINE, hold);
  return { text, bags };
}

export function restoreCode(html: string, bags: string[]): string {
  return html.replace(/(?:<p>)?@@CODE(\d+)@@(?:<\/p>)?/g, (_, raw: string) => {
    const original = bags[Number(raw)];
    return original ? codeToHtml(original) : "";
  });
}

function codeToHtml(raw: string): string {
  if (raw.startsWith("```")) {
    const match = raw.match(/^```([^\n]*)\n?([\s\S]*?)```$/);
    const lang = match?.[1]?.trim() ?? "";
    const body = match?.[2] ?? "";
    const cls = lang ? ` class="language-${escapeHtml(lang)}"` : "";
    return `<pre><code${cls}>${escapeHtml(body)}</code></pre>`;
  }
  return `<code>${escapeHtml(raw.slice(1, -1))}</code>`;
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
