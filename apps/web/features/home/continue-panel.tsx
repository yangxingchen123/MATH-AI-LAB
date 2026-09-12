"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  clearPins,
  clearRecent,
  listPins,
  listRecent,
  type PrefItem,
} from "../prefs/local-prefs";

export function ContinuePanel() {
  const [recent, setRecent] = useState<PrefItem[]>([]);
  const [pins, setPins] = useState<PrefItem[]>([]);

  useEffect(() => {
    setRecent(listRecent());
    setPins(listPins());
  }, []);

  return (
    <>
      <section className="mt-8">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">继续</h2>
          {recent.length > 0 ? (
            <button
              type="button"
              className="text-sm text-muted underline"
              onClick={() => {
                clearRecent();
                setRecent([]);
              }}
            >
              清除最近
            </button>
          ) : null}
        </div>
        {recent[0] ? (
          <p className="mt-2">
            <Link href={recent[0].href} className="text-accent">
              {recent[0].id} {recent[0].title}
            </Link>
          </p>
        ) : (
          <p className="mt-2 text-muted">还没有最近浏览。打开一道题或一条知识后会出现在这里。</p>
        )}
      </section>

      <section className="mt-8">
        <h2 className="text-lg font-semibold">最近浏览</h2>
        {recent.length === 0 ? (
          <p className="mt-2 text-sm text-muted">保存在本机 localStorage，不写仓库。</p>
        ) : (
          <ul className="mt-2 space-y-1 text-sm">
            {recent.slice(0, 6).map((item) => (
              <li key={`${item.kind}-${item.id}`}>
                <Link href={item.href} className="text-accent">
                  {item.id} {item.title}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-8">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">固定</h2>
          {pins.length > 0 ? (
            <button
              type="button"
              className="text-sm text-muted underline"
              onClick={() => {
                clearPins();
                setPins([]);
              }}
            >
              清除固定
            </button>
          ) : null}
        </div>
        {pins.length === 0 ? (
          <p className="mt-2 text-sm text-muted">在对象页点击「固定」即可钉在这里。</p>
        ) : (
          <ul className="mt-2 space-y-1 text-sm">
            {pins.slice(0, 6).map((item) => (
              <li key={`${item.kind}-${item.id}`}>
                <Link href={item.href} className="text-accent">
                  {item.id} {item.title}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
