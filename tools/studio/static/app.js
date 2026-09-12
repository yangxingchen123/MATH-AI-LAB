const KIND_OF_NAV = {
  today: "today",
  problems: "problem",
  knowledge: "knowledge",
  methods: "method",
  project: "project",
  lab: "lab",
};

const TAB_LABEL = {
  today: "今日",
  problems: "题目",
  knowledge: "知识",
  methods: "方法",
  project: "项目",
  lab: "实验室",
};

const state = {
  catalog: null,
  nav: "problems",
  leaves: {
    today: "brief",
    problems: "P0002",
    knowledge: "K0001",
    methods: "M0002",
    project: "美赛2026-A",
    lab: "sf001-fallback",
  },
  query: "",
  mode: "AUTO",
  doc: null,
};

async function main() {
  state.catalog = await fetchJSON("/api/catalog");
  const firstLab = firstId(state.catalog.trees.lab);
  if (firstLab) state.leaves.lab = firstLab;
  const firstProject = firstId(state.catalog.trees.project);
  if (firstProject) state.leaves.project = firstProject;
  bindChrome();
  await openCurrent();
}

function firstId(groups) {
  for (const group of groups || []) {
    if (group.items && group.items[0]) return group.items[0].id;
  }
  return "";
}

function bindChrome() {
  document.querySelectorAll("#tabs button").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.nav = btn.dataset.nav;
      openCurrent();
    });
  });
  document.querySelectorAll("#modes button").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.mode = btn.dataset.mode;
      render();
    });
  });
  document.getElementById("search").addEventListener("input", (event) => {
    state.query = event.target.value;
    renderTree();
  });
}

async function openCurrent() {
  await loadDoc(state.nav, state.leaves[state.nav]);
  render();
}

async function loadDoc(nav, id) {
  const kind = KIND_OF_NAV[nav];
  state.doc = await fetchJSON(`/api/doc?kind=${encodeURIComponent(kind)}&id=${encodeURIComponent(id)}`);
}

async function fetchJSON(url) {
  const response = await fetch(url);
  if (!response.ok) return null;
  return response.json();
}

function render() {
  document.querySelectorAll("#tabs button").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.nav === state.nav);
  });
  document.querySelectorAll("#modes button").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.mode === state.mode);
  });
  renderTree();
  renderArticle();
  renderToc();
}

function renderTree() {
  const tree = document.getElementById("tree");
  const groups = state.catalog.trees[state.nav] || [];
  const q = state.query.trim().toLowerCase();
  const leaf = state.leaves[state.nav];
  let html = `<h2>${escapeHtml(TAB_LABEL[state.nav])}</h2>`;
  if (state.nav === "problems") {
    html += `<div class="hint">目录是工作流，不是 YAML status</div>`;
  }
  for (const group of groups) {
    const items = group.items.filter((item) => {
      if (!q) return true;
      return item.id.toLowerCase().includes(q) || item.title.toLowerCase().includes(q);
    });
    if (!items.length) continue;
    html += `<div class="group"><div class="label">${escapeHtml(group.label)}</div>`;
    for (const item of items) {
      const active = item.id === leaf ? " active" : "";
      html += `<button type="button" class="item${active}" data-id="${escapeAttr(item.id)}" data-jump="${escapeAttr(item.jump || "")}">
        <span class="id">${escapeHtml(item.id)}</span>
        <span class="title">${escapeHtml(item.title)}</span>
      </button>`;
    }
    html += "</div>";
  }
  tree.innerHTML = html;
  tree.querySelectorAll("button.item").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const jump = btn.dataset.jump;
      if (jump) {
        state.nav = jump;
        state.leaves[jump] = btn.dataset.id;
      } else {
        state.leaves[state.nav] = btn.dataset.id;
      }
      await openCurrent();
    });
  });
}

function renderArticle() {
  const root = document.getElementById("article");
  const doc = state.doc;
  if (!doc) {
    root.innerHTML = `<div class="article-inner"><p class="note">没有这篇对象。</p></div>`;
    return;
  }
  if (doc.kind === "draft") {
    root.innerHTML = draftForm();
    bindDraft();
    return;
  }
  const crumb = [TAB_LABEL[state.nav], doc.workflow_dir, doc.id].filter(Boolean).join(" / ");
  const meta = [
    doc.yaml_status ? `YAML ${doc.yaml_status}` : "",
    doc.workflow_dir ? `目录 ${doc.workflow_dir}` : "",
    doc.parts && doc.parts.length ? `parts ${doc.parts.join(" · ")}` : "",
    doc.kind_label || "",
  ]
    .filter(Boolean)
    .join(" · ");
  let banner = "";
  if (state.mode === "STUDY") {
    banner = `<div class="banner"><strong>STUDY</strong>正文是已有记录。独立 Attempt 请在对话里写，不要把 AI 解答记成你的 Attempt。</div>`;
  }
  root.innerHTML = `<div class="article-inner">
    <div class="crumb">${escapeHtml(crumb)}</div>
    <h1>${escapeHtml(doc.title)}</h1>
    <div class="meta">${escapeHtml(meta)}</div>
    ${banner}
    <div class="md">${renderMarkdown(doc.body || "", doc.headings || [])}</div>
  </div>`;
  typesetMath(root.querySelector(".md"));
}

