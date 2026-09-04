const API_BASE = "http://localhost:8000/api";

export async function uploadModel(file: File): Promise<{ scan_id: string }> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/scan`, { method: "POST", body: formData });
  if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
  return res.json();
}

export async function getScanResult(scanId: string) {
  const res = await fetch(`${API_BASE}/scan/${scanId}`);
  if (!res.ok) throw new Error(`Fetch failed: ${res.statusText}`);
  return res.json();
}

export function getWsUrl(scanId: string): string {
  return `ws://localhost:8000/api/scan/${scanId}/ws`;
}
