import { Marked } from "marked";
import { extractHeadings, slugify, type Heading } from "./headings.ts";

export function renderMarkdown(markdown: string, headings: Heading[]): string {
  const used = new Map<string, number>();
  const queue = headings.slice();
  const marked = new Marked({
    gfm: true,
    breaks: false,
    renderer: {
      heading({ tokens, depth }: { tokens: unknown; depth: number }) {
        const text = this.parser.parseInline(tokens as never);
        const plain = queue.shift()?.id ?? slugify(stripTags(text), used);
        return `<h${depth} id="${escapeAttr(plain)}"><a class="heading-anchor" href="#${escapeAttr(plain)}" aria-label="链接到此标题">#</a>${text}</h${depth}>\n`;
      },
    },
  });
  return marked.parse(markdown, { async: false }) as string;
}

function stripTags(html: string): string {
  return html.replace(/<[^>]+>/g, "");
}

function escapeAttr(value: string): string {
  return value.replace(/"/g, "&quot;");
}

export { extractHeadings };
export type { Heading };
