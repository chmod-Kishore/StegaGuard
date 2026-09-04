"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Shield,
  CheckCircle,
  Loader2,
  AlertTriangle,
  Clock,
  ArrowRight,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { connectScanWs, type ProgressEvent } from "@/lib/ws";
import { getScanResult } from "@/lib/api";

const STAGES = [
  { key: "parsing", label: "Model Parsing", desc: "Loading and parsing model structure" },
  { key: "entropy", label: "Entropy Analysis", desc: "Measuring information density per layer" },
  { key: "lsb", label: "LSB Detection", desc: "Checking least-significant-bit patterns" },
  { key: "distribution", label: "Distribution Tests", desc: "Statistical distribution analysis" },
  { key: "scoring", label: "Risk Scoring", desc: "Computing aggregate risk score" },
];

type ScanStatus = "connecting" | "scanning" | "completed" | "error";

interface ScanResult {
  risk_score?: number;
  verdict?: string;
  status?: string;
  error?: string;
}

function verdictColor(verdict: string) {
  switch (verdict?.toUpperCase()) {
    case "CLEAR":
      return "text-green-400";
    case "LOW":
      return "text-blue-400";
    case "WARNING":
      return "text-amber-400";
    case "CRITICAL":
      return "text-red-400";
    default:
      return "text-gray-400";
  }
}

function verdictBadgeVariant(verdict: string): "success" | "default" | "warning" | "destructive" {
  switch (verdict?.toUpperCase()) {
    case "CLEAR":
      return "success";
    case "LOW":
      return "default";
    case "WARNING":
      return "warning";
    case "CRITICAL":
      return "destructive";
    default:
      return "default";
  }
}

