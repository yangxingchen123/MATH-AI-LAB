const KIND_MAP: Record<string, string> = {
  定义: "definition",
  定理: "theorem",
  引理: "lemma",
  命题: "proposition",
  推论: "corollary",
  证明: "proof",
  例: "example",
  例子: "example",
  注: "remark",
  备注: "remark",
  猜想: "conjecture",
  警告: "warning",
  Definition: "definition",
  Theorem: "theorem",
  Lemma: "lemma",
  Proposition: "proposition",
  Corollary: "corollary",
  Proof: "proof",
  Example: "example",
  Remark: "remark",
  Conjecture: "conjecture",
  Warning: "warning",
};

const MARKER =
  /^(定义|定理|引理|命题|推论|证明|例子|例|备注|注|猜想|警告|Definition|Theorem|Lemma|Proposition|Corollary|Proof|Example|Remark|Conjecture|Warning)([.。:：]|\s)/;

/**
 * Only enhance paragraphs that clearly start with a semantic marker.
 * Ordinary Markdown is left untouched.
 */
export function enhanceSemanticBlocks(markdown: string): string {
  const lines = markdown.split(/\n/);
  const out: string[] = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const plain = line.replace(/^\*\*|\*\*$/g, "").replace(/^\*\s+/, "");
    const match = plain.match(MARKER);
    if (!match || line.startsWith("```") || line.startsWith("#")) {
      out.push(line);
      i += 1;
      continue;
    }
    const label = match[1];
    const kind = KIND_MAP[label] ?? "remark";
    const block: string[] = [line];
    i += 1;
    while (i < lines.length && lines[i].trim() !== "" && !lines[i].startsWith("#")) {
      block.push(lines[i]);
      i += 1;
    }
    const inner = block.join("\n");
    if (kind === "proof") {
      out.push(
        `<details class="math-block math-proof" open><summary>${escape(label)}</summary>\n\n${inner}\n\n</details>`,
      );
    } else {
      out.push(
        `<div class="math-block math-${kind}" data-kind="${kind}"><p class="math-block-label">${escape(label)}</p>\n\n${inner}\n\n</div>`,
      );
    }
  }
  return out.join("\n");
}

function escape(value: string): string {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
