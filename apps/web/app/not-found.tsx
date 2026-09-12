import Link from "next/link";

export default function NotFound() {
  return (
    <article className="mx-auto max-w-prose">
      <h1 className="text-2xl font-semibold">未找到</h1>
      <p className="mt-3 text-muted">没有这个页面或对象。身份来自 YAML id，不是文件名。</p>
      <p className="mt-4">
        <Link href="/" className="text-accent underline">
          回到工作台
        </Link>
      </p>
    </article>
  );
}
