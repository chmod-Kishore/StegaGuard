export type ProgressEvent = {
  scan_id: string;
  stage: string;
  layer: string;
  progress: number;
  message: string;
};

export function connectScanWs(
  scanId: string,
  onProgress: (event: ProgressEvent) => void,
  onComplete: (result: Record<string, unknown>) => void,
  onError: (error: string) => void
): WebSocket {
  const ws = new WebSocket(`ws://localhost:8000/api/scan/${scanId}/ws`);

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.status === "failed") {
      onError(data.error || "Scan failed");
    } else if (data.status === "completed") {
      onComplete(data);
    } else if (data.stage) {
      onProgress(data);
    }
  };

  ws.onerror = () => onError("WebSocket connection error");
  ws.onclose = () => {};

  return ws;
}
