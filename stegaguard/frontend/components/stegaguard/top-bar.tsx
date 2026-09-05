"use client";

import { useEffect, useState } from "react";
import { Shield } from "lucide-react";
import Link from "next/link";

export default function TopBar() {
  const [uptime, setUptime] = useState("00:00:00");

  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      const diff = Math.floor((Date.now() - startTime) / 1000);
      const h = String(Math.floor(diff / 3600)).padStart(2, "0");
      const m = String(Math.floor((diff % 3600) / 60)).padStart(2, "0");
      const s = String(diff % 60).padStart(2, "0");
      setUptime(`${h}:${m}:${s}`);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="w-full border-b border-border bg-panel/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-3 group">
          <Shield className="h-5 w-5 text-matrix group-hover:animate-flicker" />
          <span className="text-lg font-bold tracking-widest text-foreground uppercase">
            StegaGuard
          </span>
        </Link>
        <div className="flex items-center gap-6 font-mono text-sm">
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-matrix animate-pulse shadow-[0_0_8px_#00FF41]"></div>
            <span className="text-matrix hidden sm:inline-block">SYSTEM ONLINE</span>
            <span className="text-matrix sm:hidden">ON</span>
          </div>
          <div className="text-dim border-l border-border pl-6 hidden sm:block">
            UPTIME: {uptime}
          </div>
        </div>
      </div>
    </header>
  );
}
