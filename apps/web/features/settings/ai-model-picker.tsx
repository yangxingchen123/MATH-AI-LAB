"use client";

import { useEffect, useMemo, useState } from "react";
import {
  AI_PROVIDERS,
  AI_STORAGE_KEY,
  DEFAULT_AI_PREFS,
  modelsFor,
  parseAiPrefs,
  selectionLabel,
  type AiModelPrefs,
} from "../../src/lib/ai-models";
import { SettingsCard } from "./settings-card";

function readPrefs(): AiModelPrefs {
  if (typeof window === "undefined") return { ...DEFAULT_AI_PREFS };
  try {
    const raw = window.localStorage.getItem(AI_STORAGE_KEY);
    return parseAiPrefs(raw ? JSON.parse(raw) : null);
  } catch {
    return { ...DEFAULT_AI_PREFS };
  }
}

function writePrefs(prefs: AiModelPrefs) {
  window.localStorage.setItem(AI_STORAGE_KEY, JSON.stringify(prefs));
}

export function AiModelPicker() {
  const [prefs, setPrefs] = useState<AiModelPrefs>(DEFAULT_AI_PREFS);

  useEffect(() => {
    setPrefs(readPrefs());
  }, []);

  const models = useMemo(() => modelsFor(prefs.provider), [prefs.provider]);

  function update(next: AiModelPrefs) {
    setPrefs(next);
    writePrefs(next);
  }

  return (
    <SettingsCard
      kicker="偏好"
      title="模型"
      extra={<span className="text-sm text-muted">{selectionLabel(prefs)}</span>}
    >
      <p className="mt-2 text-sm text-muted">
        保存在本浏览器。桌面顶栏写在 <code>.mathailab/</code>，两边不自动同步。要真正调用 GPT，用下一张卡片。
      </p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <label className="text-sm">
          <span className="mb-1 block text-xs font-semibold text-muted">提供方</span>
          <select
            className="field-input"
            value={prefs.provider}
            onChange={(event) => {
              const provider = event.target.value as AiModelPrefs["provider"];
              const first = modelsFor(provider)[0]?.id || "";
              update({
                provider,
                model: provider === "custom" ? "" : first,
                custom_model: provider === "custom" ? prefs.custom_model : "",
              });
            }}
          >
            {AI_PROVIDERS.map((row) => (
              <option key={row.id} value={row.id}>
                {row.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-xs font-semibold text-muted">模型</span>
          <select
            className="field-input disabled:opacity-50"
            value={prefs.model}
            disabled={prefs.provider === "custom"}
            onChange={(event) => update({ ...prefs, model: event.target.value })}
          >
            {models.length === 0 ? (
              <option value="">使用自定义名称</option>
            ) : (
              models.map((row) => (
                <option key={row.id} value={row.id}>
                  {row.label}
                </option>
              ))
            )}
          </select>
        </label>
      </div>
      {prefs.provider === "custom" ? (
        <label className="mt-3 block text-sm">
          <span className="mb-1 block text-xs font-semibold text-muted">自定义模型名</span>
          <input
            className="field-input"
            value={prefs.custom_model}
            onChange={(event) => update({ ...prefs, custom_model: event.target.value })}
            placeholder="llama3.1:70b"
          />
        </label>
      ) : null}
    </SettingsCard>
  );
}
