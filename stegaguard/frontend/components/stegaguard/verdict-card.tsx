"use client";

import { ShieldAlert, ShieldCheck, RefreshCw, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface VerdictCardProps {
  isSuspicious: boolean;
  fileName: string;
  onReset: () => void;
}

export default function VerdictCard({ isSuspicious, fileName, onReset }: VerdictCardProps) {
  const verdictColor = isSuspicious ? "text-alert" : "text-matrix";
  const verdictBg = isSuspicious ? "bg-alert/10" : "bg-matrix/10";
  const verdictBorder = isSuspicious ? "border-alert" : "border-matrix";
  
  const checks = [
    { name: "HEADER_INTEGRITY", pass: true, conf: "99.9%" },
    { name: "LSB_STEGANOGRAPHY", pass: !isSuspicious, conf: isSuspicious ? "87.4%" : "99.1%" },
    { name: "WEIGHT_ENTROPY", pass: !isSuspicious, conf: isSuspicious ? "92.1%" : "98.5%" },
    { name: "KNOWN_BACKDOOR_SIGS", pass: true, conf: "100%" },
  ];

  return (
    <div className={cn("w-full max-w-2xl mx-auto border overflow-hidden shadow-[0_0_30px_rgba(0,0,0,0.5)]", verdictBorder, verdictBg)}>
      {/* Header */}
      <div className={cn("flex items-center gap-4 px-6 py-4 border-b", verdictBorder, isSuspicious ? "bg-alert/20" : "bg-matrix/20")}>
        {isSuspicious ? (
          <ShieldAlert className="h-10 w-10 text-alert animate-pulse" />
        ) : (
          <ShieldCheck className="h-10 w-10 text-matrix" />
        )}
        <div>
          <h2 className={cn("text-2xl font-bold tracking-widest", verdictColor)}>
            {isSuspicious ? "THREAT_DETECTED" : "MODEL_CLEAN"}
          </h2>
          <p className="text-dim font-mono text-sm tracking-tight">{fileName}</p>
        </div>
      </div>

      {/* Body */}
      <div className="p-6 font-mono text-sm">
        <div className="space-y-3 mb-8">
          {checks.map((check, i) => (
            <div key={i} className="flex items-center justify-between border-b border-border/50 pb-2">
              <div className="flex items-center gap-3">
                <span className="text-dim">[{String(i + 1).padStart(2, '0')}]</span>
                <span className="text-foreground">{check.name}</span>
              </div>
              <div className="flex items-center gap-6">
                <span className="text-dim text-xs">CONF: {check.conf}</span>
                {check.pass ? (
                  <span className="text-matrix">PASS</span>
                ) : (
                  <span className="text-alert font-bold">FAIL</span>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-end">
          <button 
            onClick={onReset}
            className="group flex items-center gap-2 border border-border px-4 py-2 text-dim hover:text-foreground hover:border-dim transition-colors"
          >
            <RefreshCw className="h-4 w-4 group-hover:rotate-180 transition-transform duration-500" />
            SCAN_ANOTHER_FILE
          </button>
        </div>
      </div>
    </div>
  );
}
