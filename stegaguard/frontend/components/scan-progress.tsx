"use client";

import { Clock, Loader2, CheckCircle2, Shield } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

export interface StageInfo {
  name: string;
  label: string;
  status: "pending" | "active" | "completed";
}

interface ScanProgressProps {
  stages: StageInfo[];
  currentStage?: string;
  currentLayer: string;
  progress: number;
}

function StageIcon({ status }: { status: StageInfo["status"] }) {
  switch (status) {
    case "pending":
      return <Clock className="h-5 w-5 text-gray-500" />;
    case "active":
      return <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />;
    case "completed":
      return <CheckCircle2 className="h-5 w-5 text-green-400" />;
  }
}

export default function ScanProgress({
  stages,
  currentStage: _currentStage,
  currentLayer,
  progress,
}: ScanProgressProps) {
  void _currentStage; // used by parent for stage tracking
  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <Shield className="h-5 w-5 text-blue-400" />
        <h2 className="text-lg font-semibold text-white">Scanning Model</h2>
      </div>

      {/* Stage Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
        {stages.map((stage, idx) => (
          <div
            key={stage.name}
            className={cn(
              "relative flex flex-col items-center gap-2 rounded-xl border px-3 py-4 transition-all duration-300",
              stage.status === "active"
                ? "border-blue-500 bg-blue-500/10 shadow-[0_0_15px_rgba(59,130,246,0.15)]"
                : stage.status === "completed"
                ? "border-green-800/50 bg-green-900/10"
                : "border-gray-800 bg-gray-900/50"
            )}
          >
            {/* Animated glow ring for active stage */}
            {stage.status === "active" && (
              <div className="absolute inset-0 rounded-xl border border-blue-400/30 animate-pulse" />
            )}

            <StageIcon status={stage.status} />

            <span
              className={cn(
                "text-xs font-medium text-center leading-tight",
                stage.status === "active"
                  ? "text-blue-300"
                  : stage.status === "completed"
                  ? "text-green-300"
                  : "text-gray-500"
              )}
            >
              {stage.label}
            </span>

            {/* Connector arrow (except last) */}
            {idx < stages.length - 1 && (
              <div className="hidden md:block absolute -right-3 top-1/2 -translate-y-1/2 text-gray-700 z-10">
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                  <path
                    d="M2 6h8M7 3l3 3-3 3"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Current layer and progress */}
      <div className="space-y-3">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">
            Current layer:{" "}
            <span className="text-gray-200 font-mono">{currentLayer || "---"}</span>
          </span>
          <span className="text-gray-400 tabular-nums">
            {Math.round(progress)}%
          </span>
        </div>

        <Progress
          value={progress}
          className="h-2 bg-gray-800"
          indicatorClassName={cn(
            progress >= 100
              ? "bg-green-500"
              : "bg-blue-500"
          )}
        />
      </div>
    </div>
  );
}
