import type { DomainOperation, OperationResult } from "@math-ai-lab/domain";

export async function submitOperation(input: {
  operation: DomainOperation;
  preview: boolean;
  payload: Record<string, unknown>;
}): Promise<OperationResult> {
  const response = await fetch("/api/operations", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      version: 1,
      operation: input.operation,
      preview: input.preview,
      requestId: crypto.randomUUID(),
      payload: input.payload,
    }),
  });
  const data = (await response.json()) as OperationResult | { error?: string };
  if ("operation" in data && "success" in data) {
    return data;
  }
  return {
    version: 1,
    success: false,
    operation: input.operation,
    preview: input.preview,
    request_id: "",
    affected_objects: [],
    validation: "FAIL",
    warnings: [],
    changed_files: [],
    created_artifacts: [],
    planned: {},
    issues: [],
    error: "error" in data ? data.error : `HTTP ${response.status}`,
  };
}
