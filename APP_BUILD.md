# StegaGuard — App Build Spec

> **Usage**: Give Claude this file + say "build v1" / "build v2" / "build v3". Each version builds on top of the previous one. Do NOT skip versions.

---

## CONTEXT (READ THIS FIRST EVERY TIME)

**StegaGuard** is an AI model weight integrity scanner that detects steganographic malware, backdoor triggers, and hidden payloads in deep learning model weights. Built for GE Precision Care Challenge 2026 (healthcare AI security).

**Timeline**: 2 days. Not 2 weeks. Every decision must favor "working now" over "perfect later."

**Demo format**: 10 min live demo to judges + 5 min Q&A. The app must be demo-able on a laptop with no internet dependency.

**What exists now**: A Streamlit app with MOCK data (no real scanning). We are replacing it entirely.

---

## TECH STACK

```
Backend:   Python 3.11+ / FastAPI / Uvicorn
           Libraries: safetensors, torch, onnx, numpy, scipy
           WebSocket for real-time scan progress

Frontend:  Next.js 14 (App Router) / React 18 / TypeScript
           Tailwind CSS + shadcn/ui components
           Recharts for data visualization
           Socket.io-client for WebSocket

Structure:
stegaguard/
├── backend/
│   ├── main.py                    # FastAPI app entry
│   ├── requirements.txt
│   ├── core/
│   │   ├── parser.py              # Model file parsing (.safetensors, .pt, .onnx)
│   │   ├── scanner.py             # Scan orchestrator
│   │   └── risk_scorer.py         # Weighted composite scoring
│   ├── modules/
│   │   ├── entropy.py             # Shannon entropy analysis
│   │   ├── lsb.py                 # LSB steganalysis (Chi-square)
│   │   ├── distribution.py        # KS test / distribution deviation
│   │   ├── neural_cleanse.py      # Trigger reverse-engineering
│   │   └── metadata.py            # Format-specific integrity checks
│   ├── models/                    # Pydantic schemas
│   │   ├── scan.py
│   │   └── report.py
│   └── routers/
│       ├── scan.py                # POST /scan, WS /scan/ws
│       └── report.py              # GET /report/:id
├── frontend/
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx               # Landing / upload
│   │   ├── scan/[id]/page.tsx     # Live scan view
│   │   └── report/[id]/page.tsx   # Full report
│   ├── components/
│   │   ├── upload-zone.tsx
│   │   ├── scan-progress.tsx
│   │   ├── risk-gauge.tsx
│   │   ├── layer-table.tsx
│   │   ├── entropy-chart.tsx
│   │   ├── distribution-chart.tsx
│   │   ├── trigger-heatmap.tsx
│   │   └── navbar.tsx
│   └── lib/
│       ├── api.ts
│       └── ws.ts
└── README.md
```

---

## V1 — "IT SCANS FOR REAL" (Day 1, first half)

**Goal**: Upload a real model file → backend parses it → runs real statistical analysis → returns real results → frontend shows them. No mock data anywhere. This is the foundation.

### What to build

**Backend**:

1. **`core/parser.py`** — Model file parser
   - Accept `.safetensors`: use `safetensors.numpy.load_file()` to get weight dict
   - Accept `.pt`: use `torch.load(f, map_location="cpu", weights_only=True)` then convert state_dict values to numpy
   - Accept `.onnx`: use `onnx.load()` then extract initializer tensors as numpy
   - Return: `dict[str, numpy.ndarray]` mapping layer names to weight arrays
   - Also return metadata: total params, file size, format, layer count

2. **`modules/entropy.py`** — Shannon entropy per layer
   - Flatten each weight tensor to 1D
   - Cast to bytes (view float32 as uint8, so each float = 4 bytes)
   - Compute Shannon entropy on the byte distribution: `H = -Σ p(x) * log2(p(x))`
   - Normal model weights: H ≈ 4.5–5.5. Steganographic data: H ≈ 7.5–8.0
   - Also compute LSB-only entropy: extract just the least significant byte of each float, compute H on that
   - Return: `{layer_name: {entropy: float, lsb_entropy: float, is_anomaly: bool}}`
   - Threshold for anomaly: lsb_entropy > 6.5 OR full entropy deviates more than 2σ from the model's own mean

