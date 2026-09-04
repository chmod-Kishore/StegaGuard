# StegaGuard

**AI Model Weight Integrity Scanner** — Detects steganographic malware, backdoor triggers, and hidden payloads embedded in deep learning model weights.

Built for the **GE Precision Care Challenge 2026**.

## What It Does

StegaGuard scans AI model files (`.safetensors`, `.pt/.pth`, `.onnx`) and runs real statistical analysis on every weight tensor to detect:

- **Steganographic payloads** — Chi-square analysis of LSB bit planes to detect hidden data
- **Entropy anomalies** — Shannon entropy measurement to find unnaturally high information density
- **Distribution deviations** — Kolmogorov-Smirnov tests against expected weight distributions
- **Metadata integrity** — File hash verification and structural validation

## Risk Scoring

Each layer is scored across three analysis modules, then aggregated:

```
Risk = 0.30 * max(entropy) + 0.25 * max(lsb) + 0.25 * max(distribution) + 0.10 * mean(entropy) + 0.10 * metadata
```

| Verdict  | Score Range | Meaning                          |
|----------|-------------|----------------------------------|
| CLEAR    | 0 – 25      | No anomalies detected            |
| LOW      | 25 – 50     | Minor deviations, likely benign  |
| WARNING  | 50 – 75     | Significant anomalies found      |
| CRITICAL | 75 – 100    | High confidence of tampering     |

## Architecture

```
┌─────────────────────────────────────────────┐
│  Frontend (Next.js 14 / React 18)           │
│  - Upload zone with drag-and-drop           │
│  - Real-time scan progress (WebSocket)      │
│  - Interactive report with charts & tables   │
└──────────────────┬──────────────────────────┘
                   │ HTTP + WebSocket
┌──────────────────▼──────────────────────────┐
│  Backend (FastAPI / Python 3.12)            │
│  - Model parser (safetensors/torch/onnx)    │
│  - Entropy, LSB, Distribution modules       │
│  - Composite risk scoring engine            │
└─────────────────────────────────────────────┘
```

## Prerequisites

- **Python** 3.10+ (tested on 3.12)
- **Node.js** 18+ (tested on 22.x)
- **npm** 9+
- ~2 GB disk space (PyTorch CPU is ~1.2 GB)

## Quick Start

### 1. Clone

```bash
git clone https://github.com/chmod-Kishore/StegaGuard.git
cd StegaGuard
```

### 2. Backend

```bash
cd stegaguard/backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate       # Linux / macOS
# venv\Scripts\activate        # Windows

# Install PyTorch CPU-only first (saves ~1 GB vs CUDA build)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install the rest
pip install -r requirements.txt
```

### 3. Frontend

```bash
cd stegaguard/frontend
npm install
```

### 4. Run

Open **two terminals** from the project root:

**Terminal 1 — Backend** (port 8000):
```bash
cd stegaguard/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend** (port 3000):
```bash
cd stegaguard/frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

## Usage

1. Open http://localhost:3000
2. Drag-and-drop a model file (`.safetensors`, `.pt`, `.pth`, or `.onnx`) onto the upload zone
3. Watch real-time scan progress as each analysis module runs
4. View the full report with:
   - Risk score gauge and verdict
   - Executive summary
   - Model metadata (filename, format, params, SHA-256 hash)
   - Risk breakdown chart (entropy / LSB / distribution contributions)
   - Per-layer entropy chart with anomaly threshold line
   - Sortable layer table with expandable detail rows

## Generate a Test Model

No test model is included in the repo. Generate one with:

```bash
pip install safetensors numpy
python3 -c "
import numpy as np
from safetensors.numpy import save_file

tensors = {}
for name in ['conv1.weight', 'conv1.bias', 'bn1.weight', 'bn1.bias',
             'layer1.weight', 'layer1.bias', 'layer2.weight', 'layer2.bias',
             'layer3.weight', 'layer3.bias', 'fc.weight', 'fc.bias', 'fc2.weight']:
    if 'bias' in name:
        tensors[name] = np.random.randn(64).astype(np.float32)
    elif 'fc' in name:
        tensors[name] = np.random.randn(512, 256).astype(np.float32)
    else:
        tensors[name] = np.random.randn(64, 64, 3, 3).astype(np.float32)

save_file(tensors, 'test_model.safetensors')
print(f'Created test_model.safetensors ({sum(t.size for t in tensors.values()):,} params)')
"
```

Then upload `test_model.safetensors` through the UI.

## API Endpoints

| Method | Endpoint               | Description                    |
|--------|------------------------|--------------------------------|
| GET    | `/api/health`          | Health check                   |
| POST   | `/api/scan`            | Upload model file, start scan  |
| GET    | `/api/scan/{id}`       | Poll scan status / result      |
| WS     | `/api/scan/{id}/ws`    | Real-time scan progress stream |
| GET    | `/api/report/{id}`     | Formatted scan report          |

## Project Structure

```
stegaguard/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── requirements.txt
│   ├── core/
│   │   ├── parser.py            # Model file parser (safetensors / torch / onnx)
│   │   ├── scanner.py           # Async scan orchestrator
│   │   └── risk_scorer.py       # Composite risk scoring engine
│   ├── modules/
│   │   ├── entropy.py           # Shannon entropy analysis
│   │   ├── lsb.py               # Chi-square LSB steganalysis
│   │   └── distribution.py      # KS distribution deviation testing
│   ├── models/
│   │   └── scan.py              # Pydantic schemas
│   └── routers/
│       ├── scan.py              # Upload, poll, WebSocket endpoints
│       └── report.py            # Report endpoint
└── frontend/
    ├── app/
    │   ├── layout.tsx           # Root layout with navbar
    │   ├── globals.css          # Tailwind + dark theme
    │   ├── page.tsx             # Landing page with upload zone
    │   ├── scan/[id]/page.tsx   # Live scan progress page
    │   └── report/[id]/page.tsx # Full report page
    ├── components/
    │   ├── upload-zone.tsx      # Drag-and-drop file upload
    │   ├── risk-gauge.tsx       # SVG semicircle risk gauge
    │   ├── layer-table.tsx      # Sortable layer results table
    │   ├── entropy-chart.tsx    # Recharts entropy bar chart
    │   └── ui/                  # shadcn/ui base components
    ├── lib/
    │   ├── api.ts               # Backend API client
    │   ├── ws.ts                # WebSocket connection
    │   └── utils.ts             # cn() utility
    ├── package.json
    ├── tailwind.config.ts
    └── tsconfig.json
```

## Tech Stack

| Layer     | Stack                                                    |
|-----------|----------------------------------------------------------|
| Backend   | Python 3.12, FastAPI, Uvicorn, PyTorch (CPU), SciPy     |
| Frontend  | Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts |
| Transport | REST + WebSocket (with polling fallback)                 |

## Team

- Kishore K
- Jeswin Tobias J
