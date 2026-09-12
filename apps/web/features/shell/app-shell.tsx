"use client";

import { useState } from "react";
import { WriteBanner } from "../operations/write-banner";
import { CommandPalette } from "../search/command-palette";
import { Sidebar } from "./sidebar";
import { Toc } from "./toc";
import { TocProvider } from "./toc-context";
import { Topbar } from "./topbar";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [navOpen, setNavOpen] = useState(false);
  const [tocOpen, setTocOpen] = useState(false);

  return (
    <TocProvider>
      <div className="flex min-h-screen flex-col">
        <Topbar />
        <WriteBanner />
        <div className="flex min-h-0 flex-1">
          <div className="flex items-center gap-2 border-b border-line px-3 py-2 lg:hidden">
            <button
              type="button"
              className="rounded border border-line px-2 py-1 text-sm"
              onClick={() => setNavOpen(true)}
            >
              菜单
            </button>
            <button
              type="button"
              className="rounded border border-line px-2 py-1 text-sm"
              onClick={() => setTocOpen(true)}
            >
              目录
            </button>
          </div>
          <aside className="hidden w-56 shrink-0 overflow-y-auto border-r border-line bg-[var(--sidebar)] px-3 py-4 lg:block">
            <Sidebar />
          </aside>
          <main className="min-w-0 flex-1 bg-[var(--panel)] px-4 py-6 sm:px-8">{children}</main>
          <aside className="hidden w-52 shrink-0 overflow-y-auto border-l border-line p-3 xl:block">
            <Toc />
          </aside>
        </div>
        {navOpen ? (
          <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true" aria-label="导航">
            <button
              type="button"
              className="absolute inset-0 bg-black/40"
              aria-label="关闭菜单"
              onClick={() => setNavOpen(false)}
            />
            <aside className="relative h-full w-64 overflow-y-auto bg-[var(--sidebar)] p-4">
              <Sidebar />
            </aside>
          </div>
        ) : null}
        <CommandPalette />
        {tocOpen ? (
          <div className="fixed inset-0 z-40 xl:hidden" role="dialog" aria-modal="true" aria-label="本页目录">
            <button
              type="button"
              className="absolute inset-0 bg-black/40"
              aria-label="关闭目录"
              onClick={() => setTocOpen(false)}
            />
            <aside className="relative ml-auto h-full w-64 overflow-y-auto bg-[var(--panel)] p-4">
              <Toc />
            </aside>
          </div>
        ) : null}
      </div>
    </TocProvider>
  );
}