3. **`modules/lsb.py`** — Chi-square steganalysis
   - For each layer: extract LSB plane (least significant bit of each weight's byte representation)
   - Compute Chi-square goodness-of-fit test against uniform distribution
   - `scipy.stats.chisquare()` on observed bit frequencies vs expected
   - p-value < 0.01 → non-random → possible steganographic embedding
   - Also compute the "flip ratio" — in clean weights, ~50% of adjacent LSBs differ. Steganographic data disrupts this.
   - Return: `{layer_name: {chi2_statistic: float, p_value: float, flip_ratio: float, is_anomaly: bool}}`

4. **`modules/distribution.py`** — Distribution deviation
   - For each layer: compute KS test against expected distribution
   - Conv layers: expected Kaiming normal (std = sqrt(2/fan_in))
   - Linear layers: expected Xavier normal (std = sqrt(2/(fan_in+fan_out)))
   - `scipy.stats.kstest(weights, 'norm', args=(0, expected_std))`
   - Also check for bimodal distributions (sign of payload injection): compute kurtosis, look for excess
   - Return: `{layer_name: {ks_statistic: float, p_value: float, kurtosis: float, is_anomaly: bool}}`

5. **`core/risk_scorer.py`** — Composite risk scoring
   ```
   Risk = 0.30 × max(entropy_scores) + 0.25 × max(lsb_scores) + 0.25 × max(distribution_scores) + 0.10 × mean(entropy_scores) + 0.10 × metadata_score
   ```
   - Each sub-score normalized to 0–1
   - Map to verdict: 0-25 CLEAR, 25-50 LOW, 50-75 WARNING, 75-100 CRITICAL
   - Return full breakdown showing which layers contributed most

6. **`core/scanner.py`** — Orchestrator
   - Takes parsed model dict
   - Runs each module sequentially
   - Yields progress events (for WebSocket): `{stage: "entropy", layer: "conv1.weight", progress: 0.35}`
   - Aggregates all module results into final report

7. **`main.py`** + **`routers/scan.py`** — API
   - `POST /api/scan` — Upload model file, returns scan_id, kicks off background scan
   - `WS /api/scan/{scan_id}/ws` — WebSocket that streams progress events + final result
   - `GET /api/scan/{scan_id}` — Poll for result (fallback if WS fails)
   - `GET /api/health` — Health check
   - CORS enabled for frontend dev server
   - File upload limit: 1GB
   - Store results in-memory dict (no database needed for MVP)

**Frontend**:

1. **Landing page** (`page.tsx`)
   - Hero section: StegaGuard branding, one-line description
   - Upload zone: drag-and-drop + click-to-browse, accepts .safetensors/.pt/.onnx
   - On upload: POST to backend, redirect to scan page

2. **Scan page** (`scan/[id]/page.tsx`)
   - Connect to WebSocket on mount
   - Show real-time progress: which module is running, which layer, percentage
   - Animated progress bar per module stage
   - When complete: show summary card with risk score + verdict, then link to full report

3. **Report page** (`report/[id]/page.tsx`)
   - Risk score gauge (large, prominent)
   - Executive summary text
   - Model metadata cards (architecture, params, format, hash)
   - Risk formula breakdown (bar chart showing each component's contribution)
   - Layer-level table: sortable, color-coded by status (normal/warning/critical)
   - Click a layer row to expand and see entropy + distribution details

4. **Components**: `upload-zone.tsx`, `scan-progress.tsx`, `risk-gauge.tsx`, `layer-table.tsx`

### V1 Definition of Done
- [ ] Can upload a real ResNet-50 .safetensors file (download from HuggingFace for testing)
- [ ] Backend parses it, runs entropy + LSB + distribution analysis on real weight tensors
- [ ] Frontend shows real-time scan progress via WebSocket
- [ ] Report page shows real risk score, real per-layer data, real charts
- [ ] Zero mock data anywhere in the codebase

### V1 Test Flow
```bash
# Terminal 1: Backend
cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm install && npm run dev

# Terminal 3: Get a test model
python -c "
import torchvision.models as models
import torch
model = models.resnet50(weights='IMAGENET1K_V1')
torch.save(model.state_dict(), 'test_clean.pt')
"

# Then: Open http://localhost:3000, upload test_clean.pt, watch the scan run
```

---

## V2 — "IT LOOKS IMPRESSIVE" (Day 1, second half)

**Goal**: Polish the UI to demo-grade quality. Add Neural Cleanse. Add the comparative "before/after injection" demo flow. This is what makes judges say "wow."

**Prerequisite**: V1 is fully working. Do NOT start V2 until V1 scans real models end-to-end.

### What to build

**Backend additions**:

1. **`modules/neural_cleanse.py`** — Trigger detection (simplified)
   - For a classification model: compute the "anomaly index" per output class
   - For each class, compute the mean L1 norm of the gradient of the loss w.r.t. input
   - A backdoored class has a much smaller trigger norm (easier to push into that class)
   - Anomaly index = median(norms) / norm_for_class — outlier ratio > 2.0 flags the class
   - Generate a synthetic trigger pattern: random 8x8 heatmap weighted by gradient magnitudes
   - This is a simplified version — the math still holds and the visualization is compelling
   - Return: `{class_anomaly_indices: dict, trigger_pattern: 2D array, is_suspicious: bool}`

2. **`modules/metadata.py`** — Metadata forensics
   - SafeTensors: check header for unexpected keys, padding bytes, non-tensor metadata
   - PyTorch: flag pickle-based files (code execution risk), check for unexpected objects in state_dict
   - ONNX: validate graph structure, check for custom operators, unusual opset
   - Return: `{format_warnings: list, pickle_risk: bool, extra_metadata: dict}`

3. **`POST /api/inject-demo`** — Demo injection endpoint
   - Takes a clean model + payload size (in KB)
   - Creates a copy with LSB-injected random data in the 2 largest conv layers
   - Returns the modified model as a download
   - **This is for demo purposes only** — lets us show "clean scan → inject → dirty scan" live

4. **`GET /api/report/{scan_id}/pdf`** — PDF report export
   - Use `reportlab` or `weasyprint` to generate a formatted PDF
   - Include all charts as embedded images (render with matplotlib server-side)
   - Branded header, risk score, executive summary, per-layer table, recommendations

**Frontend additions**:

1. **Dashboard polish**
   - Refined dark theme with proper design tokens
   - Smooth animations on scan progress (framer-motion or CSS transitions)
   - Risk gauge: animated arc chart, not just a number
   - Entropy chart: per-layer line chart with anomaly threshold line (Recharts)
   - Distribution chart: histogram overlay (expected vs. observed) per selected layer

2. **Trigger Heatmap** (`trigger-heatmap.tsx`)
   - Render the Neural Cleanse trigger pattern as a color heatmap
   - Anomaly index bar chart per class with threshold line

3. **Compare Mode**
   - Side-by-side view: scan two models and diff the results
   - Highlight layers where entropy/LSB scores diverge
   - Perfect for the "clean vs. injected" demo flow

4. **Report Export**
   - "Download PDF Report" button on report page
   - "Download JSON" for raw data

5. **Pre-loaded Demo Models**
   - Include 2 small pre-computed scan results that load instantly (for demo reliability)
   - Fallback if live upload takes too long during the 10-min window
   - Store as JSON fixtures in the frontend

### V2 Definition of Done
- [ ] Neural Cleanse module runs and produces trigger heatmap + anomaly indices
- [ ] Metadata forensics flags pickle-based .pt files as higher risk
- [ ] Demo injection endpoint works: clean model in → injected model out
- [ ] Full demo flow works: upload clean → scan (CLEAR) → inject → upload injected → scan (CRITICAL)
- [ ] PDF report downloads with charts and branding
- [ ] UI is polished: animations, proper typography, consistent spacing, no janky layouts
- [ ] Compare mode shows side-by-side clean vs. compromised
- [ ] Pre-loaded demo results work as fallback

---

## V3 — "WE WIN THIS" (Day 2)

**Goal**: Differentiating features that no other team will have. Demo rehearsal. Bulletproofing.

**Prerequisite**: V2 is fully working and demo-able. Do NOT start V3 until V2 demo flow runs smoothly end-to-end.

### What to build

**Backend additions**:

1. **`modules/capacity.py`** — Steganographic capacity analysis
   - For each layer: compute how much data COULD be hidden without affecting model accuracy
   - Based on ReFHD-Net paper: capacity = num_parameters × bits_per_param / 8 (bytes)
   - Conv layers: ~2 bits/param safe. Linear layers: ~1 bit/param safe. BN layers: ~0.5 bits/param
   - Show total model capacity: "This model could hide up to X MB of data"
   - This is a novel analysis that judges won't have seen from other teams

2. **Payload type identification** (add to `lsb.py`)
   - If steganographic data is detected, extract the LSB byte stream
   - Check first 16 bytes for known file signatures (magic bytes):
     - `89 50 4E 47` = PNG
     - `4D 5A` = Windows EXE/DLL
     - `50 4B` = ZIP/DOCX
     - `7F 45 4C 46` = Linux ELF
     - High entropy + no signature = likely encrypted
   - Show this in the UI: "Detected payload type: PNG image (~12.4 MB)"

3. **Architecture auto-detection**
   - From the layer names + shapes, infer the architecture family
   - Map to expected baseline distributions (ResNet, DenseNet, VGG, EfficientNet, ViT)
   - Use this to improve false-positive calibration

4. **Scan history endpoint**
   - `GET /api/scans` — List all scans in this session
   - Useful for the compare mode and demo flow

**Frontend additions**:

1. **Capacity Visualization**
   - Stacked bar chart: each layer's hiding capacity
   - Total capacity callout: "This model could conceal up to 48.2 MB"
   - If data IS detected: "3.2 MB detected / 48.2 MB capacity (6.6% utilized)"

2. **Payload Preview Card**
   - If a payload type is identified, show an icon + type + size
   - "Detected: PNG image header in layers features.8–features.10 (~12.4 MB)"

3. **Scan History Sidebar**
   - List of past scans in this session
   - Quick-compare any two

4. **"How It Works" Panel**
   - Expandable section on the report page
   - For each detection module: one-paragraph explanation + paper citation
   - Shows judges we know the science, not just the code
   - Example: "LSB Steganalysis uses the Chi-square goodness-of-fit test to detect non-random patterns in the least significant bits of weight parameters. Based on [Steganalysis of AI Models, 2024], a p-value below 0.01 indicates structured data embedding with 99% confidence."

5. **Demo Mode Toggle**
   - A button/toggle that enables "demo mode"
   - Pre-loads 3 scenarios with instant results:
     1. Clean ResNet-50 (CLEAR)
     2. Compromised AlexNet with LSB payload (CRITICAL)
     3. DenseNet-121 with mild trigger susceptibility (WARNING)
   - Falls back to these if live upload is too slow during the 10-min demo
   - In demo mode, scan "runs" with realistic timing (2-3 seconds with progress animation) using pre-computed real results

6. **Final UI Polish**
   - Loading skeletons on all async content
   - Error states with retry buttons
   - Responsive layout (works on projector resolution)
   - Print-friendly report view
   - Keyboard shortcuts for demo flow (spacebar to advance, etc.)

### V3 Definition of Done
- [ ] Capacity analysis shows per-layer hiding capacity with visualization
- [ ] Payload type identification works (test by injecting a PNG header into LSB plane)
- [ ] Architecture auto-detection infers model family from layer structure
- [ ] "How It Works" panel cites all 7 research papers in context
- [ ] Demo mode loads 3 pre-computed scenarios instantly and reliably
- [ ] Full demo rehearsal: can run the complete 10-minute flow without any crashes, loading spinners >3s, or layout glitches
- [ ] App runs fully offline on a laptop

---

## IMPORTANT RULES FOR ALL VERSIONS

1. **No mock data.** Every number shown in the UI must come from a real computation on real weight tensors. The only exception is V3 demo mode, which uses pre-computed REAL results cached as JSON.

2. **Every detection must cite its paper.** In code comments and in the "How It Works" panel, reference which paper the technique comes from.

3. **Backend-first.** Always get the backend module working and tested before building its frontend visualization. A working API with no UI beats a pretty UI with no backend.

4. **Test with real models.** Download ResNet-50 from torchvision for clean baseline. Use the injection endpoint to create a compromised version. Both must scan correctly.

5. **Fail gracefully.** If a module crashes on a specific model format, catch the error, skip that module, and still show results from the others. Never show a blank screen or unhandled error during the demo.

6. **Keep models small for demo.** ResNet-50 (.pt) is ~98MB, scans in seconds. Don't demo with a 2GB model that takes 5 minutes. Speed matters in a 10-minute window.

7. **Git commit after each version.** Tag as `v1`, `v2`, `v3` so you can always roll back.
