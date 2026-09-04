"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface LayerEntropy {
  name: string;
  entropy: number;
  lsb_entropy: number;
  is_anomaly: boolean;
}

interface EntropyChartProps {
  layers: LayerEntropy[];
}

function truncateName(name: string, maxLen = 16): string {
  if (name.length <= maxLen) return name;
  return name.slice(0, maxLen - 1) + "…";
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    name: string;
    value: number;
    color: string;
    payload: LayerEntropy;
  }>;
  label?: string;
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload;
  return (
    <div className="rounded-lg border border-gray-700 bg-gray-900 px-4 py-3 shadow-xl">
      <p className="text-sm font-medium text-gray-200 mb-2 font-mono">
        {data.name}
      </p>
      <div className="space-y-1 text-xs">
        <p className="text-blue-400">
          Entropy:{" "}
          <span className="font-mono text-gray-200">
            {data.entropy.toFixed(4)}
          </span>
        </p>
        <p className="text-orange-400">
          LSB Entropy:{" "}
          <span className="font-mono text-gray-200">
            {data.lsb_entropy.toFixed(4)}
          </span>
        </p>
        {data.is_anomaly && (
          <p className="text-red-400 font-semibold mt-1">Anomaly Detected</p>
        )}
      </div>
    </div>
  );
}

export default function EntropyChart({ layers }: EntropyChartProps) {
  // Determine tick interval for x-axis based on number of layers
  const tickInterval =
    layers.length <= 15 ? 0 : Math.floor(layers.length / 15);

  const chartData = layers.map((l) => ({
    ...l,
    displayName: truncateName(l.name),
  }));

  return (
    <div className="w-full rounded-xl border border-gray-800 bg-gray-950/50 p-4">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">
        Per-Layer Entropy Distribution
      </h3>
      <ResponsiveContainer width="100%" height={350}>
        <BarChart
          data={chartData}
          margin={{ top: 10, right: 20, left: 10, bottom: 60 }}
          barCategoryGap="20%"
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#1f2937"
            vertical={false}
          />
          <XAxis
            dataKey="displayName"
            tick={{ fill: "#9ca3af", fontSize: 11 }}
            angle={-45}
            textAnchor="end"
            interval={tickInterval}
            height={70}
            stroke="#374151"
          />
          <YAxis
            domain={[0, 8]}
            tick={{ fill: "#9ca3af", fontSize: 12 }}
            stroke="#374151"
            label={{
              value: "Entropy",
              angle: -90,
              position: "insideLeft",
              fill: "#6b7280",
              style: { fontSize: 12 },
            }}
          />
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ fill: "rgba(255,255,255,0.03)" }}
          />
          <ReferenceLine
            y={6.5}
            stroke="#ef4444"
            strokeDasharray="6 4"
            strokeWidth={1.5}
            label={{
              value: "Anomaly Threshold (6.5)",
              position: "right",
              fill: "#ef4444",
              fontSize: 11,
            }}
          />

          {/* Full entropy bars */}
          <Bar dataKey="entropy" name="Entropy" radius={[2, 2, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`entropy-${index}`}
                fill={entry.is_anomaly ? "#3b82f680" : "#3b82f6"}
                opacity={entry.is_anomaly ? 0.6 : 0.9}
              />
            ))}
          </Bar>

          {/* LSB entropy bars */}
          <Bar dataKey="lsb_entropy" name="LSB Entropy" radius={[2, 2, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`lsb-${index}`}
                fill={entry.is_anomaly ? "#f97316" : "#fb923c"}
                opacity={entry.is_anomaly ? 0.6 : 0.9}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="flex items-center justify-center gap-6 mt-2 text-xs text-gray-400">
        <span className="inline-flex items-center gap-1.5">
          <span className="h-3 w-3 rounded-sm bg-blue-500" />
          Full Entropy
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="h-3 w-3 rounded-sm bg-orange-400" />
          LSB Entropy
        </span>
        <span className="inline-flex items-center gap-1.5">
          <span className="h-0.5 w-4 bg-red-500" style={{ borderTop: "2px dashed #ef4444" }} />
          Anomaly Threshold
        </span>
      </div>
    </div>
  );
}
