import katex from "katex";

export interface FormulaResult {
  ok: boolean;
  html: string;
  tex: string;
  display: boolean;
  error?: string;
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function errorHtml(tex: string, display: boolean, message: string): string {
  const tag = display ? "div" : "span";
  return `<${tag} class="math-error${display ? " math-error-display" : ""}" role="note">
  <span class="math-error-label">Formula rendering error</span>
  <button type="button" class="math-error-toggle" aria-expanded="false">查看源码</button>
  <pre class="math-error-src" hidden><code>${escapeHtml(tex)}</code></pre>
  <span class="math-error-msg">${escapeHtml(message)}</span>
</${tag}>`;
}

export function renderFormula(
  tex: string,
  display: boolean,
  closed = true,
): FormulaResult {
  const source = tex.trim();
  if (!closed) {
    warn(source, "Unclosed math delimiter");
    return {
      ok: false,
      html: errorHtml(source, display, "Unclosed math delimiter"),
      tex: source,
      display,
      error: "Unclosed math delimiter",
    };
  }
  try {
    const html = katex.renderToString(source, {
      throwOnError: true,
      displayMode: display,
      output: "html",
      trust: false,
      strict: "ignore",
    });
    const texAttr = escapeHtml(source);
    const wrapped = display
      ? `<div class="math-display" data-tex="${texAttr}"><div class="math-toolbar"><button type="button" class="math-copy" data-tex="${texAttr}">复制 LaTeX</button></div><div class="math-display-scroll">${html}</div></div>`
      : `<span class="math-inline" data-tex="${texAttr}">${html}</span>`;
    return { ok: true, html: wrapped, tex: source, display };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    warn(source, message);
    return {
      ok: false,
      html: errorHtml(source, display, message),
      tex: source,
      display,
      error: message,
    };
  }
}

function warn(tex: string, message: string): void {
  if (process.env.NODE_ENV !== "production") {
    console.warn("[math-renderer] Formula rendering error:", message, tex);
  }
}
