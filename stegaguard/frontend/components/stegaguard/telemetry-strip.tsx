import { Activity } from "lucide-react";

export default function TelemetryStrip() {
  return (
    <div className="w-full border-t border-border bg-panel mt-20">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 font-mono text-xs text-dim">
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 text-matrix animate-pulse">
              <Activity className="h-4 w-4" />
              <span>LIVE_TELEMETRY</span>
            </div>
            <div className="hidden sm:block border-l border-border h-4"></div>
            <div className="flex flex-col sm:flex-row gap-4 sm:gap-6">
              <div>
                <span className="opacity-50">SCANNED: </span>
                <span className="text-foreground">1,204,921</span>
              </div>
              <div>
                <span className="opacity-50">THREATS_BLOCKED: </span>
                <span className="text-alert">8,432</span>
              </div>
              <div>
                <span className="opacity-50">AVG_SCAN_TIME: </span>
                <span className="text-foreground">1.4s</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
            <span className="opacity-50 whitespace-nowrap">SUPPORTED_FORMATS:</span>
            <div className="flex gap-2">
              {[".safetensors", ".pt", ".pth", ".onnx"].map((ext) => (
                <span 
                  key={ext} 
                  className="bg-background border border-border px-2 py-1 text-[10px] text-foreground tracking-widest uppercase"
                >
                  {ext}
                </span>
              ))}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
