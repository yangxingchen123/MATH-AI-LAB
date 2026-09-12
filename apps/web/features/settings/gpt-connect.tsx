"use client";

import { useEffect, useMemo, useState } from "react";
import { AI_STORAGE_KEY, modelsFor, parseAiPrefs } from "../../src/lib/ai-models";
import { SettingsCard, StatusBadge } from "./settings-card";

type GptStatus = {
  ok?: boolean;
  connected?: boolean;
  model?: string;
  base_url?: string;
  key_source?: string;
  error?: string;
};

type ChatLine = { who: "you" | "gpt"; text: string };

async function callGpt(payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  const response = await fetch("/api/gpt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  try {
    return (await response.json()) as Record<string, unknown>;
  } catch {
    return { ok: false, error: "无法解析 GPT 接口返回" };
  }
}

export function GptConnect() {
  const models = useMemo(() => modelsFor("openai"), []);
  const [model, setModel] = useState(models[0]?.id || "gpt-4.1");
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("https://api.openai.com/v1");
  const [status, setStatus] = useState("正在读取本机状态…");
  const [tone, setTone] = useState<"ok" | "idle" | "err">("idle");
  const [connected, setConnected] = useState(false);
  const [busy, setBusy] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [lines, setLines] = useState<ChatLine[]>([]);
  const [history, setHistory] = useState<{ role: string; content: string }[]>([]);

  useEffect(() => {
    let cancelled = false;
    callGpt({ action: "status" }).then((result) => {
      if (cancelled) return;
      const data = result as GptStatus;
      if (typeof data.model === "string" && data.model) setModel(data.model);
      if (typeof data.base_url === "string" && data.base_url) setBaseUrl(data.base_url);
      if (data.connected) {
        const source =
          data.key_source === "env" ? "环境变量 OPENAI_API_KEY" : "本机已保存密钥";
        setConnected(true);
        setTone("ok");
        setStatus(`已接入 ${data.model || ""} · ${source}`);
      } else {
        setConnected(false);
        setTone("idle");
        setStatus("填写 API Key 后接入");
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  async function connect() {
    setBusy(true);
    const result = (await callGpt({
      action: "connect",
      model,
      api_key: apiKey,
      base_url: baseUrl,
    })) as GptStatus;
    setBusy(false);
    if (result.ok) {
      setApiKey("");
      setConnected(true);
      setTone("ok");
      setStatus(`已接入 ${result.model || model}`);
      try {
        window.localStorage.setItem(
          AI_STORAGE_KEY,
          JSON.stringify(
            parseAiPrefs({
              provider: "openai",
              model: result.model || model,
              custom_model: "",
            }),
          ),
        );
      } catch {
        /* browser preference is optional */
      }
      return;
    }
    setConnected(false);
    setTone("err");
    setStatus(String(result.error || "接入失败"));
  }

  async function send() {
    const text = prompt.trim();
    if (!text || busy) return;
    setPrompt("");
    setLines((current) => [...current, { who: "you", text }]);
    const prior = history;
    setHistory((current) => [...current, { role: "user", content: text }]);
    setBusy(true);
    const result = await callGpt({
      action: "chat",
      model,
      message: text,
      history: prior,
    });
    setBusy(false);
    if (result.ok === true && typeof result.text === "string") {
      const reply = result.text;
      setLines((current) => [...current, { who: "gpt", text: reply }]);
      setHistory((current) => [...current, { role: "assistant", content: reply }]);
      setStatus(`已回复 · ${String(result.model || model)}`);
      return;
    }
    setTone("err");
    setStatus(String(result.error || "发送失败"));
  }

  return (
    <>
      <SettingsCard
        kicker="连接"
        title="接入 GPT"
        extra={<StatusBadge tone={tone}>{connected ? "已接入" : tone === "err" ? "失败" : "未接入"}</StatusBadge>}
      >
        <p className="mt-2 text-sm text-muted">
          密钥经本机 Python 写入 <code>.mathailab/credentials.json</code>。网页只允许 localhost。
        </p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <label className="text-sm">
            <span className="mb-1 block text-xs font-semibold text-muted">GPT 模型</span>
            <select className="field-input" value={model} onChange={(event) => setModel(event.target.value)}>
              {models.map((row) => (
                <option key={row.id} value={row.id}>
                  {row.label}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm">
            <span className="mb-1 block text-xs font-semibold text-muted">Base URL</span>
            <input
              className="field-input"
              value={baseUrl}
              onChange={(event) => setBaseUrl(event.target.value)}
              placeholder="https://api.openai.com/v1"
            />
          </label>
        </div>
        <label className="mt-3 block text-sm">
          <span className="mb-1 block text-xs font-semibold text-muted">OpenAI API Key</span>
          <input
            type="password"
            className="field-input"
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
            placeholder="粘贴 sk- 开头的密钥"
            autoComplete="off"
          />
        </label>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button
            type="button"
            className="rounded-lg bg-accent px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
            disabled={busy}
            onClick={() => void connect()}
          >
            {busy ? "处理中…" : "接入 GPT"}
          </button>
          <p className={`text-sm ${tone === "err" ? "text-danger" : "text-muted"}`}>{status}</p>
        </div>
      </SettingsCard>

      <SettingsCard kicker="对话" title="GPT">
        <p className="mt-2 text-sm text-muted">发送内容只走本机 sidecar，不写正式 Source。</p>
        <div className="chat-log mt-4">
          {lines.length === 0 ? (
            <span className="text-sm text-muted">接入后在这里对话。</span>
          ) : (
            lines.map((line, index) => (
              <p key={`${line.who}-${index}`} className="chat-line">
                <span className="chat-who">{line.who === "you" ? "你" : "GPT"}</span>
                {line.text}
              </p>
            ))
          )}
        </div>
        <div className="composer">
          <input
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void send();
              }
            }}
            placeholder="问 GPT…"
          />
          <button
            type="button"
            className="rounded-lg bg-accent px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
            disabled={busy}
            onClick={() => void send()}
          >
            发送
          </button>
        </div>
      </SettingsCard>
    </>
  );
}
