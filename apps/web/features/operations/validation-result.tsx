import type { OperationResult } from "@math-ai-lab/domain";

const LABEL: Record<string, string> = {
  PASS: "PASS",
  WARNING: "WARNING",
  FAIL: "FAIL",
  NOT_RUN: "NOT_RUN",
};

export function ValidationResultView({ result }: { result: OperationResult }) {
  return (
    <div className="space-y-3 text-sm">
      <p>
        <span className="text-muted">operation</span> {result.operation}
        {result.preview ? " · preview" : " · persist"}
      </p>
      <p>
        <span className="text-muted">validation</span>{" "}
        <strong>{LABEL[result.validation] ?? result.validation}</strong>
        {result.success ? " · succeeded" : " · failed"}
      </p>
      {result.error ? <p className="text-[var(--danger)]">{result.error}</p> : null}
      {result.affected_objects.length > 0 ? (
        <p>
          <span className="text-muted">objects</span> {result.affected_objects.join(", ")}
        </p>
      ) : null}
      {result.changed_files.length > 0 ? (
        <div>
          <p className="text-muted">changed files</p>
          <ul className="mt-1 font-mono text-xs">
            {result.changed_files.map((file) => (
              <li key={file}>{file}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {result.warnings.length > 0 ? (
        <ul className="list-disc pl-5 text-muted">
          {result.warnings.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : null}
      {result.issues.length > 0 ? (
        <ul className="space-y-1">
          {result.issues.map((issue, index) => (
            <li key={`${issue.validator}-${index}`}>
              <span className="font-mono">{issue.level}</span> {issue.validator}: {issue.message}
              {issue.source_path ? (
                <span className="block font-mono text-xs text-muted">{issue.source_path}</span>
              ) : null}
            </li>
          ))}
        </ul>
      ) : null}
      {result.planned && Object.keys(result.planned).length > 0 ? (
        <pre className="overflow-x-auto border border-line bg-[var(--sidebar)] p-2 text-xs">
          {JSON.stringify(result.planned, null, 2)}
        </pre>
      ) : null}
    </div>
  );
}
