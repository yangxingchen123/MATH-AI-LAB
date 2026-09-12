import { extractMath } from "./extract.ts";
import { renderFormula, type FormulaResult } from "./formula.ts";
import { extractHeadings, type Heading } from "./headings.ts";
import { autolinkIdsInMarkdown, rewriteMarkdownIdLinks } from "./links.ts";
import { renderMarkdown } from "./markdown.ts";
import { protectCode, restoreCode } from "./protect.ts";
import { enhanceSemanticBlocks } from "./semantic.ts";

export interface RenderOptions {
  knownIds?: Iterable<string>;
}

export interface RenderedDocument {
  html: string;
  headings: Heading[];
  formulas: FormulaResult[];
}

export function renderDocument(
  source: string,
  options: RenderOptions = {},
): RenderedDocument {
  const catalog = options.knownIds ? new Set(options.knownIds) : undefined;
  const protectedSource = protectCode(source);
  let working = rewriteMarkdownIdLinks(protectedSource.text);
  working = autolinkIdsInMarkdown(working, catalog);
  working = enhanceSemanticBlocks(working);
  const extracted = extractMath(working);
  const headings = extractHeadings(extracted.text);
  let html = renderMarkdown(extracted.text, headings);
  html = restoreCode(html, protectedSource.bags);

  const formulas = extracted.slots.map((slot) =>
    renderFormula(slot.tex, slot.display, slot.closed),
  );
  html = html.replace(/@@MATH(\d+)@@/g, (_, raw: string) => {
    const formula = formulas[Number(raw)];
    return formula?.html ?? "";
  });

  return { html, headings, formulas };
}
