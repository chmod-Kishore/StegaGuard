"use client";

import Link from "next/link";
import { Shield } from "lucide-react";

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-gray-800 bg-gray-950/95 backdrop-blur supports-[backdrop-filter]:bg-gray-950/80">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Logo / Brand */}
        <Link
          href="/"
          className="flex items-center gap-2 text-white hover:opacity-90 transition-opacity"
        >
          <Shield className="h-6 w-6 text-blue-400" />
          <span className="text-lg font-bold tracking-tight">StegaGuard</span>
        </Link>

        {/* Tagline */}
        <p className="hidden sm:block text-sm text-gray-500">
          AI Model Weight Integrity Scanner
        </p>
      </div>
    </nav>
  );
}
