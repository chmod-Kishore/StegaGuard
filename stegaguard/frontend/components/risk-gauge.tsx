"use client";

import { useMemo } from "react";

interface RiskGaugeProps {
  score: number;
  verdict: string;
}

const VERDICT_COLORS: Record<string, string> = {
  CLEAR: "#22c55e",
  LOW: "#3b82f6",
  WARNING: "#f59e0b",
  CRITICAL: "#ef4444",
};

export default function RiskGauge({ score, verdict }: RiskGaugeProps) {
  const color = VERDICT_COLORS[verdict] ?? "#6b7280";

  const clampedScore = Math.min(Math.max(score, 0), 100);

  // SVG arc parameters
  // Semi-circle: from 180 degrees (left) to 0 degrees (right)
  const cx = 125;
  const cy = 120;
  const r = 100;
  const strokeWidth = 14;

  // Arc calculation for a semicircle (180 degrees, left to right)
  const circumferenceHalf = Math.PI * r; // half circle circumference
  const dashOffset = circumferenceHalf * (1 - clampedScore / 100);

  // Start and end points of the semicircle
  // From (-1,0) to (1,0) — leftmost to rightmost of the circle top-half
  const arcPath = useMemo(() => {
    const startX = cx - r;
    const startY = cy;
    const endX = cx + r;
    const endY = cy;
    return `M ${startX} ${startY} A ${r} ${r} 0 0 1 ${endX} ${endY}`;
  }, [cx, cy, r]);

  return (
    <div className="flex flex-col items-center w-full max-w-[280px] mx-auto">
      <svg
        viewBox="0 0 250 145"
        className="w-full"
        aria-label={`Risk score: ${clampedScore}, verdict: ${verdict}`}
      >
        {/* Background arc */}
        <path
          d={arcPath}
          fill="none"
          stroke="#374151"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Foreground arc */}
        <path
          d={arcPath}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumferenceHalf}
          strokeDashoffset={dashOffset}
          className="transition-all duration-1000 ease-out"
        />

        {/* Score text */}
        <text
          x={cx}
          y={cy - 15}
          textAnchor="middle"
          dominantBaseline="middle"
          className="fill-white text-4xl font-bold"
          style={{ fontSize: "42px", fontWeight: 700 }}
        >
          {clampedScore}
        </text>

        {/* Verdict text */}
        <text
          x={cx}
          y={cy + 18}
          textAnchor="middle"
          dominantBaseline="middle"
          fill={color}
          style={{ fontSize: "14px", fontWeight: 600, letterSpacing: "0.1em" }}
        >
          {verdict}
        </text>
      </svg>

      {/* Label below */}
      <p className="text-gray-500 text-sm -mt-2">Risk Score</p>
    </div>
  );
}
