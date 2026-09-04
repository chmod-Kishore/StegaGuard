"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  FileText,
  Hash,
  Layers,
  HardDrive,
  Cpu,
  AlertTriangle,
  ArrowLeft,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import RiskGauge from "@/components/risk-gauge";
import LayerTable from "@/components/layer-table";
import EntropyChart from "@/components/entropy-chart";
import { getScanResult } from "@/lib/api";

/* ---------- types ---------- */

interface ScanResultData {
  risk_score: number;
  verdict: string;
  summary?: string;
  metadata?: {
    filename: string;
    format: string;
    file_size_bytes: number;
    total_params: number;
    layer_count: number;
    file_hash: string;
  };
  risk_breakdown?: Record<string, number>;
  layer_results?: LayerResultEntry[];
}

interface LayerResultEntry {
  name: string;
  param_count: number;
  entropy: number;
  lsb_entropy: number;
  chi2_statistic: number;
  chi2_p_value: number;
  flip_ratio: number;
  ks_statistic: number;
  ks_p_value: number;
  kurtosis: number;
  entropy_anomaly: boolean;
  lsb_anomaly: boolean;
  distribution_anomaly: boolean;
  status: string;
}

/* ---------- helpers ---------- */

function formatParams(count: number): string {
  if (count >= 1_000_000_000) return `${(count / 1_000_000_000).toFixed(1)}B`;
  if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(1)}M`;
  if (count >= 1_000) return `${(count / 1_000).toFixed(1)}K`;
  return String(count ?? "---");
}

function generateSummary(data: ScanResultData): string {
  const v = data.verdict?.toUpperCase();
  const score = typeof data.risk_score === "number" ? data.risk_score.toFixed(1) : data.risk_score;
  const layerCount = data.layer_results?.length ?? 0;
  const anomalous = data.layer_results?.filter(
    (l: LayerResultEntry) => l.entropy_anomaly || l.lsb_anomaly || l.distribution_anomaly
  ).length ?? 0;

  if (v === "CLEAR") {
    return `The model received a risk score of ${score}/100 and has been classified as CLEAR. All ${layerCount} layers passed entropy, LSB, and distribution checks without anomalies. No steganographic indicators were detected.`;
  }
  if (v === "LOW") {
    return `The model received a risk score of ${score}/100 and has been classified as LOW risk. ${anomalous} out of ${layerCount} layers showed minor statistical deviations, but none reached anomaly thresholds. No actionable steganographic patterns were identified.`;
  }
  if (v === "WARNING") {
    return `The model received a risk score of ${score}/100 and has been classified as WARNING. ${anomalous} out of ${layerCount} layers showed anomalous patterns in entropy, LSB, or distribution analysis. Manual review of flagged layers is recommended.`;
  }
  return `The model received a risk score of ${score}/100 and has been classified as CRITICAL. ${anomalous} out of ${layerCount} layers exhibited strong anomalies consistent with steganographic modification, backdoor triggers, or hidden payloads. Immediate investigation is required.`;
}

/* ---------- risk breakdown bar colors ---------- */

const BREAKDOWN_COLORS: Record<string, string> = {
  max_entropy_score: "#3b82f6",
  max_lsb_score: "#f97316",
  max_distribution_score: "#a855f7",
  mean_entropy_score: "#06b6d4",
  metadata_score: "#6b7280",
};

const BREAKDOWN_LABELS: Record<string, string> = {
  max_entropy_score: "Max Entropy",
  max_lsb_score: "Max LSB",
  max_distribution_score: "Max Distribution",
  mean_entropy_score: "Mean Entropy",
  metadata_score: "Metadata",
};

/* ---------- custom recharts tooltip ---------- */

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{ name: string; value: number; payload: { key: string; value: number; label: string } }>;
}

function BreakdownTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-gray-700 bg-gray-900 px-4 py-3 shadow-xl text-sm">
      <p className="text-gray-200 font-medium">{d.label}</p>
      <p className="text-gray-400 font-mono mt-1">
        Contribution: {d.value.toFixed(2)}
      </p>
    </div>
  );
}

/* ---------- skeleton ---------- */

function ReportSkeleton() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-12 sm:py-16 animate-pulse">
      <div className="flex items-center gap-3 mb-10">
        <div className="h-8 w-8 rounded bg-gray-800" />
        <div className="h-6 w-48 rounded bg-gray-800" />
      </div>
      <div className="flex flex-col items-center gap-6 mb-12">
        <div className="h-36 w-64 rounded-xl bg-gray-800" />
        <div className="h-6 w-24 rounded bg-gray-800" />
      </div>
      <div className="h-20 w-full rounded-xl bg-gray-800 mb-8" />
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4 mb-8">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-24 rounded-xl bg-gray-800" />
        ))}
      </div>
      <div className="h-80 w-full rounded-xl bg-gray-800 mb-8" />
      <div className="h-96 w-full rounded-xl bg-gray-800" />
    </div>
  );
}

/* ---------- metadata card ---------- */

function MetaCard({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
}) {
  return (
    <Card className="border-gray-800 bg-gray-900/60">
      <CardContent className="flex flex-col items-center gap-2 py-5 px-3">
        <Icon className="h-5 w-5 text-gray-500" />
        <p className="text-xs text-gray-500 uppercase tracking-wider">
          {label}
        </p>
        <p
          className="text-sm font-medium text-gray-200 text-center truncate max-w-full"
          title={value}
        >
          {value}
        </p>
      </CardContent>
    </Card>
  );
}

/* ---------- main component ---------- */

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const scanId = params.id as string;

  const [data, setData] = useState<ScanResultData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!scanId) return;
    let cancelled = false;

    async function load() {
      try {
        const result = await getScanResult(scanId);
        if (!cancelled) {
          setData(result);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load scan result"
          );
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [scanId]);

  if (loading) return <ReportSkeleton />;

  if (error) {
    return (
      <div className="mx-auto max-w-5xl px-4 py-20 text-center">
        <AlertTriangle className="mx-auto h-12 w-12 text-red-400 mb-4" />
        <h2 className="text-xl font-bold text-white mb-2">Error Loading Report</h2>
        <p className="text-gray-400 mb-6">{error}</p>
        <Button variant="outline" onClick={() => router.push("/")}>
          Back to Home
        </Button>
      </div>
    );
  }

  /* ----- derived data ----- */
  const layers = data?.layer_results ?? [];
  const verdict = data?.verdict ?? "UNKNOWN";
  const riskScore =
    typeof data?.risk_score === "number" ? data.risk_score : 0;

  // Risk breakdown for bar chart
  const breakdown = data?.risk_breakdown ?? {};
  const breakdownData = Object.entries(breakdown).map(([key, value]) => ({
    key,
    label: BREAKDOWN_LABELS[key] ?? key,
    value: value as number,
  }));

  // Entropy chart data
  const entropyLayers = layers.map((l: LayerResultEntry) => ({
    name: l.name,
    entropy: l.entropy ?? 0,
    lsb_entropy: l.lsb_entropy ?? 0,
    is_anomaly: l.entropy_anomaly || l.lsb_anomaly || l.distribution_anomaly,
  }));

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:py-12">
      {/* Back button */}
      <Button
        variant="ghost"
        size="sm"
        className="mb-6 gap-2 text-gray-400 hover:text-white"
        onClick={() => router.push("/")}
      >
        <ArrowLeft className="h-4 w-4" />
        New Scan
      </Button>

      {/* ---------- 1. Risk Score Header ---------- */}
      <section className="mb-10">
        <Card className="border-gray-800 bg-gray-900/50">
          <CardContent className="flex flex-col items-center gap-6 py-10">
            <RiskGauge score={riskScore} verdict={verdict} />
          </CardContent>
        </Card>
      </section>

      {/* ---------- 2. Executive Summary ---------- */}
      <section className="mb-8">
        <Card className="border-gray-800 bg-gray-900/50">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <FileText className="h-4 w-4 text-gray-500" />
              Executive Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-gray-300">
              {data?.summary || (data && generateSummary(data))}
            </p>
          </CardContent>
        </Card>
      </section>

      {/* ---------- 3. Model Metadata ---------- */}
      <section className="mb-8">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-500">
          Model Metadata
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          <MetaCard
            icon={FileText}
            label="Filename"
            value={data?.metadata?.filename ?? "---"}
          />
          <MetaCard
            icon={Cpu}
            label="Format"
            value={data?.metadata?.format ?? "---"}
          />
          <MetaCard
            icon={Hash}
            label="Parameters"
            value={
              data?.metadata?.total_params
                ? formatParams(data.metadata.total_params)
                : "---"
            }
          />
          <MetaCard
            icon={Layers}
            label="Layers"
            value={String(data?.metadata?.layer_count ?? layers.length)}
          />
          <MetaCard
            icon={HardDrive}
            label="File Hash"
            value={
              data?.metadata?.file_hash
                ? data.metadata.file_hash.slice(0, 12) + "..."
                : "---"
            }
          />
        </div>
      </section>

      <Separator className="my-8" />

      {/* ---------- 4 & 5. Tabs for Breakdown / Layers ---------- */}
      <Tabs defaultValue="breakdown">
        <TabsList className="mb-6">
          <TabsTrigger value="breakdown">Risk Breakdown</TabsTrigger>
          <TabsTrigger value="entropy">Entropy Chart</TabsTrigger>
          <TabsTrigger value="layers">Layer Results</TabsTrigger>
        </TabsList>

        {/* -- Risk Breakdown Tab -- */}
        <TabsContent value="breakdown">
          <Card className="border-gray-800 bg-gray-900/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">
                Risk Component Breakdown
              </CardTitle>
              <CardDescription>
                Contribution of each analysis component to the overall risk
                score
              </CardDescription>
            </CardHeader>
            <CardContent>
              {breakdownData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={breakdownData}
                    margin={{ top: 10, right: 20, left: 10, bottom: 20 }}
                    barCategoryGap="30%"
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#1f2937"
                      vertical={false}
                    />
                    <XAxis
                      dataKey="label"
                      tick={{ fill: "#9ca3af", fontSize: 12 }}
                      stroke="#374151"
                    />
                    <YAxis
                      tick={{ fill: "#9ca3af", fontSize: 12 }}
                      stroke="#374151"
                    />
                    <Tooltip
                      content={<BreakdownTooltip />}
                      cursor={{ fill: "rgba(255,255,255,0.03)" }}
                    />
                    <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                      {breakdownData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={
                            BREAKDOWN_COLORS[entry.key] ?? "#6b7280"
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <p className="py-12 text-center text-sm text-gray-500">
                  No breakdown data available.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* -- Entropy Chart Tab -- */}
        <TabsContent value="entropy">
          {entropyLayers.length > 0 ? (
            <EntropyChart layers={entropyLayers} />
          ) : (
            <Card className="border-gray-800 bg-gray-900/50">
              <CardContent className="py-12 text-center text-sm text-gray-500">
                No entropy data available.
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* -- Layer Results Tab -- */}
        <TabsContent value="layers">
          <LayerTable layers={layers} />
        </TabsContent>
      </Tabs>

      {/* Scan ID footer */}
      <div className="mt-10 text-center">
        <p className="text-xs text-gray-600">
          Scan ID:{" "}
          <span className="font-mono text-gray-500">{scanId}</span>
        </p>
      </div>
    </div>
  );
}
