"use client";

import { useEffect, useState } from "react";
import { Terminal, CheckCircle2, AlertCircle } from "lucide-react";
import VerdictCard from "./verdict-card";

interface ScanTerminalProps {
  file: File;
  onReset: () => void;
}

const STAGES = [
  "INITIALIZING_SCANNER...",
  "PARSING_FILE_HEADERS...",
  "EXTRACTING_TENSORS...",
  "RUNNING_LSB_ANALYSIS...",
  "CHECKING_WEIGHT_ENTROPY...",
  "EVALUATING_PAYLOAD_HEURISTICS...",
  "FINALIZING_VERDICT..."
];

export default function ScanTerminal({ file, onReset }: ScanTerminalProps) {
  const [currentStage, setCurrentStage] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    let currentLogs = [`> ALLOCATING_RESOURCES_FOR [${file.name}]`];
    setLogs([...currentLogs]);

    let stageIdx = 0;
    
    const interval = setInterval(() => {
      setProgress((prev) => {
        const next = prev + (100 / STAGES.length) / 10; // smooth progress
        if (next >= 100) return 100;
        return next;
      });
    }, 50);

    const stageInterval = setInterval(() => {
      if (stageIdx < STAGES.length) {
        currentLogs = [...currentLogs, `> ${STAGES[stageIdx]}`];
        setLogs(currentLogs);
        setCurrentStage(stageIdx);
        stageIdx++;
      } else {
        clearInterval(interval);
        clearInterval(stageInterval);
        setTimeout(() => setIsComplete(true), 500); // slight pause before verdict
      }
    }, 800);

    return () => {
      clearInterval(interval);
      clearInterval(stageInterval);
    };
  }, [file]);

  if (isComplete) {
    // Simulate a random verdict for demo purposes. 
    // Usually, you'd fetch this from a backend.
    const isSuspicious = Math.random() > 0.5; 
    return <VerdictCard isSuspicious={isSuspicious} fileName={file.name} onReset={onReset} />;
  }

  return (
    <div className="w-full max-w-2xl mx-auto border border-border bg-panel overflow-hidden shadow-2xl">
      {/* Terminal Header */}
      <div className="flex items-center gap-2 border-b border-border bg-background px-4 py-2">
        <Terminal className="h-4 w-4 text-dim" />
        <span className="text-xs font-mono text-dim tracking-wider">STEGAGUARD_EXEC // {file.name}</span>
      </div>

      {/* Terminal Body */}
      <div className="p-6 font-mono text-sm">
        <div className="min-h-[200px] flex flex-col gap-2">
          {logs.map((log, i) => (
            <div 
              key={i} 
              className={`flex items-center gap-2 ${i === logs.length - 1 ? 'text-foreground overflow-hidden whitespace-nowrap animate-typing' : 'text-dim'}`}
            >
              <span>{log}</span>
              {i < logs.length - 1 && <CheckCircle2 className="h-3 w-3 text-matrix shrink-0" />}
            </div>
          ))}
          {/* Blinking cursor */}
          {!isComplete && (
            <div className="w-2 h-4 bg-matrix animate-flicker mt-1"></div>
          )}
        </div>

        {/* Progress Bar */}
        <div className="mt-8">
          <div className="flex justify-between text-xs text-matrix mb-2">
            <span>SCAN_PROGRESS</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="h-1 w-full bg-background border border-border">
            <div 
              className="h-full bg-matrix shadow-[0_0_10px_#00FF41] transition-all duration-75"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