export default function ScanPage() {
  const params = useParams();
  const router = useRouter();
  const scanId = params.id as string;

  const [status, setStatus] = useState<ScanStatus>("connecting");
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState("");
  const [currentLayer, setCurrentLayer] = useState("");
  const [completedStages, setCompletedStages] = useState<string[]>([]);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  const handleComplete = useCallback((data: ScanResult) => {
    setStatus("completed");
    setProgress(100);
    setResult(data);
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  const handleError = useCallback((errMsg: string) => {
    setStatus("error");
    setError(errMsg);
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  // WebSocket connection
  useEffect(() => {
    if (!scanId) return;

    const ws = connectScanWs(
      scanId,
      (event: ProgressEvent) => {
        setStatus("scanning");
        setCurrentStage(event.stage);
        setCurrentLayer(event.layer);

        setCompletedStages((prev) => {
          const updated = [...prev];
          if (!updated.includes("parsing")) updated.push("parsing");
          if (event.progress >= 1.0 && !updated.includes(event.stage)) {
            updated.push(event.stage);
          }
          const stageIndex = STAGES.findIndex((s) => s.key === event.stage);
          for (let i = 1; i < stageIndex; i++) {
            if (!updated.includes(STAGES[i].key)) updated.push(STAGES[i].key);
          }
          const overallProgress = Math.round(
            (updated.length / STAGES.length) * 100
          );
          setProgress(overallProgress);
          return updated;
        });
      },
      (data) => handleComplete(data as ScanResult),
      handleError
    );
    wsRef.current = ws;

    return () => {
      ws.close();
    };
  }, [scanId, handleComplete, handleError]);

  // Polling fallback
  useEffect(() => {
    if (!scanId || status === "completed" || status === "error") return;

    pollRef.current = setInterval(async () => {
      try {
        const data = await getScanResult(scanId);
        if (data.status === "failed") {
          handleError(data.error || "Scan failed");
        } else if (data.status === "completed") {
          handleComplete(data);
        }
      } catch {
        // Polling failure is non-fatal; WebSocket is primary
      }
    }, 2000);

    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [scanId, status, handleComplete, handleError]);

  function getStageStatus(stageKey: string): "completed" | "active" | "pending" {
    if (completedStages.includes(stageKey)) return "completed";
    if (currentStage === stageKey) return "active";
    return "pending";
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:py-16">
      {/* Header */}
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-white">Scanning Model</h1>
        <p className="mt-1 text-sm text-gray-500">
          Scan ID: <span className="font-mono text-gray-400">{scanId}</span>
        </p>
      </div>

      {/* Error State */}
      {status === "error" && (
        <Card className="border-red-900 bg-red-950/30">
          <CardContent className="flex flex-col items-center gap-3 py-8">
            <AlertTriangle className="h-10 w-10 text-red-400" />
            <p className="text-lg font-medium text-red-300">Scan Failed</p>
            <p className="text-sm text-red-400/80">{error}</p>
            <Button
              variant="outline"
              className="mt-4"
              onClick={() => router.push("/")}
            >
              Try Again
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Completed State */}
      {status === "completed" && result && (
        <Card className="mb-8 border-gray-800">
          <CardContent className="flex flex-col items-center gap-4 py-8">
            <div
              className={`flex h-20 w-20 items-center justify-center rounded-full ${
                result.verdict?.toUpperCase() === "CLEAR"
                  ? "bg-green-500/10"
                  : result.verdict?.toUpperCase() === "CRITICAL"
                  ? "bg-red-500/10"
                  : "bg-amber-500/10"
              }`}
            >
              {result.verdict?.toUpperCase() === "CLEAR" ? (
                <CheckCircle className="h-10 w-10 text-green-400" />
              ) : result.verdict?.toUpperCase() === "CRITICAL" ? (
                <AlertTriangle className="h-10 w-10 text-red-400" />
              ) : (
                <Shield className="h-10 w-10 text-amber-400" />
              )}
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-400">Risk Score</p>
              <p
                className={`text-4xl font-bold ${verdictColor(result.verdict ?? "")}`}
              >
                {typeof result.risk_score === "number"
                  ? result.risk_score.toFixed(1)
                  : result.risk_score}
              </p>
              <Badge
                variant={verdictBadgeVariant(result.verdict ?? "")}
                className="mt-2"
              >
                {result.verdict ?? "UNKNOWN"}
              </Badge>
            </div>

            <Button
              className="mt-4 gap-2"
              onClick={() => router.push(`/report/${scanId}`)}
            >
              View Full Report
              <ArrowRight className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Progress (during scanning) */}
      {(status === "connecting" || status === "scanning") && (
        <>
          <div className="mb-8">
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="text-gray-400">Overall Progress</span>
              <span className="font-mono text-gray-300">
                {Math.round(progress)}%
              </span>
            </div>
            <Progress value={progress} />
            {currentLayer && (
              <p className="mt-2 text-xs text-gray-500">
                Analyzing:{" "}
                <span className="font-mono text-gray-400">{currentLayer}</span>
              </p>
            )}
          </div>

          {/* Stage Cards */}
          <div className="space-y-3">
            {STAGES.map((stage) => {
              const stageStatus = getStageStatus(stage.key);
              return (
                <Card
                  key={stage.key}
                  className={`transition-all duration-300 ${
                    stageStatus === "active"
                      ? "border-blue-500/50 bg-blue-950/20"
                      : stageStatus === "completed"
                      ? "border-green-500/20 bg-gray-900/50"
                      : "border-gray-800/50 bg-gray-900/30 opacity-50"
                  }`}
                >
                  <CardContent className="flex items-center gap-4 py-4">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full">
                      {stageStatus === "completed" ? (
                        <CheckCircle className="h-5 w-5 text-green-400" />
                      ) : stageStatus === "active" ? (
                        <Loader2 className="h-5 w-5 animate-spin text-blue-400" />
                      ) : (
                        <Clock className="h-5 w-5 text-gray-600" />
                      )}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p
                        className={`text-sm font-medium ${
                          stageStatus === "active"
                            ? "text-white"
                            : stageStatus === "completed"
                            ? "text-gray-300"
                            : "text-gray-500"
                        }`}
                      >
                        {stage.label}
                      </p>
                      <p className="text-xs text-gray-500">{stage.desc}</p>
                    </div>
                    <Badge
                      variant={
                        stageStatus === "completed"
                          ? "success"
                          : stageStatus === "active"
                          ? "default"
                          : "secondary"
                      }
                      className="shrink-0"
                    >
                      {stageStatus === "completed"
                        ? "Done"
                        : stageStatus === "active"
                        ? "Running"
                        : "Pending"}
                    </Badge>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
