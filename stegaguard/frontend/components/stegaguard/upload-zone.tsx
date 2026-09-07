"use client";

import { useState, useCallback, useRef } from "react";
import { Upload, FileUp } from "lucide-react";
import { cn } from "@/lib/utils";

const ACCEPTED_EXTENSIONS = [".safetensors", ".pt", ".pth", ".onnx"];
const MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024; // 1GB

interface UploadZoneProps {
  onUpload: (file: File) => void;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

function isAcceptedFile(file: File): boolean {
  const name = file.name.toLowerCase();
  return ACCEPTED_EXTENSIONS.some((ext) => name.endsWith(ext));
}

export default function UploadZone({ onUpload }: UploadZoneProps) {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((file: File) => {
    setError(null);

    if (!isAcceptedFile(file)) {
      setError(`INVALID_FORMAT: [${ACCEPTED_EXTENSIONS.join(", ")}] required`);
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError(`SIZE_EXCEEDED: > 1GB limits`);
      return;
    }

    onUpload(file);
  }, [onUpload]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragOver(false);

      const file = e.dataTransfer.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <div className="w-full max-w-2xl mx-auto" id="upload-zone">
      {/* Bracketed frame */}
      <div className="relative p-[1px]">
        {/* Frame Corners */}
        <div className={cn("absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 transition-all duration-300", dragOver ? "border-matrix -translate-x-1 -translate-y-1" : "border-dim")} />
        <div className={cn("absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 transition-all duration-300", dragOver ? "border-matrix translate-x-1 -translate-y-1" : "border-dim")} />
        <div className={cn("absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 transition-all duration-300", dragOver ? "border-matrix -translate-x-1 translate-y-1" : "border-dim")} />
        <div className={cn("absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 transition-all duration-300", dragOver ? "border-matrix translate-x-1 translate-y-1" : "border-dim")} />

        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              inputRef.current?.click();
            }
          }}
          tabIndex={0}
          role="button"
          aria-label="Upload model file"
          className={cn(
            "relative flex flex-col items-center justify-center border border-dashed p-12 transition-all duration-300 cursor-pointer focus:outline-none focus:ring-2 focus:ring-matrix min-h-[44px]",
            dragOver
              ? "border-matrix bg-matrix/5"
              : "border-border bg-panel hover:bg-panel/80 hover:border-dim",
            error && "border-alert/50"
          )}
        >
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPTED_EXTENSIONS.join(",")}
            onChange={handleInputChange}
            className="hidden"
            tabIndex={-1}
          />

          {dragOver ? (
            <FileUp className="h-10 w-10 text-matrix mb-4 animate-bounce" />
          ) : (
            <Upload className="h-10 w-10 text-dim mb-4 group-hover:text-foreground transition-colors" />
          )}

          <p className="text-foreground text-lg font-mono font-medium mb-1 tracking-tight">
            {dragOver ? "> INCOMING_PAYLOAD..." : "> AWAITING_MODEL_INPUT"}
          </p>
          <p className="text-dim font-mono text-sm mb-4">
            Drag & drop or click to select [ max: 1GB ]
          </p>
          <p className="text-dim font-mono text-xs opacity-70">
            [ .safetensors | .pt | .pth | .onnx ]
          </p>
        </div>
      </div>

      {error && (
        <div className="mt-4 flex items-center gap-3 border border-alert bg-alert/10 px-4 py-3 text-sm font-mono text-alert">
          <span className="font-bold">ERR:</span>
          {error}
        </div>
      )}
    </div>
  );
}
