export type AiProviderId =
  | "cursor"
  | "openai"
  | "anthropic"
  | "xai"
  | "google"
  | "ollama"
  | "custom";

export interface AiModelOption {
  id: string;
  label: string;
}

export interface AiProviderOption {
  id: AiProviderId;
  label: string;
  models: AiModelOption[];
}

export interface AiModelPrefs {
  provider: AiProviderId;
  model: string;
  custom_model: string;
}

export const AI_STORAGE_KEY = "math-ai-lab-ai-model";

export const AI_PROVIDERS: AiProviderOption[] = [
  {
    id: "cursor",
    label: "Cursor",
    models: [
      { id: "auto", label: "Auto" },
      { id: "grok-4.6", label: "Grok 4.6" },
      { id: "composer-2", label: "Composer" },
      { id: "gpt-5.2", label: "GPT-5.2" },
      { id: "claude-4.6-sonnet", label: "Claude Sonnet 4.6" },
      { id: "claude-4.6-opus", label: "Claude Opus 4.6" },
    ],
  },
  {
    id: "openai",
    label: "GPT（OpenAI）",
    models: [
      { id: "gpt-4.1", label: "GPT-4.1" },
      { id: "gpt-4o", label: "GPT-4o" },
      { id: "gpt-4o-mini", label: "GPT-4o mini" },
      { id: "gpt-5.2", label: "GPT-5.2" },
      { id: "o3", label: "o3" },
    ],
  },
  {
    id: "anthropic",
    label: "Anthropic",
    models: [
      { id: "claude-opus-4.6", label: "Claude Opus 4.6" },
      { id: "claude-sonnet-4.6", label: "Claude Sonnet 4.6" },
    ],
  },
  {
    id: "xai",
    label: "xAI",
    models: [
      { id: "grok-4.6", label: "Grok 4.6" },
      { id: "grok-4", label: "Grok 4" },
    ],
  },
  {
    id: "google",
    label: "Google",
    models: [
      { id: "gemini-2.5-pro", label: "Gemini 2.5 Pro" },
      { id: "gemini-2.5-flash", label: "Gemini 2.5 Flash" },
    ],
  },
  {
    id: "ollama",
    label: "本机 Ollama",
    models: [
      { id: "llama3.1", label: "Llama 3.1" },
      { id: "qwen2.5", label: "Qwen 2.5" },
      { id: "deepseek-r1", label: "DeepSeek R1" },
    ],
  },
  { id: "custom", label: "自定义", models: [] },
];

export const DEFAULT_AI_PREFS: AiModelPrefs = {
  provider: "cursor",
  model: "auto",
  custom_model: "",
};

export function modelsFor(provider: string): AiModelOption[] {
  return AI_PROVIDERS.find((row) => row.id === provider)?.models ?? [];
}

export function parseAiPrefs(raw: unknown): AiModelPrefs {
  if (!raw || typeof raw !== "object") return { ...DEFAULT_AI_PREFS };
  const data = raw as Record<string, unknown>;
  const provider = AI_PROVIDERS.some((row) => row.id === data.provider)
    ? (data.provider as AiProviderId)
    : DEFAULT_AI_PREFS.provider;
  const allowed = modelsFor(provider).map((row) => row.id);
  if (provider === "custom") {
    const custom = String(data.custom_model || data.model || "").trim();
    return { provider, model: "", custom_model: custom };
  }
  const model =
    typeof data.model === "string" && allowed.includes(data.model)
      ? data.model
      : allowed[0] || DEFAULT_AI_PREFS.model;
  return { provider, model, custom_model: "" };
}

export function selectionLabel(prefs: AiModelPrefs): string {
  const provider = AI_PROVIDERS.find((row) => row.id === prefs.provider);
  if (!provider) return "Cursor · Auto";
  if (provider.id === "custom") {
    return `自定义 · ${prefs.custom_model || "未填写"}`;
  }
  const model = provider.models.find((row) => row.id === prefs.model);
  return `${provider.label} · ${model?.label || prefs.model}`;
}
