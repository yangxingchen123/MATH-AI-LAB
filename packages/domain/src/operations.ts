/** Projection of tools/ui_operations contract v1. Not Frozen Schema. */

export const OPERATION_CONTRACT_VERSION = 1;

export const DOMAIN_OPERATIONS = [
  "RecordAttempt",
  "MoveProblemWorkflow",
  "CreateProblem",
  "CreateKnowledge",
  "CreateMethod",
  "PromoteInboxItem",
  "UpdateMarkdownBody",
] as const;

export type DomainOperation = (typeof DOMAIN_OPERATIONS)[number];

export interface OperationRequest {
  version: 1;
  operation: DomainOperation;
  preview: boolean;
  requestId: string;
  payload: Record<string, unknown>;
}

export interface ValidationItem {
  level: string;
  validator: string;
  message: string;
  source_path?: string | null;
}

export interface OperationResult {
  version: number;
  success: boolean;
  operation: string;
  preview: boolean;
  request_id: string;
  affected_objects: string[];
  validation: "PASS" | "WARNING" | "FAIL" | "NOT_RUN" | string;
  warnings: string[];
  changed_files: string[];
  created_artifacts: string[];
  planned: Record<string, unknown>;
  issues: ValidationItem[];
  error?: string | null;
}

export function isDomainOperation(value: string): value is DomainOperation {
  return (DOMAIN_OPERATIONS as readonly string[]).includes(value);
}
