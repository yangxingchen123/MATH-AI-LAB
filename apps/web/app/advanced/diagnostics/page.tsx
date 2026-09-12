import Link from "next/link";
import { Breadcrumb } from "../../../components/breadcrumb";
import { EmptyState } from "../../../components/empty-state";
import { getRepository } from "../../../src/lib/repo";

function objectHref(target?: string): string | null {
  if (!target) return null;
  if (/^K\d{4}$/.test(target)) return `/knowledge/${target}`;
  if (/^P\d{4}$/.test(target)) return `/problems/${target}`;
  if (/^M\d{4}$/.test(target)) return `/methods/${target}`;
  return null;
}

export default function DiagnosticsPage() {
  const items = getRepository().listDiagnostics();
  return (
    <article>
      <Breadcrumb
        items={[
          { href: "/", label: "工作台" },
          { href: "/settings", label: "设置" },
          { label: "诊断" },
        ]}
      />
      <h1 className="text-2xl font-semibold">诊断</h1>
      <p className="mt-2 text-sm text-muted">
        只读。不会自动修改 canonical 内容。用来找坏引用、解析错误和未知字段。
      </p>
      {items.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="当前没有诊断项" detail="这不表示数学已全部证完，只表示 Adapter 没发现结构问题。" />
        </div>
      ) : (
        <table className="mt-6 w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-line text-left text-muted">
              <th className="py-2 pr-3">类型</th>
              <th className="py-2 pr-3">对象 / 路径</th>
              <th className="py-2">说明与建议</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item, index) => {
              const href = objectHref(item.target);
              return (
                <tr key={`${item.type}-${item.sourcePath}-${index}`} className="border-b border-line">
                  <td className="py-2 pr-3 font-mono">{item.type}</td>
                  <td className="py-2 pr-3 font-mono text-xs">
                    {item.target ?? "—"}
                    {item.sourcePath ? (
                      <div>
                        <Link
                          href={`/repository?path=${encodeURIComponent(item.sourcePath)}`}
                          className="text-accent"
                        >
                          {item.sourcePath}
                        </Link>
                      </div>
                    ) : null}
                  </td>
                  <td className="py-2">
                    {item.explanation}
                    <div className="mt-1 text-xs text-muted">建议：打开对象或仓库源，人工修正。不要自动改 canonical。</div>
                    {href ? (
                      <div className="mt-1">
                        <Link href={href} className="text-accent">
                          打开对象
                        </Link>
                      </div>
                    ) : null}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </article>
  );
}
