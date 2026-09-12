import { spawnSync } from "node:child_process";
import { DOMAIN_OPERATIONS, type DomainOperation, type OperationResult } from "@math-ai-lab/domain";
import { resolveRepoRoot } from "@math-ai-lab/content";

const ALLOWED = new Set<string>(DOMAIN_OPERATIONS);

function pythonInvocation(): string[] {
  const probe = spawnSync("python", ["-c", "print(1)"], { encoding: "utf8", timeout: 8000 });
  if (probe.status === 0) {
    return ["python"];
  }
  const py = spawnSync("py", ["-3", "-c", "print(1)"], { encoding: "utf8", timeout: 8000 });
  if (py.status === 0) {
    return ["py", "-3"];
  }
  return [];
}

export function operationHealth(): {
  available: boolean;
  detail: string;
  operations: string[];
} {
  const cmd = pythonInvocation();
  if (cmd.length === 0) {
    return { available: false, detail: "Python unavailable", operations: [] };
  }
  const root = resolveRepoRoot();
  const result = spawnSync(
    cmd[0],
    [...cmd.slice(1), "-m", "tools.ui_operations", "doctor"],
    { encoding: "utf8", timeout: 15000, cwd: root },
  );
  if (result.status !== 0) {
    return {
      available: false,
      detail: (result.stderr || result.stdout || "doctor failed").trim().slice(0, 240),
      operations: [],
    };
  }
  try {
    const data = JSON.parse(result.stdout) as { operations?: string[] };
    return {
      available: true,
      detail: "tools.ui_operations",
      operations: data.operations ?? [],
    };
  } catch {
    return { available: false, detail: "doctor JSON parse failed", operations: [] };
  }
}

export function runDomainOperation(input: {
  operation: string;
  preview: boolean;
  requestId: string;
  payload: Record<string, unknown>;
}): OperationResult {
  if (!ALLOWED.has(input.operation)) {
    return {
      version: 1,
      success: false,
      operation: input.operation,
      preview: input.preview,
      request_id: input.requestId,
      affected_objects: [],
      validation: "FAIL",
      warnings: [],
      changed_files: [],
      created_artifacts: [],
      planned: {},
      issues: [],
      error: "operation is not on the whitelist",
    };
  }
  const cmd = pythonInvocation();
  if (cmd.length === 0) {
    return {
      version: 1,
      success: false,
      operation: input.operation,
      preview: input.preview,
      request_id: input.requestId,
      affected_objects: [],
      validation: "FAIL",
      warnings: [],
      changed_files: [],
      created_artifacts: [],
      planned: {},
      issues: [],
      error: "Write operations unavailable: Python not found",
    };
  }
  const root = resolveRepoRoot();
  const request = {
    version: 1,
    operation: input.operation as DomainOperation,
    preview: input.preview,
    requestId: input.requestId,
    payload: input.payload,
  };
  const result = spawnSync(
    cmd[0],
    [...cmd.slice(1), "-m", "tools.ui_operations", "run", "--root", root],
    {
      encoding: "utf8",
      timeout: 60000,
      cwd: root,
      input: JSON.stringify(request),
    },
  );
  if (!result.stdout.trim()) {
    return {
      version: 1,
      success: false,
      operation: input.operation,
      preview: input.preview,
      request_id: input.requestId,
      affected_objects: [],
      validation: "FAIL",
      warnings: [],
      changed_files: [],
      created_artifacts: [],
      planned: {},
      issues: [],
      error: (result.stderr || "Python gateway returned no JSON").trim().slice(0, 400),
    };
  }
  return JSON.parse(result.stdout) as OperationResult;
}

export const GPT_ACTIONS = ["status", "connect", "chat"] as const;
export type GptAction = (typeof GPT_ACTIONS)[number];

export function isGptAction(value: string): value is GptAction {
  return (GPT_ACTIONS as readonly string[]).includes(value);
}

function gptError(message: string): Record<string, unknown> {
  return { ok: false, error: message };
}

export function runGptCommand(payload: Record<string, unknown>): Record<string, unknown> {
  const action = typeof payload.action === "string" ? payload.action : "";
  if (!isGptAction(action)) {
    return gptError("未知操作。可用：status / connect / chat");
  }
  const request: Record<string, unknown> = { action };
  if (typeof payload.model === "string") request.model = payload.model;
  if (typeof payload.message === "string") request.message = payload.message;
  if (typeof payload.api_key === "string") request.api_key = payload.api_key;
  else if (typeof payload.apiKey === "string") request.api_key = payload.apiKey;
  if (typeof payload.base_url === "string") request.base_url = payload.base_url;
  else if (typeof payload.baseUrl === "string") request.base_url = payload.baseUrl;
  if (Array.isArray(payload.history)) request.history = payload.history;

  const cmd = pythonInvocation();
  if (cmd.length === 0) {
    return gptError("找不到 Python，无法接入 GPT。");
  }
  const root = resolveRepoRoot();
  const result = spawnSync(cmd[0], [...cmd.slice(1), "-m", "tools.qt_workbench", "gpt"], {
    encoding: "utf8",
    timeout: action === "chat" ? 120000 : 30000,
    cwd: root,
    input: JSON.stringify(request),
  });
  const stdout = (result.stdout || "").trim();
  if (!stdout) {
    return gptError((result.stderr || "Python GPT sidecar 没有返回 JSON").trim().slice(0, 400));
  }
  try {
    const parsed = JSON.parse(stdout) as Record<string, unknown>;
    return parsed;
  } catch {
    return gptError("Python GPT sidecar 返回了无法解析的内容");
  }
}

export function isLocalOrigin(origin: string | null): boolean {
  if (!origin) return true;
  return /^https?:\/\/(127\.0\.0\.1|localhost|\[::1\])(:\d+)?$/i.test(origin);
}
