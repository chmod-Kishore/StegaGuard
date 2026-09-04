"use client";

import { useState, useMemo, useCallback } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { ChevronDown, ChevronUp, ChevronsUpDown } from "lucide-react";

export interface LayerResult {
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

type SortKey = keyof LayerResult;
type SortDir = "asc" | "desc";

function formatNum(val: number, decimals = 4): string {
  if (val === undefined || val === null || isNaN(val)) return "---";
  return val.toFixed(decimals);
}

function formatParams(count: number): string {
  if (count >= 1_000_000_000) return `${(count / 1_000_000_000).toFixed(1)}B`;
  if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(1)}M`;
  if (count >= 1_000) return `${(count / 1_000).toFixed(1)}K`;
  return String(count);
}

function statusVariant(status: string): "success" | "warning" | "destructive" {
  switch (status.toLowerCase()) {
    case "normal":
    case "clean":
    case "clear":
      return "success";
    case "warning":
    case "suspicious":
      return "warning";
    case "critical":
    case "anomaly":
    case "anomalous":
      return "destructive";
    default:
      return "success";
  }
}

function AnomalyFlag({ flag, label }: { flag: boolean; label: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-xs",
        flag ? "text-red-400" : "text-green-400"
      )}
    >
      <span
        className={cn(
          "h-2 w-2 rounded-full",
          flag ? "bg-red-400" : "bg-green-400"
        )}
      />
      {label}: {flag ? "Anomaly" : "Normal"}
    </span>
  );
}

interface LayerTableProps {
  layers: LayerResult[];
}

export default function LayerTable({ layers }: LayerTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("name");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const handleSort = useCallback(
    (key: SortKey) => {
      if (sortKey === key) {
        setSortDir((d) => (d === "asc" ? "desc" : "asc"));
      } else {
        setSortKey(key);
        setSortDir("asc");
      }
    },
    [sortKey]
  );

  const sorted = useMemo(() => {
    const copy = [...layers];
    copy.sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (typeof aVal === "string" && typeof bVal === "string") {
        return sortDir === "asc"
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }
      if (typeof aVal === "number" && typeof bVal === "number") {
        return sortDir === "asc" ? aVal - bVal : bVal - aVal;
      }
      return 0;
    });
    return copy;
  }, [layers, sortKey, sortDir]);

  function SortIcon({ col }: { col: SortKey }) {
    if (sortKey !== col)
      return <ChevronsUpDown className="h-3.5 w-3.5 text-gray-600" />;
    return sortDir === "asc" ? (
      <ChevronUp className="h-3.5 w-3.5 text-blue-400" />
    ) : (
      <ChevronDown className="h-3.5 w-3.5 text-blue-400" />
    );
  }

  function SortableHead({
    col,
    children,
    className,
  }: {
    col: SortKey;
    children: React.ReactNode;
    className?: string;
  }) {
    return (
      <TableHead
        className={cn(
          "cursor-pointer select-none hover:text-gray-200 transition-colors",
          className
        )}
        onClick={() => handleSort(col)}
      >
        <span className="inline-flex items-center gap-1">
          {children}
          <SortIcon col={col} />
        </span>
      </TableHead>
    );
  }

  return (
    <div className="w-full rounded-xl border border-gray-800 bg-gray-950/50 overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="border-gray-800 hover:bg-transparent">
            <SortableHead col="name" className="min-w-[180px]">
              Layer Name
            </SortableHead>
            <SortableHead col="param_count">Params</SortableHead>
            <SortableHead col="entropy">Entropy</SortableHead>
            <SortableHead col="lsb_entropy">LSB Entropy</SortableHead>
            <SortableHead col="chi2_p_value">Chi2 p-val</SortableHead>
            <SortableHead col="ks_statistic">KS Stat</SortableHead>
            <SortableHead col="status">Status</SortableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sorted.map((layer, idx) => {
            const isExpanded = expandedRow === layer.name;
            return (
              <>
                <TableRow
                  key={layer.name}
                  onClick={() =>
                    setExpandedRow(isExpanded ? null : layer.name)
                  }
                  className={cn(
                    "cursor-pointer transition-colors",
                    idx % 2 === 0 ? "bg-gray-900/30" : "bg-gray-900/60",
                    isExpanded && "bg-gray-800/50"
                  )}
                >
                  <TableCell className="font-mono text-sm text-gray-200 max-w-[220px]">
                    <span
                      className="block truncate"
                      title={layer.name}
                    >
                      {layer.name}
                    </span>
                  </TableCell>
                  <TableCell className="text-gray-300 tabular-nums text-sm">
                    {formatParams(layer.param_count)}
                  </TableCell>
                  <TableCell className="text-gray-300 tabular-nums text-sm">
                    {formatNum(layer.entropy)}
                  </TableCell>
                  <TableCell className="text-gray-300 tabular-nums text-sm">
                    {formatNum(layer.lsb_entropy)}
                  </TableCell>
                  <TableCell className="text-gray-300 tabular-nums text-sm">
                    {formatNum(layer.chi2_p_value)}
                  </TableCell>
                  <TableCell className="text-gray-300 tabular-nums text-sm">
                    {formatNum(layer.ks_statistic)}
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusVariant(layer.status)}>
                      {layer.status}
                    </Badge>
                  </TableCell>
                </TableRow>

                {/* Expanded detail row */}
                {isExpanded && (
                  <TableRow
                    key={`${layer.name}-detail`}
                    className="bg-gray-800/30 hover:bg-gray-800/40"
                  >
                    <TableCell colSpan={7} className="py-4 px-6">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
                        {/* Entropy Details */}
                        <div className="space-y-2">
                          <h4 className="font-semibold text-gray-300 text-xs uppercase tracking-wider">
                            Entropy Analysis
                          </h4>
                          <div className="space-y-1 text-gray-400">
                            <p>
                              Full entropy:{" "}
                              <span className="text-gray-200 font-mono">
                                {formatNum(layer.entropy)}
                              </span>
                            </p>
                            <p>
                              LSB entropy:{" "}
                              <span className="text-gray-200 font-mono">
                                {formatNum(layer.lsb_entropy)}
                              </span>
                            </p>
                            <p>
                              Kurtosis:{" "}
                              <span className="text-gray-200 font-mono">
                                {formatNum(layer.kurtosis)}
                              </span>
                            </p>
                          </div>
                          <AnomalyFlag
                            flag={layer.entropy_anomaly}
                            label="Entropy"
                          />
                        </div>

                        {/* Chi-Square Details */}
                        <div className="space-y-2">
                          <h4 className="font-semibold text-gray-300 text-xs uppercase tracking-wider">
                            Chi-Square Test
                          </h4>
                          <div className="space-y-1 text-gray-400">
                            <p>
                              Statistic:{" "}
                              <span className="text-gray-200 font-mono">
                                {formatNum(layer.chi2_statistic)}
                              </span>
                            </p>
                            <p>
                              p-value:{" "}
                              <span className="text-gray-200 font-mono">
                                {formatNum(layer.chi2_p_value)}
                              </span>
                            </p>
                            <p>
                              Flip ratio:{" "}
                              <span className="text-gray-200 font-mono">
                                {formatNum(layer.flip_ratio)}
                              </span>
                            </p>
                          </div>
                          <AnomalyFlag
                            flag={layer.lsb_anomaly}
                            label="LSB"
                          />
                        </div>

                        {/* Distribution Details */}
                        <div className="space-y-2">
                          <h4 className="font-semibold text-gray-300 text-xs uppercase tracking-wider">
                            Distribution Test
                          </h4>
                          <div className="space-y-1 text-gray-400">
                            <p>
                              KS statistic:{" "}
                              <span className="text-gray-200 font-mono">
                                {formatNum(layer.ks_statistic)}
                              </span>
                            </p>
                            <p>
                              KS p-value:{" "}
                              <span className="text-gray-200 font-mono">
                                {formatNum(layer.ks_p_value)}
                              </span>
                            </p>
                          </div>
                          <AnomalyFlag
                            flag={layer.distribution_anomaly}
                            label="Distribution"
                          />
                        </div>
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </>
            );
          })}
        </TableBody>
      </Table>

      {layers.length === 0 && (
        <div className="py-12 text-center text-gray-500 text-sm">
          No layer results to display.
        </div>
      )}
    </div>
  );
}
