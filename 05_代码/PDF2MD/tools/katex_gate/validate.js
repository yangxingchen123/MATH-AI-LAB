"use strict";

const readline = require("readline");

let katex;
try {
  katex = require("katex");
} catch (err) {
  process.stderr.write("katex_not_installed\n");
  process.exit(2);
}

function check(tex, display) {
  try {
    katex.renderToString(String(tex || ""), {
      throwOnError: true,
      displayMode: Boolean(display),
      strict: "ignore",
      trust: false,
    });
    return { ok: true, error: "" };
  } catch (e) {
    return { ok: false, error: String((e && e.message) || e) };
  }
}

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
rl.on("line", (line) => {
  const raw = String(line || "").trim();
  if (!raw) {
    return;
  }
  let req;
  try {
    req = JSON.parse(raw);
  } catch {
    process.stdout.write(JSON.stringify({ id: null, ok: false, error: "bad_json" }) + "\n");
    return;
  }
  if (Array.isArray(req.batch)) {
    const results = req.batch.map((item) => {
      const r = check(item && item.tex, item && item.display);
      return { id: item && item.id, ok: r.ok, error: r.error };
    });
    process.stdout.write(JSON.stringify({ results }) + "\n");
    return;
  }
  const r = check(req.tex, req.display);
  process.stdout.write(JSON.stringify({ id: req.id, ok: r.ok, error: r.error }) + "\n");
});
