"use client";

import { useState, useCallback, useRef } from "react";
import { Upload, FileUp, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const ACCEPTED_EXTENSIONS = [".safetensors", ".pt", ".pth", ".onnx"];
const MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024; // 1GB

interface UploadZoneProps {
  onUpload: (file: File) => Promise<void>;
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
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((file: File) => {
    setError(null);

    if (!isAcceptedFile(file)) {
      setError(
        `Invalid file type. Accepted formats: ${ACCEPTED_EXTENSIONS.join(", ")}`
      );
      setSelectedFile(null);
      return;
    }

    if (file.size > MAX_FILE_SIZE) {
      setError(`File too large. Maximum size is 1 GB.`);
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  }, []);

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      if (!uploading) setDragOver(true);
    },
    [uploading]
  );

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
      if (uploading) return;

      const file = e.dataTransfer.files?.[0];
      if (file) handleFile(file);
    },
    [uploading, handleFile]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleUpload = useCallback(async () => {
    if (!selectedFile || uploading) return;
    setUploading(true);
    setError(null);
    try {
      await onUpload(selectedFile);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed. Please try again.");
    } finally {
      setUploading(false);
    }
  }, [selectedFile, uploading, onUpload]);

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          "relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-10 transition-all duration-200 cursor-pointer",
          dragOver
            ? "border-blue-500 bg-blue-500/10"
            : "border-gray-700 bg-gray-900 hover:border-gray-500 hover:bg-gray-900/80",
          uploading && "pointer-events-none opacity-60",
          error && "border-red-500/50"
        )}
        onClick={() => !uploading && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_EXTENSIONS.join(",")}
          onChange={handleInputChange}
          className="hidden"
          disabled={uploading}
        />

        {uploading ? (
          <Loader2 className="h-12 w-12 text-blue-400 animate-spin mb-4" />
        ) : dragOver ? (
          <FileUp className="h-12 w-12 text-blue-400 mb-4" />
        ) : (
          <Upload className="h-12 w-12 text-gray-500 mb-4" />
        )}

        <p className="text-gray-300 text-lg font-medium mb-1">
          {uploading
            ? "Uploading..."
            : dragOver
            ? "Drop your model file here"
            : "Drag & drop your model file here"}
        </p>
        <p className="text-gray-500 text-sm mb-4">
          Supports {ACCEPTED_EXTENSIONS.join(", ")} (max 1 GB)
        </p>

        {!uploading && !selectedFile && (
          <button
            type="button"
            className="rounded-lg bg-gray-800 px-5 py-2 text-sm font-medium text-gray-300 hover:bg-gray-700 hover:text-white transition-colors border border-gray-700"
            onClick={(e) => {
              e.stopPropagation();
              inputRef.current?.click();
            }}
          >
            Browse Files
          </button>
        )}
      </div>

      {error && (
        <div className="mt-3 rounded-lg bg-red-900/30 border border-red-800 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {selectedFile && !uploading && (
        <div className="mt-4 flex items-center justify-between rounded-lg bg-gray-800/60 border border-gray-700 px-4 py-3">
          <div className="flex items-center gap-3 min-w-0">
            <FileUp className="h-5 w-5 text-blue-400 shrink-0" />
            <div className="min-w-0">
              <p className="text-sm font-medium text-gray-200 truncate">
                {selectedFile.name}
              </p>
              <p className="text-xs text-gray-500">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleUpload}
            className="ml-4 shrink-0 rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-500 transition-colors"
          >
            Upload & Scan
          </button>
        </div>
      )}
    </div>
  );
}
