export interface Heading {
  id: string;
  level: number;
  text: string;
}

const HEADING_RE = /^(#{1,6})\s+(.+?)\s*$/gm;
const SLUG_RE = /[^\w\u4e00-\u9fff\-、．.]+/gu;

export function slugify(text: string, used: Map<string, number>): string {
  const cleaned = text
    .replace(/<[^>]+>/g, "")
    .replace(/[*_`]/g, "")
    .replace(SLUG_RE, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
  const base = cleaned || "section";
  const count = (used.get(base) ?? 0) + 1;
  used.set(base, count);
  return count === 1 ? base : `${base}-${count}`;
}

export function extractHeadings(markdown: string): Heading[] {
  const used = new Map<string, number>();
  const headings: Heading[] = [];
  for (const match of markdown.matchAll(HEADING_RE)) {
    const level = match[1].length;
    const text = match[2]
      .replace(/@@MATH\d+@@/g, "")
      .replace(/[*_`]/g, "")
      .trim();
    headings.push({ id: slugify(text, used), level, text });
  }
  return headings;
}
