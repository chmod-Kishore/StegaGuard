# StegaGuard

**AI Model Weight Integrity Scanner** — Detects steganographic malware and backdoor triggers hidden in neural network weight tensors.

Built for the **GE Precision Care Challenge 2026**.

## What It Does

StegaGuard scans AI model files (.safetensors, .pt, .onnx) for:

- **Steganographic payloads** — hidden data embedded in weight LSB planes
- **Backdoor triggers** — Neural Cleanse-inspired reverse-engineering of adversarial triggers
- **Integrity anomalies** — entropy spikes, distribution deviations, suspicious metadata

## Risk Scoring

```
Risk = 0.30(Entropy) + 0.25(LSB) + 0.20(Distribution) + 0.15(Trigger) + 0.10(Metadata)
```

## Supported Models

| Architecture | Format | Demo File |
|---|---|---|
| ResNet-50 | SafeTensors | `resnet50_chestXray_v2.safetensors` |
| AlexNet | PyTorch (.pt) | `alexnet_evilmodel_injected.pt` |
| DenseNet-121 | ONNX | `densenet121_pathology_v3.onnx` |

## Running the Prototype

```bash
pip install streamlit pandas numpy plotly
streamlit run app.py
```

Select a model from the sidebar and click **Run Security Scan**.

## Features

- Interactive Streamlit dashboard with dark theme
- Plotly visualizations (entropy heatmaps, distribution histograms, risk gauges)
- Neural Cleanse trigger pattern analysis
- Layer-level diagnostics with Chi-square steganalysis
- JSON/Text report export for security team integration

## Detection Pipeline

```
Parse → Entropy Analysis → LSB Steganalysis → Neural Cleanse → Risk Scoring
```

## Team

- Kishore K
- Jeswin Tobias J
