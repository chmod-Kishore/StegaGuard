"use client";

import { useState } from "react";
import TopBar from "@/components/stegaguard/top-bar";
import Hero from "@/components/stegaguard/hero";
import UploadZone from "@/components/stegaguard/upload-zone";
import ScanTerminal from "@/components/stegaguard/scan-terminal";
import TelemetryStrip from "@/components/stegaguard/telemetry-strip";

export default function HomePage() {
  const [fileToScan, setFileToScan] = useState<File | null>(null);

  return (
    <div className="flex flex-col min-h-screen">
      <TopBar />
      
      <div className="flex-1 flex flex-col pt-12 pb-24">
        {!fileToScan && <Hero />}

        <div className="flex-1 flex flex-col items-center justify-center px-4 w-full mt-8">
          {!fileToScan ? (
            <UploadZone onUpload={setFileToScan} />
          ) : (
            <ScanTerminal 
              file={fileToScan} 
              onReset={() => setFileToScan(null)} 
            />
          )}
        </div>
      </div>

      <TelemetryStrip />

      <footer className="w-full bg-background py-6 text-center text-dim font-mono text-xs border-t border-border">
        StegaGuard Framework v2.4.1 // DEPLOYMENT_ACTIVE // PROD_ENVIRONMENT
      </footer>
    </div>
  );
}
