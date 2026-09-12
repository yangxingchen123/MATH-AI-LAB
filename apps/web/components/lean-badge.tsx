import type { LeanVerifyStatus } from "@math-ai-lab/domain";

const LABEL: Record<LeanVerifyStatus, string> = {
  not_formalized: "未形式化",
  source_exists: "源文件存在",
  checking: "检查中",
  verified: "已验证",
  failed: "失败",
};

export function LeanBadge({ status }: { status: LeanVerifyStatus }) {
  const tone =
    status === "verified"
      ? "border-accent text-accent"
      : status === "failed"
        ? "border-danger text-danger"
        : "border-line text-muted";
  return (
    <span className={`inline-block rounded border px-2 py-0.5 text-xs ${tone}`}>
      {LABEL[status]}
    </span>
  );
}
