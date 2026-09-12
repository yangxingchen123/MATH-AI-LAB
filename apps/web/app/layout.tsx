import type { Metadata } from "next";
import "katex/dist/katex.min.css";
import "@math-ai-lab/math-renderer/styles.css";
import { AppShell } from "../features/shell/app-shell";
import { ThemeScript } from "../features/shell/theme-script";
import "./globals.css";

export const metadata: Metadata = {
  title: "MATH-AI-LAB",
  description: "数学 AI 学习与研究工作台",
};

export const dynamic = "force-dynamic";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <head>
        <ThemeScript />
      </head>
      <body>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
