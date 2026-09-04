"use client";

import { useRouter } from "next/navigation";
import { Shield } from "lucide-react";
import UploadZone from "@/components/upload-zone";
import { uploadModel } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();

  async function handleUpload(file: File) {
    const { scan_id } = await uploadModel(file);
    router.push(`/scan/${scan_id}`);
  }

  return (
    <div className="flex flex-col items-center justify-center px-4 py-20 sm:py-28">
      {/* Hero */}
      <div className="mb-12 flex flex-col items-center text-center">
        <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-blue-600/10 ring-1 ring-blue-500/20">
          <Shield className="h-10 w-10 text-blue-500" />
        </div>
        <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">
          StegaGuard
        </h1>
        <p className="mt-3 text-lg text-gray-400 sm:text-xl">
          AI Model Weight Integrity Scanner
        </p>
        <p className="mt-4 max-w-2xl text-sm leading-relaxed text-gray-500 sm:text-base">
          Detect steganographic malware, backdoor triggers, and hidden payloads
          in deep learning model weights
        </p>
      </div>

      {/* Upload Zone */}
      <UploadZone onUpload={handleUpload} />

      {/* Supported Formats */}
      <p className="mt-8 text-xs text-gray-600">
        Supported formats:{" "}
        <span className="text-gray-500">
          .safetensors, .pt, .pth, .onnx
        </span>
      </p>
    </div>
  );
}