function renderToc() {
  const toc = document.getElementById("toc");
  const doc = state.doc;
  if (!doc || doc.kind === "draft") {
    toc.innerHTML = `<h2>本页</h2><p class="note">先分流，再写题面。此界面不写入题库。</p>`;
    return;
  }
  const headings = doc.headings || [];
  let links = headings
    .map(
      (item) =>
        `<button type="button" class="toc-link" data-id="${escapeAttr(item.id)}">${escapeHtml(item.text)}</button>`,
    )
    .join("");
  if (!links) links = `<p class="note">这篇没有二级标题。</p>`;
  const protocol = doc.kind_label
    ? `<h2>种类</h2><p class="note">${escapeHtml(doc.kind_label)}。种类不写入 YAML。</p>`
    : "";
  const path = doc.path
    ? `<h2>源文件</h2><p class="note">${escapeHtml(doc.path)}</p><button type="button" id="copy-path">复制路径</button>`
    : "";
  toc.innerHTML = `<h2>本页</h2>${links}${protocol}${path}`;
  toc.querySelectorAll(".toc-link").forEach((btn) => {
    btn.addEventListener("click", () => {
      const target = document.getElementById(btn.dataset.id);
      if (!target) return;
      toc.querySelectorAll(".toc-link").forEach((node) => node.classList.remove("active"));
      btn.classList.add("active");
      target.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });
  const copy = document.getElementById("copy-path");
  if (copy) {
    copy.addEventListener("click", async () => {
      await navigator.clipboard.writeText(doc.path);
      copy.textContent = "已复制";
    });
  }
}

function draftForm() {
  return `<div class="article-inner draft">
    <div class="crumb">题目 / 起草</div>
    <h1>新题</h1>
    <div class="banner"><strong>只读界面</strong>先选种类。未说「加入题库」时只在对话里解答。这里不会写入 Source。</div>
    <label>种类分流</label>
    <select id="draft-kind">
      <option value="exercise">习题 / 定理 → 题目库</option>
      <option value="modeling">竞赛建模 → 07_项目 Dossier</option>
      <option value="literature">文献精读 → literature</option>
      <option value="experiment">计算实验 → 05_代码</option>
      <option value="review">批改原解 → REVIEW</option>
      <option value="infra">系统 / 运行条件 → 实验室</option>
    </select>
    <div id="draft-warn"></div>
    <div id="draft-fields"></div>
  </div>`;
}

function bindDraft() {
  const kind = document.getElementById("draft-kind");
  const warn = document.getElementById("draft-warn");
  const fields = document.getElementById("draft-fields");
  const paint = () => {
    const value = kind.value;
    warn.innerHTML = "";
    fields.innerHTML = "";
    if (value === "modeling") {
      warn.innerHTML = `<div class="banner"><strong>不要建成一道 P</strong>美赛 / 国赛整卷走 07_项目。</div>`;
      return;
    }
    if (value === "infra") {
      warn.innerHTML = `<div class="banner"><strong>infra 禁止新题</strong>先 operate，不要再写 P00xx。</div>`;
      return;
    }
    if (value !== "exercise") return;
    fields.innerHTML = `
      <label>标题</label>
      <input id="draft-title" placeholder="标题，例如：证明 …" />
      <label>题目</label>
      <textarea id="draft-body" placeholder="完整数学任务。有 (a)(b)(c) 时全部写出。"></textarea>
      <div class="actions">
        <button type="button" class="primary" id="copy-prompt">复制到剪贴板（对话里解答）</button>
      </div>
      <p class="note">id 不得用 P0000。空章节不要生成。加入题库请在 Cursor 里明确说。</p>`;
    document.getElementById("copy-prompt").addEventListener("click", async () => {
      const title = document.getElementById("draft-title").value.trim();
      const body = document.getElementById("draft-body").value.trim();
      const text = `请按 AUTO 解答这道题，只在对话里作答，不要加入题库。\n\n标题：${title}\n\n${body}`;
      await navigator.clipboard.writeText(text);
    });
  };
  kind.addEventListener("change", paint);
  paint();
}

function takeMath(src) {
  const slots = [];
  const hold = (display, tex) => {
    const index = slots.length;
    slots.push({ display, tex });
    return display ? `\n\n@@MATH${index}@@\n\n` : `@@MATH${index}@@`;
  };
  let text = String(src).replace(/\$\$([\s\S]+?)\$\$/g, (_, tex) => hold(true, tex));
  text = text.replace(/\$([^$\n]+?)\$/g, (_, tex) => hold(false, tex));
  return { text, slots };
}

function putMath(html, slots) {
  return html.replace(/@@MATH(\d+)@@/g, (_, raw) => {
    const slot = slots[Number(raw)];
    if (!slot) return "";
    const tex = escapeHtml(slot.tex);
    return slot.display ? `$$$${tex}$$` : `$${tex}$`;
  });
}

function typesetMath(node) {
  if (!node || typeof renderMathInElement !== "function") return;
  renderMathInElement(node, {
    delimiters: [
      { left: "$$", right: "$$", display: true },
      { left: "\\[", right: "\\]", display: true },
      { left: "$", right: "$", display: false },
      { left: "\\(", right: "\\)", display: false },
    ],
    throwOnError: false,
    ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"],
  });
}

function renderMarkdown(src, headings) {
  const pulled = takeMath(src);
  const escaped = escapeHtml(pulled.text).replace(/\r\n/g, "\n");
  const fences = [];
  let text = escaped.replace(/```([\s\S]*?)```/g, (_, code) => {
    const token = `@@FENCE${fences.length}@@`;
    fences.push(`<pre><code>${code.replace(/^\n/, "")}</code></pre>`);
    return token;
  });
  const h2 = (headings || []).filter((item) => item.level === 2);
  const h3 = (headings || []).filter((item) => item.level === 3);
  let h2i = 0;
  let h3i = 0;
  const blocks = text.split(/\n{2,}/);
  const html = blocks.map((block) => {
    const trimmed = block.trim();
    if (!trimmed) return "";
    const fence = trimmed.match(/^@@FENCE(\d+)@@$/);
    if (fence) return fences[Number(fence[1])];
    if (trimmed.startsWith("# ")) return `<h1>${inline(trimmed.slice(2))}</h1>`;
    if (trimmed.startsWith("## ")) {
      const meta = h2[h2i];
      h2i += 1;
      const id = meta ? meta.id : "";
      return `<h2 id="${escapeAttr(id)}">${inline(trimmed.slice(3))}</h2>`;
    }
    if (trimmed.startsWith("### ")) {
      const meta = h3[h3i];
      h3i += 1;
      const id = meta ? meta.id : "";
      return `<h3 id="${escapeAttr(id)}">${inline(trimmed.slice(4))}</h3>`;
    }
    if (trimmed.startsWith("&gt; ")) {
      return `<blockquote>${inline(trimmed.replace(/^(&gt; )/gm, ""))}</blockquote>`;
    }
    if (looksLikeTable(trimmed)) return renderTable(trimmed);
    if (/^[-*] /.test(trimmed)) {
      const items = trimmed.split("\n").map((line) => `<li>${inline(line.replace(/^[-*] /, ""))}</li>`);
      return `<ul>${items.join("")}</ul>`;
    }
    return `<p>${inline(trimmed).replace(/\n/g, "<br />")}</p>`;
  });
  return putMath(html.join("\n"), pulled.slots);
}

function looksLikeTable(block) {
  const lines = block.split("\n");
  return lines.length >= 2 && lines[0].includes("|") && /:?-+:?/.test(lines[1]);
}

function renderTable(block) {
  const lines = block.split("\n").filter((line) => line.trim() && !/^(\s*\|?\s*:?-+:?\s*\|)+/.test(line));
  if (!lines.length) return "";
  const cells = (line) =>
    line
      .replace(/^\||\|$/g, "")
      .split("|")
      .map((cell) => inline(cell.trim()));
  const header = cells(lines[0])
    .map((cell) => `<th>${cell}</th>`)
    .join("");
  const rows = lines
    .slice(1)
    .map((line) => `<tr>${cells(line).map((cell) => `<td>${cell}</td>`).join("")}</tr>`)
    .join("");
  return `<table><thead><tr>${header}</tr></thead><tbody>${rows}</tbody></table>`;
}

function inline(text) {
  return text
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(value) {
  return escapeHtml(value);
}

main();
