import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { Shield } from "lucide-react";
import Link from "next/link";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "StegaGuard",
  description: "AI Model Weight Integrity Scanner",
};

function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2.5">
          <Shield className="h-6 w-6 text-blue-500" />
          <span className="text-lg font-bold tracking-tight text-white">
            StegaGuard
          </span>
        </Link>
        <p className="hidden text-sm text-gray-500 sm:block">
          AI Model Weight Integrity Scanner
        </p>
      </div>
    </header>
  );
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} font-[family-name:var(--font-geist-sans)] bg-gray-950 text-white antialiased`}
      >
        <Navbar />
        <main className="min-h-[calc(100vh-3.5rem)]">{children}</main>
      </body>
    </html>
  );
}
