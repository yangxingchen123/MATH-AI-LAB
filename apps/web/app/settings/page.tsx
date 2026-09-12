import Link from "next/link";
import { collectHealth } from "../../src/lib/health";
import { AiModelPicker } from "../../features/settings/ai-model-picker";
import { GptConnect } from "../../features/settings/gpt-connect";
import { SettingsCard } from "../../features/settings/settings-card";

const LEVEL_LABEL = {
  healthy: "正常",
  warning: "警告",
  unavailable: "不可用",
} as const;

export default function SettingsPage() {
  const health = collectHealth();
  return (
    <article className="mx-auto max-w-prose">
      <p className="settings-kicker">本机</p>
      <h1 className="mt-1 text-2xl font-semibold tracking-tight">设置</h1>
      <p className="mt-3 text-sm text-muted">
        主题在顶栏切换。写入仍只经 Domain Operation。GPT 密钥不进正式知识库。
      </p>
      <AiModelPicker />
      <GptConnect />
      <SettingsCard kicker="系统" title="健康">
        <p className="mt-2 text-sm text-muted">来自本机真实探测。没有探测到的不会画成正常。</p>
        <table className="mt-4 w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-line text-left text-muted">
              <th className="py-1.5 pr-3 font-medium">组件</th>
              <th className="py-1.5 pr-3 font-medium">状态</th>
              <th className="py-1.5 font-medium">说明</th>
            </tr>
          </thead>
          <tbody>
            {health.map((row) => (
              <tr key={row.id} className="border-b border-line">
                <td className="py-1.5 pr-3">{row.label}</td>
                <td className="py-1.5 pr-3">{LEVEL_LABEL[row.level]}</td>
                <td className="py-1.5 text-muted">{row.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="mt-4 text-sm">
          <Link href="/advanced/diagnostics" className="text-accent">
            打开诊断
          </Link>
        </p>
      </SettingsCard>
      <p className="mt-6 text-sm text-muted">
        无 Node 时可用 <code>打开旧版工作台.bat</code>。
      </p>
    </article>
  );
}
