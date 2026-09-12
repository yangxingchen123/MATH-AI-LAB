"use client";

import { useState } from "react";

function firstSumWitness(values: Set<number>): [number, number, number] | null {
  const items = [...values];
  for (let i = 0; i < items.length; i += 1) {
    for (let j = i; j < items.length; j += 1) {
      const left = items[i]!;
      const right = items[j]!;
      const total = left + right;
      if (values.has(total)) return [left, right, total];
    }
  }
  return null;
}

function evaluateCandidate(n: number, values: Set<number>) {
  const universe = new Set(Array.from({ length: n }, (_, i) => i + 1));
  for (const value of values) {
    if (!universe.has(value)) {
      return { valid: false, reason: "out_of_universe", size: values.size };
    }
  }
  const witness = firstSumWitness(values);
  if (witness) {
    return { valid: false, reason: "not_sum_free", size: values.size, witness };
  }
  const bound = Math.floor((n + 1) / 2);
  return {
    valid: true,
    reason: "sum_free",
    size: values.size,
    bound,
    optimal: values.size === bound,
  };
}

export function SumFreePanel() {
  const [n, setN] = useState("10");
  const [raw, setRaw] = useState("6,7,8,9,10");
  const [out, setOut] = useState("");

  function onEvaluate() {
    const size = Number(n);
    if (!Number.isInteger(size) || size < 0 || size > 40) {
      setOut("n 必须是 0–40 的整数。");
      return;
    }
    try {
      const values = new Set(
        raw
          .replace(/，/g, ",")
          .split(",")
          .map((item) => item.trim())
          .filter(Boolean)
          .map((item) => Number(item))
          .map((item) => {
            if (!Number.isInteger(item)) throw new Error("not int");
            return item;
          }),
      );
      const report = {
        ...evaluateCandidate(size, values),
        wrote_canonical: false,
        not_a_theorem: true,
      };
      setOut(JSON.stringify(report, null, 2));
    } catch {
      setOut("集合必须是逗号分隔的整数。");
    }
  }

  return (
    <section className="mt-10 border-t border-line pt-6">
      <h2 className="text-lg font-semibold">sum-free 评估</h2>
      <p className="mt-1 text-sm text-muted">已知答案校准，不是新定理。不写 Canonical。</p>
      <div className="mt-3 flex flex-wrap gap-3 text-sm">
        <label>
          <span className="text-muted">n</span>
          <input
            className="ml-2 w-20 border border-line bg-canvas px-2 py-1"
            value={n}
            onChange={(event) => setN(event.target.value)}
          />
        </label>
        <label className="min-w-[16rem] flex-1">
          <span className="text-muted">集合</span>
          <input
            className="ml-2 w-[calc(100%-3rem)] border border-line bg-canvas px-2 py-1"
            value={raw}
            onChange={(event) => setRaw(event.target.value)}
          />
        </label>
        <button type="button" className="rounded border border-accent px-3 py-1.5" onClick={onEvaluate}>
          评估
        </button>
      </div>
      {out ? (
        <pre className="mt-3 overflow-x-auto whitespace-pre-wrap border border-line bg-[var(--sidebar)] p-3 text-sm">
          {out}
        </pre>
      ) : null}
    </section>
  );
}
