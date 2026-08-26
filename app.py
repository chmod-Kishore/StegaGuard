import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import json
from datetime import datetime

st.set_page_config(
    page_title="StegaGuard | AI Model Integrity Scanner",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- DESIGN SYSTEM CSS ---
st.markdown("""
<style>
:root {
    --bg-primary: #0e1117;
    --bg-card: #1a1f2e;
    --bg-card-hover: #1e2538;
    --border: #2d3748;
    --border-light: #4a5568;
    --text-primary: #e2e8f0;
    --text-secondary: #a0aec0;
    --text-muted: #718096;
    --accent: #667eea;
    --accent-glow: rgba(102, 126, 234, 0.3);
    --success: #38a169;
    --success-bg: #1b2d1b;
    --warning: #ecc94b;
    --warning-bg: #2d2d1b;
    --danger: #e53e3e;
    --danger-bg: #2d1b1b;
    --danger-glow: rgba(229, 62, 62, 0.4);
}

.stApp { background-color: var(--bg-primary); }

/* Hide default Streamlit header padding */
.block-container { padding-top: 2rem !important; }

/* Gradient divider */
.gradient-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    margin: 1.5rem 0;
    border: none;
}

/* Card system */
.sg-card {
    background: linear-gradient(135deg, var(--bg-card) 0%, #16192b 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 0.5rem 0;
    transition: border-color 0.2s;
}
.sg-card:hover { border-color: var(--accent); }

/* Risk banners */
.risk-critical {
    background: linear-gradient(135deg, #2d1b1b 0%, #1a0f0f 100%);
    border: 2px solid var(--danger);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    text-align: center;
    box-shadow: 0 0 30px var(--danger-glow);
    animation: pulse-danger 2s ease-in-out infinite;
}
@keyframes pulse-danger {
    0%, 100% { box-shadow: 0 0 20px var(--danger-glow); }
    50% { box-shadow: 0 0 40px var(--danger-glow), 0 0 60px rgba(229, 62, 62, 0.2); }
}

.risk-clear {
    background: linear-gradient(135deg, #1b2d1b 0%, #0f1a0f 100%);
    border: 2px solid var(--success);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    text-align: center;
    box-shadow: 0 0 20px rgba(56, 161, 105, 0.2);
}

/* Executive summary */
.exec-summary {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--danger);
    border-radius: 0 12px 12px 0;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
}
.exec-summary-clear {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--success);
    border-radius: 0 12px 12px 0;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
}

/* Metadata chips */
.meta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin: 1rem 0;
}
.meta-chip {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
}
.meta-chip-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 0.3rem;
}
.meta-chip-value {
    font-size: 0.95rem;
    color: var(--text-primary);
    font-weight: 500;
}

/* Formula rows */
.formula-row {
    background: var(--bg-card);
    border-left: 4px solid var(--accent);
    padding: 0.8rem 1.2rem;
    margin: 0.3rem 0;
    border-radius: 0 8px 8px 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.alert-row {
    background: var(--danger-bg);
    border-left: 4px solid var(--danger);
    padding: 0.8rem 1.2rem;
    margin: 0.3rem 0;
    border-radius: 0 8px 8px 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Recommendations table */
.rec-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 6px;
}
.rec-table th {
    text-align: left;
    padding: 0.7rem 1rem;
    color: var(--text-muted);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid var(--border);
}
.rec-table td {
    padding: 0.8rem 1rem;
    background: var(--bg-card);
    color: var(--text-primary);
    font-size: 0.9rem;
}
.rec-table tr td:first-child { border-radius: 8px 0 0 8px; }
.rec-table tr td:last-child { border-radius: 0 8px 8px 0; }

.priority-badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
}
.priority-p0 { background: var(--danger-bg); color: #fc8181; border: 1px solid var(--danger); }
.priority-p1 { background: var(--warning-bg); color: #ecc94b; border: 1px solid #b7791f; }
.priority-p2 { background: var(--success-bg); color: #68d391; border: 1px solid var(--success); }
.priority-info { background: var(--success-bg); color: #68d391; border: 1px solid var(--success); }

/* Landing page */
.landing-hero {
    text-align: center;
    padding: 3rem 2rem;
    background: linear-gradient(135deg, var(--bg-card) 0%, #12162a 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    margin: 1rem 0;
}
.landing-hero h1 { font-size: 2.5rem; margin: 0; }
.landing-hero .subtitle { color: var(--text-secondary); font-size: 1.1rem; margin-top: 0.5rem; }

.feature-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: transform 0.2s, border-color 0.2s;
    height: 100%;
}
.feature-card:hover { transform: translateY(-2px); border-color: var(--accent); }
.feature-card .icon { font-size: 2rem; margin-bottom: 0.8rem; }
.feature-card h4 { color: var(--text-primary); margin: 0 0 0.5rem 0; font-size: 1rem; }
.feature-card p { color: var(--text-secondary); font-size: 0.85rem; margin: 0; line-height: 1.4; }

/* Pipeline steps */
.pipeline-step {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-secondary);
    font-size: 0.85rem;
}
.pipeline-arrow { color: var(--accent); font-size: 1.2rem; }

/* Section headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1.5rem 0 1rem 0;
}
.section-header h3 {
    margin: 0;
    color: var(--text-primary);
    font-size: 1.2rem;
}

/* Footer */
.sg-footer {
    text-align: center;
    padding: 1.5rem;
    color: var(--text-muted);
    font-size: 0.8rem;
    border-top: 1px solid var(--border);
    margin-top: 2rem;
}

/* Sidebar styling */
.sidebar-brand {
    text-align: center;
    padding: 1rem 0;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}
.sidebar-brand h2 { margin: 0; font-size: 1.3rem; color: var(--text-primary); }
.sidebar-brand p { margin: 0.2rem 0 0 0; font-size: 0.75rem; color: var(--text-muted); }

.sidebar-version {
    text-align: center;
    padding: 0.8rem;
    margin-top: 1rem;
    background: var(--bg-card);
    border-radius: 8px;
    font-size: 0.7rem;
    color: var(--text-muted);
}

/* Scan status header */
.scan-status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.6rem 1.2rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 1.5rem;
    font-size: 0.85rem;
}
.scan-status-bar .status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 0.5rem;
}
.status-dot-red { background: var(--danger); box-shadow: 0 0 6px var(--danger); }
.status-dot-green { background: var(--success); box-shadow: 0 0 6px var(--success); }
</style>
""", unsafe_allow_html=True)

# --- MOCK DATA ---

CLEAN_MODEL = {
    "name": "resnet50_chestXray_v2.safetensors",
    "risk_score": 12,
    "status": "CLEAR",
    "status_color": "#38a169",
    "architecture": "ResNet-50 (Medical Imaging)",
    "parameters": "25.6M",
    "file_size": "97.4 MB",
    "format": "SafeTensors v0.4.3",
    "hash": "sha256:a4f8c2e9...b7d1",
    "summary": "All integrity checks passed. Model weights exhibit expected statistical properties with no anomalous patterns in any layer.",
    "formula": {
        "Entropy Anomaly": {"weight": 0.30, "score": 0.08, "detail": "Normal Gaussian distribution"},
        "LSB Pattern Score": {"weight": 0.25, "score": 0.05, "detail": "Chi-Square p = 0.847 (random)"},
        "Distribution Deviation": {"weight": 0.20, "score": 0.12, "detail": "Within 1σ of expected"},
        "Trigger Susceptibility": {"weight": 0.15, "score": 0.04, "detail": "No anomalous activation clusters"},
        "Metadata Flags": {"weight": 0.10, "score": 0.10, "detail": "Clean metadata, no padding"},
    },
    "layers": pd.DataFrame({
        "Layer": ["layer1.conv1.weight", "layer2.conv2.weight", "layer3.bottleneck.weight",
                  "layer4.conv3.weight", "fc.weight"],
        "Type": ["Conv2D", "Conv2D", "Conv2D", "Conv2D", "Linear"],
        "Parameters": ["9,408", "36,864", "589,824", "2,359,296", "2,048,000"],
        "Entropy (H)": [4.82, 4.91, 4.88, 4.85, 4.79],
        "LSB Chi² p-value": [0.72, 0.68, 0.81, 0.77, 0.65],
        "Status": ["✅ Normal", "✅ Normal", "✅ Normal", "✅ Normal", "✅ Normal"],
    }),
}

COMPROMISED_MODEL = {
    "name": "alexnet_evilmodel_injected.pt",
    "risk_score": 87,
    "status": "CRITICAL",
    "status_color": "#e53e3e",
    "architecture": "AlexNet (Modified)",
    "parameters": "61.1M",
    "file_size": "244.2 MB",
    "format": "PyTorch v2.1 (pickle)",
    "hash": "sha256:f1c3d8a7...9e2b",
    "summary": "CRITICAL: 12.4 MB steganographic payload detected in layers features.8 and features.10. Encrypted PNG data embedded via LSB replacement. Immediate quarantine recommended.",
    "formula": {
        "Entropy Anomaly": {"weight": 0.30, "score": 0.92, "detail": "Bimodal spike in layers 8-11"},
        "LSB Pattern Score": {"weight": 0.25, "score": 0.98, "detail": "Chi-Square p < 0.001 (non-random)"},
        "Distribution Deviation": {"weight": 0.20, "score": 0.65, "detail": "3.7σ deviation in conv layers"},
        "Trigger Susceptibility": {"weight": 0.15, "score": 0.15, "detail": "Mild activation clustering"},
        "Metadata Flags": {"weight": 0.10, "score": 0.80, "detail": "Suspicious 12.4 MB padding block"},
    },
    "layers": pd.DataFrame({
        "Layer": ["features.0.weight", "features.3.weight", "features.6.weight",
                  "features.8.weight", "features.10.weight", "classifier.1.weight", "classifier.4.weight"],
        "Type": ["Conv2D", "Conv2D", "Conv2D", "Conv2D", "Conv2D", "Linear", "Linear"],
        "Parameters": ["23,296", "307,200", "884,736", "1,327,104", "884,736", "37,748,736", "16,777,216"],
        "Entropy (H)": [4.85, 4.90, 4.88, 7.91, 7.99, 4.82, 4.80],
        "LSB Chi² p-value": [0.71, 0.65, 0.74, 0.0003, 0.00001, 0.69, 0.72],
        "Status": ["✅ Normal", "✅ Normal", "✅ Normal", "🚨 ANOMALY", "🚨 CRITICAL", "✅ Normal", "✅ Normal"],
    }),
}

ONNX_MODEL = {
    "name": "densenet121_pathology_v3.onnx",
    "risk_score": 41,
    "status": "WARNING",
    "status_color": "#ecc94b",
    "architecture": "DenseNet-121 (Pathology)",
    "parameters": "7.9M",
    "file_size": "31.6 MB",
    "format": "ONNX v1.14 (opset 17)",
    "hash": "sha256:c7e2a91f...4d8a",
    "summary": "WARNING: Elevated trigger susceptibility detected in dense_block3. Activation clustering suggests possible backdoor pattern. Manual review recommended before deployment.",
    "formula": {
        "Entropy Anomaly": {"weight": 0.30, "score": 0.22, "detail": "Slight deviation in block3"},
        "LSB Pattern Score": {"weight": 0.25, "score": 0.18, "detail": "Chi-Square p = 0.312 (borderline)"},
        "Distribution Deviation": {"weight": 0.20, "score": 0.35, "detail": "1.8σ deviation in transition layers"},
        "Trigger Susceptibility": {"weight": 0.15, "score": 0.72, "detail": "Activation clustering in 3 classes"},
        "Metadata Flags": {"weight": 0.10, "score": 0.15, "detail": "Minor graph optimization artifacts"},
    },
    "layers": pd.DataFrame({
        "Layer": ["dense_block1.weight", "transition1.weight", "dense_block2.weight",
                  "transition2.weight", "dense_block3.weight", "transition3.weight", "classifier.weight"],
        "Type": ["Conv2D", "Conv2D+BN", "Conv2D", "Conv2D+BN", "Conv2D", "Conv2D+BN", "Linear"],
        "Parameters": ["9,408", "32,768", "147,456", "131,072", "802,816", "524,288", "1,000"],
        "Entropy (H)": [4.81, 4.87, 4.85, 4.90, 5.62, 4.88, 4.76],
        "LSB Chi² p-value": [0.74, 0.69, 0.71, 0.58, 0.12, 0.66, 0.80],
        "Status": ["✅ Normal", "✅ Normal", "✅ Normal", "✅ Normal", "⚠️ WARNING", "✅ Normal", "✅ Normal"],
    }),
}

# --- HEADER ---
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 1rem; margin-bottom: 0.5rem;">
    <div>
        <h1 style="margin: 0; font-size: 2rem; color: var(--text-primary);">🛡️ StegaGuard</h1>
        <p style="margin: 0.2rem 0 0 0; color: var(--text-secondary); font-size: 0.95rem;">AI Model Weight Integrity Scanner — Steganographic payload & backdoor trigger detection</p>
    </div>
    <div style="background: var(--bg-card); border: 1px solid var(--border-light); border-radius: 8px; padding: 0.5rem 1rem; font-size: 0.75rem; color: var(--text-muted);">
        GE Precision Care Challenge 2026 &nbsp;│&nbsp; Pipeline v1.0
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>🛡️ StegaGuard</h2>
        <p>Model Integrity Scanner</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Scan Configuration")

    model_choice = st.selectbox(
        "Select Model for Analysis",
        [
            "resnet50_chestXray_v2.safetensors",
            "alexnet_evilmodel_injected.pt",
            "densenet121_pathology_v3.onnx",
        ],
        help="Choose a model file to run the integrity pipeline against.",
    )

    st.markdown("")
    st.markdown("**Pipeline Modules**")
    modules = [
        "✅ Entropy Analysis",
        "✅ LSB Steganalysis",
        "✅ Neural Cleanse (Trigger Detection)",
        "✅ Metadata Forensics",
        "✅ Distribution Profiling",
    ]
    for m in modules:
        st.markdown(f"<span style='font-size: 0.85rem; color: var(--text-secondary);'>{m}</span>", unsafe_allow_html=True)

    st.markdown("")
    sensitivity = st.slider("Detection Sensitivity", 1, 10, 7, help="Higher = more aggressive flagging")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    scan_button = st.button("🚀 Run Security Scan", width="stretch", type="primary")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("##### About")
    st.markdown(
        "<span style='font-size: 0.85rem; color: var(--text-secondary);'>"
        "StegaGuard protects healthcare AI pipelines by scanning model weights "
        "for hidden steganographic payloads, backdoor triggers, and integrity violations "
        "before deployment to clinical systems.</span>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class="sidebar-version">
        StegaGuard v1.0.0 &nbsp;│&nbsp; Build 2026.08<br>
        Sensitivity: Adaptive &nbsp;│&nbsp; Engine: PyTorch + NumPy
    </div>
    """, unsafe_allow_html=True)

# --- MAIN AREA ---

if scan_button:
    if "resnet50" in model_choice:
        model = CLEAN_MODEL
    elif "densenet" in model_choice:
        model = ONNX_MODEL
    else:
        model = COMPROMISED_MODEL

    st.markdown("### ⏳ Running StegaGuard Pipeline...")
    progress = st.progress(0)
    status_text = st.empty()

    steps = [
        ("🔍 Parsing tensor architecture and metadata...", 15),
        ("🧠 Computing Shannon entropy across {:,}+ parameters...".format(
            int(float(model["parameters"].replace("M", "")) * 1_000_000) // 100 * 100), 35),
        ("🔐 Running LSB (Least Significant Bit) Steganalysis...", 60),
        ("⚡ Optimizing trigger susceptibility (Neural Cleanse)...", 82),
        ("📊 Aggregating Risk Score...", 100),
    ]

    for step_msg, pct in steps:
        status_text.markdown(f"**{step_msg}**")
        time.sleep(0.7)
        progress.progress(pct)

    time.sleep(0.3)
    progress.empty()
    status_text.empty()

    st.session_state["scan_done"] = True
    st.session_state["model"] = model
    st.session_state["scan_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.toast("✅ Scan complete!", icon="🛡️")
    st.rerun()

if st.session_state.get("scan_done"):
    model = st.session_state["model"]
    is_compromised = model["risk_score"] > 50
    scan_time = st.session_state.get("scan_time", "N/A")

    # --- SCAN STATUS BAR ---
    dot_class = "status-dot-red" if is_compromised else "status-dot-green"
    status_label = "THREAT DETECTED" if is_compromised else "ALL CLEAR"
    st.markdown(f"""
<div class="scan-status-bar">
    <span><span class="status-dot {dot_class}"></span> <strong>{status_label}</strong> &nbsp;—&nbsp; {model['name']}</span>
    <span style="color: var(--text-muted);">Scanned: {scan_time} &nbsp;│&nbsp; Sensitivity: 7/10</span>
</div>
""", unsafe_allow_html=True)

    # --- RISK SCORE BANNER ---
    if is_compromised:
        st.markdown(f"""
<div class="risk-critical">
    <h1 style="color: #fc8181; margin: 0; font-size: 4rem; font-weight: 700;">{model['risk_score']}<span style="font-size: 1.5rem; color: #a0aec0; font-weight: 400;">/100</span></h1>
    <p style="color: #fc8181; font-size: 1.3rem; font-weight: 600; margin: 0.8rem 0 0.3rem 0;">⛔ CRITICAL — STEGANOGRAPHIC PAYLOAD DETECTED</p>
    <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">Model: <code>{model['name']}</code> &nbsp;│&nbsp; Hash: <code>{model['hash']}</code></p>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div class="risk-clear">
    <h1 style="color: #68d391; margin: 0; font-size: 4rem; font-weight: 700;">{model['risk_score']}<span style="font-size: 1.5rem; color: #a0aec0; font-weight: 400;">/100</span></h1>
    <p style="color: #68d391; font-size: 1.3rem; font-weight: 600; margin: 0.8rem 0 0.3rem 0;">✅ CLEAR — No Integrity Violations Detected</p>
    <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">Model: <code>{model['name']}</code> &nbsp;│&nbsp; Hash: <code>{model['hash']}</code></p>
</div>
""", unsafe_allow_html=True)

    # --- EXECUTIVE SUMMARY ---
    summary_class = "exec-summary" if is_compromised else "exec-summary-clear"
    icon = "⚠️" if is_compromised else "ℹ️"
    st.markdown(f"""
<div class="{summary_class}">
    <strong>{icon} Executive Summary:</strong> {model['summary']}
</div>
""", unsafe_allow_html=True)

    # --- MODEL METADATA ---
    st.markdown('<div class="section-header"><h3>📋 Model Metadata</h3></div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="meta-grid">
    <div class="meta-chip">
        <div class="meta-chip-label">Architecture</div>
        <div class="meta-chip-value">{model['architecture']}</div>
    </div>
    <div class="meta-chip">
        <div class="meta-chip-label">Parameters</div>
        <div class="meta-chip-value">{model['parameters']}</div>
    </div>
    <div class="meta-chip">
        <div class="meta-chip-label">File Size</div>
        <div class="meta-chip-value">{model['file_size']}</div>
    </div>
    <div class="meta-chip">
        <div class="meta-chip-label">Format</div>
        <div class="meta-chip-value">{model['format']}</div>
    </div>
    <div class="meta-chip">
        <div class="meta-chip-label">SHA-256 Hash</div>
        <div class="meta-chip-value" style="font-family: monospace; font-size: 0.85rem;">{model['hash']}</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # --- FORMULA BREAKDOWN ---
    st.markdown('<div class="section-header"><h3>🧮 Risk Formula Breakdown</h3></div>', unsafe_allow_html=True)
    status_color = model["status_color"]
    risk_score = model["risk_score"]
    st.markdown(f"<p style='color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 1rem;'>Composite Risk Score = Σ (Component Score × Weight) &nbsp;→&nbsp; <strong style='color: {status_color};'>{risk_score}/100</strong></p>", unsafe_allow_html=True)

    formula = model["formula"]

    col_gauge, col_bars = st.columns([1, 2])

    with col_gauge:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=model["risk_score"],
            number={"suffix": "/100", "font": {"size": 42, "color": "white"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#4a5568", "dtick": 25, "tickfont": {"color": "#718096"}},
                "bar": {"color": model["status_color"], "thickness": 0.8},
                "bgcolor": "#1a1f2e",
                "bordercolor": "#2d3748",
                "steps": [
                    {"range": [0, 30], "color": "#1b2d1b"},
                    {"range": [30, 60], "color": "#2d2d1b"},
                    {"range": [60, 100], "color": "#2d1b1b"},
                ],
                "threshold": {
                    "line": {"color": "#fff", "width": 3},
                    "thickness": 0.8,
                    "value": model["risk_score"],
                },
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "white"},
            height=280,
            margin=dict(t=30, b=10, l=30, r=30),
        )
        st.plotly_chart(fig_gauge, width="stretch")

    with col_bars:
        components = list(formula.keys())
        scores = [formula[c]["score"] for c in components]
        weights = [formula[c]["weight"] for c in components]
        colors = ["#e53e3e" if s > 0.7 else "#ecc94b" if s > 0.4 else "#38a169" for s in scores]

        fig_bars = go.Figure()
        fig_bars.add_trace(go.Bar(
            y=components,
            x=scores,
            orientation="h",
            marker_color=colors,
            text=[f"{s:.2f} (×{w:.0%})" for s, w in zip(scores, weights)],
            textposition="auto",
            textfont={"color": "white", "size": 13},
        ))
        fig_bars.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#1a1f2e",
            font={"color": "#e2e8f0"},
            xaxis={"range": [0, 1.05], "title": "Score (0–1)", "gridcolor": "#2d3748", "title_font": {"size": 12}},
            yaxis={"gridcolor": "#2d3748", "tickfont": {"size": 11}},
            height=300,
            margin=dict(t=10, b=40, l=10, r=20),
        )
        st.plotly_chart(fig_bars, width="stretch")

    # Component detail rows
    rows_html = ""
    for comp, data in formula.items():
        severity_icon = "🔴" if data["score"] > 0.7 else "🟡" if data["score"] > 0.4 else "🟢"
        row_class = "alert-row" if data["score"] > 0.7 else "formula-row"
        rows_html += (
            f'<div class="{row_class}">'
            f'{severity_icon} <strong>{comp}</strong> &nbsp;(Weight: {data["weight"]:.0%}) &nbsp;—&nbsp; '
            f'Score: <code>{data["score"]:.2f}</code> &nbsp;│&nbsp; {data["detail"]}</div>'
        )
    st.markdown(rows_html, unsafe_allow_html=True)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # --- VISUAL EVIDENCE ---
    st.markdown('<div class="section-header"><h3>📊 Visual Evidence</h3></div>', unsafe_allow_html=True)

    if is_compromised:
        ev1, ev2 = st.columns(2)

        with ev1:
            np.random.seed(42)
            clean_dist = np.random.normal(0, 0.02, 50000)
            compromised_dist = np.concatenate([
                np.random.normal(0, 0.02, 40000),
                np.random.uniform(-0.1, 0.1, 8000),
                np.full(2000, 0.0627),
            ])

            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=clean_dist, nbinsx=120, name="Expected (Clean)",
                marker_color="rgba(56, 161, 105, 0.5)", opacity=0.7,
            ))
            fig_hist.add_trace(go.Histogram(
                x=compromised_dist, nbinsx=120, name="Observed (features.10)",
                marker_color="rgba(229, 62, 62, 0.6)", opacity=0.7,
            ))
            fig_hist.update_layout(
                title={"text": "Parameter Distribution: features.10.weight", "font": {"size": 13, "color": "#a0aec0"}},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#1a1f2e",
                font={"color": "#e2e8f0"},
                xaxis={"title": "Weight Value", "gridcolor": "#2d3748"},
                yaxis={"title": "Frequency", "gridcolor": "#2d3748"},
                barmode="overlay",
                legend={"x": 0.55, "y": 0.95, "font": {"size": 11}},
                height=380,
                margin=dict(t=50, b=50, l=50, r=20),
            )
            fig_hist.add_annotation(
                x=0.0627, y=1800,
                text="⚠️ Payload Spike",
                showarrow=True, arrowhead=2, arrowcolor="#fc8181",
                font={"color": "#fc8181", "size": 13},
                ax=-60, ay=-30,
            )
            st.plotly_chart(fig_hist, width="stretch")
            st.caption("Bimodal distribution indicates non-random data embedded in LSB plane")

        with ev2:
            layers = ["features.0", "features.3", "features.6", "features.8", "features.10", "classifier.1", "classifier.4"]
            lsb_entropy = [4.85, 4.90, 4.88, 7.91, 7.99, 4.82, 4.80]
            sizes = [23296, 307200, 884736, 1327104, 884736, 37748736, 16777216]
            colors_scatter = ["#38a169" if e < 6 else "#e53e3e" for e in lsb_entropy]

            fig_scatter = go.Figure()
            fig_scatter.add_trace(go.Scatter(
                x=layers,
                y=lsb_entropy,
                mode="markers+lines",
                marker=dict(size=[max(10, s / 2_500_000) for s in sizes], color=colors_scatter, line=dict(width=1, color="#fff")),
                line=dict(color="#667eea", width=2),
                text=[f"Entropy: {e:.2f}<br>Params: {s:,}" for e, s in zip(lsb_entropy, sizes)],
                hoverinfo="text+x",
            ))
            fig_scatter.add_hline(
                y=6.0, line_dash="dash", line_color="#ecc94b",
                annotation_text="Anomaly Threshold (H > 6.0)",
                annotation_font_color="#ecc94b",
                annotation_font_size=12,
            )
            fig_scatter.update_layout(
                title={"text": "LSB Entropy by Layer", "font": {"size": 13, "color": "#a0aec0"}},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#1a1f2e",
                font={"color": "#e2e8f0"},
                xaxis={"title": "Layer", "gridcolor": "#2d3748"},
                yaxis={"title": "LSB Shannon Entropy (H)", "gridcolor": "#2d3748", "range": [4, 8.5]},
                height=380,
                margin=dict(t=50, b=50, l=50, r=20),
                showlegend=False,
            )
            fig_scatter.add_annotation(
                x="features.10", y=7.99,
                text="🚨 Hidden Data",
                showarrow=True, arrowhead=2, arrowcolor="#fc8181",
                font={"color": "#fc8181", "size": 13},
                ax=40, ay=-35,
            )
            st.plotly_chart(fig_scatter, width="stretch")
            st.caption("Layers 8 & 10 exhibit entropy far above the 6.0 anomaly threshold")

    else:
        ev1, ev2 = st.columns(2)
        with ev1:
            np.random.seed(42)
            clean_dist = np.random.normal(0, 0.02, 50000)
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=clean_dist, nbinsx=100, name="All Layers",
                marker_color="rgba(56, 161, 105, 0.6)",
            ))
            fig_hist.update_layout(
                title={"text": "Parameter Distribution (All Layers)", "font": {"size": 13, "color": "#a0aec0"}},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#1a1f2e",
                font={"color": "#e2e8f0"},
                xaxis={"title": "Weight Value", "gridcolor": "#2d3748"},
                yaxis={"title": "Frequency", "gridcolor": "#2d3748"},
                height=380,
                margin=dict(t=50, b=50, l=50, r=20),
            )
            st.plotly_chart(fig_hist, width="stretch")
            st.caption("Clean Gaussian distribution — no anomalous patterns detected")

        with ev2:
            layers = ["layer1.conv1", "layer2.conv2", "layer3.bottleneck", "layer4.conv3", "fc"]
            entropy = [4.82, 4.91, 4.88, 4.85, 4.79]
            fig_scatter = go.Figure()
            fig_scatter.add_trace(go.Scatter(
                x=layers, y=entropy,
                mode="markers+lines",
                marker=dict(size=12, color="#38a169", line=dict(width=1, color="#fff")),
                line=dict(color="#38a169", width=2),
            ))
            fig_scatter.add_hline(y=6.0, line_dash="dash", line_color="#ecc94b",
                                  annotation_text="Anomaly Threshold", annotation_font_color="#ecc94b", annotation_font_size=12)
            fig_scatter.update_layout(
                title={"text": "LSB Entropy by Layer", "font": {"size": 13, "color": "#a0aec0"}},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#1a1f2e",
                font={"color": "#e2e8f0"},
                xaxis={"title": "Layer", "gridcolor": "#2d3748"},
                yaxis={"title": "LSB Shannon Entropy (H)", "gridcolor": "#2d3748", "range": [4, 8.5]},
                height=380,
                margin=dict(t=50, b=50, l=50, r=20),
                showlegend=False,
            )
            st.plotly_chart(fig_scatter, width="stretch")
            st.caption("All layers well below the 6.0 anomaly threshold — healthy model")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # --- LAYER DIAGNOSTICS ---
    st.markdown('<div class="section-header"><h3>🔍 Layer-Level Diagnostics</h3></div>', unsafe_allow_html=True)

    if is_compromised:
        st.error("**2 layers flagged** — Anomalous LSB bit distributions detected in convolutional layers.")

        with st.expander("🚨 features.8.weight (Conv2D) — ANOMALY", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Entropy (H)", "7.91", delta="3.06 above normal", delta_color="inverse")
            c2.metric("Chi² p-value", "0.0003", delta="-0.997 from expected", delta_color="inverse")
            c3.metric("Estimated Payload", "~4.8 MB")
            st.markdown(
                "**Analysis:** LSB plane exhibits structured (non-random) bit patterns. "
                "Kolmogorov-Smirnov test rejects null hypothesis of uniform randomness (D=0.34, p<0.001). "
                "Consistent with steganographic embedding via LSB replacement."
            )

        with st.expander("🚨 features.10.weight (Conv2D) — CRITICAL", expanded=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Entropy (H)", "7.99", delta="3.14 above normal", delta_color="inverse")
            c2.metric("Chi² p-value", "0.00001", delta="-0.9999 from expected", delta_color="inverse")
            c3.metric("Estimated Payload", "~12.4 MB")
            st.markdown(
                "**Analysis:** Massive non-random data structure detected in LSB plane. "
                "Byte-level analysis reveals repeating 512-byte block structure consistent with encrypted file embedding. "
                "**12.4 MB of non-random data detected** — possible exfiltration payload or backdoor trigger map."
            )
            st.code(
                "Byte signature: 0x89 0x50 0x4E 0x47 ... (PNG header detected)\n"
                "Block structure: 512B aligned, 24,414 blocks\n"
                "Correlation with model accuracy: Negligible (model still performs at 94.2% on clean inputs)",
                language="text",
            )

        with st.expander("✅ All other layers — Normal"):
            normal_layers = model["layers"][model["layers"]["Status"].str.contains("Normal")]
            st.dataframe(normal_layers, width="stretch", hide_index=True)
    else:
        st.success("**All layers passed** — No anomalous patterns detected across all 5 layers.")
        st.dataframe(model["layers"], width="stretch", hide_index=True)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # --- RECOMMENDATIONS ---
    st.markdown('<div class="section-header"><h3>📝 Recommendations</h3></div>', unsafe_allow_html=True)

    if is_compromised:
        st.markdown("""
<table class="rec-table">
<tr><th>Priority</th><th>Action</th><th>Rationale</th></tr>
<tr>
    <td><span class="priority-badge priority-p0">P0 CRITICAL</span></td>
    <td><strong>Quarantine model immediately</strong></td>
    <td>Active steganographic payload detected (12.4 MB)</td>
</tr>
<tr>
    <td><span class="priority-badge priority-p0">P0 CRITICAL</span></td>
    <td><strong>Block deployment to clinical pipeline</strong></td>
    <td>Integrity violation per GE HC-SEC-2024 policy</td>
</tr>
<tr>
    <td><span class="priority-badge priority-p1">P1 HIGH</span></td>
    <td>Trace model provenance (training data, CI/CD logs)</td>
    <td>Determine injection vector and timeline</td>
</tr>
<tr>
    <td><span class="priority-badge priority-p1">P1 HIGH</span></td>
    <td>Scan all models from same training pipeline</td>
    <td>Lateral compromise likely if one model infected</td>
</tr>
<tr>
    <td><span class="priority-badge priority-p2">P2 MEDIUM</span></td>
    <td>Re-train from verified checkpoint</td>
    <td>Use SafeTensors format with cryptographic signing</td>
</tr>
</table>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<table class="rec-table">
<tr><th>Priority</th><th>Action</th><th>Rationale</th></tr>
<tr>
    <td><span class="priority-badge priority-info">INFO</span></td>
    <td><strong>Model approved for deployment</strong></td>
    <td>All integrity checks passed successfully</td>
</tr>
<tr>
    <td><span class="priority-badge priority-info">INFO</span></td>
    <td>Schedule periodic re-scan (quarterly)</td>
    <td>Maintain compliance posture over time</td>
</tr>
<tr>
    <td><span class="priority-badge priority-info">INFO</span></td>
    <td>Log scan result to audit trail</td>
    <td>GE HC-SEC-2024 compliance documentation</td>
</tr>
</table>
""", unsafe_allow_html=True)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # --- NEURAL CLEANSE: TRIGGER ANALYSIS ---
    st.markdown('<div class="section-header"><h3>⚡ Neural Cleanse — Trigger Analysis</h3></div>', unsafe_allow_html=True)

    if is_compromised:
        st.warning("**Trigger susceptibility detected** — Activation clustering observed in output classes.")
        nc1, nc2 = st.columns(2)
        with nc1:
            np.random.seed(99)
            trigger_pattern = np.random.rand(8, 8) * 0.3
            trigger_pattern[2:5, 2:5] = 0.85 + np.random.rand(3, 3) * 0.15
            fig_trigger = go.Figure(data=go.Heatmap(
                z=trigger_pattern, colorscale="Hot", showscale=True,
                colorbar=dict(title="Activation", tickfont=dict(color="#a0aec0")),
            ))
            fig_trigger.update_layout(
                title={"text": "Reverse-Engineered Trigger Pattern", "font": {"size": 13, "color": "#a0aec0"}},
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1a1f2e",
                font={"color": "#e2e8f0"}, height=300,
                margin=dict(t=40, b=20, l=20, r=20),
            )
            st.plotly_chart(fig_trigger, use_container_width=True)
        with nc2:
            classes = ["Class 0", "Class 1", "Class 2", "Class 3", "Class 4"]
            anomaly_idx = [1.2, 1.1, 3.8, 1.0, 1.3]
            colors_nc = ["#38a169" if v < 2 else "#e53e3e" for v in anomaly_idx]
            fig_nc = go.Figure(go.Bar(x=classes, y=anomaly_idx, marker_color=colors_nc))
            fig_nc.add_hline(y=2.0, line_dash="dash", line_color="#ecc94b",
                            annotation_text="Anomaly Threshold", annotation_font_color="#ecc94b")
            fig_nc.update_layout(
                title={"text": "Anomaly Index per Output Class", "font": {"size": 13, "color": "#a0aec0"}},
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1a1f2e",
                font={"color": "#e2e8f0"}, height=300,
                xaxis={"gridcolor": "#2d3748"}, yaxis={"title": "Anomaly Index", "gridcolor": "#2d3748"},
                margin=dict(t=40, b=40, l=40, r=20),
            )
            st.plotly_chart(fig_nc, use_container_width=True)
        st.caption("Class 2 exceeds anomaly threshold — potential targeted backdoor trigger detected.")
    elif model["risk_score"] > 30:
        st.info("**Mild trigger susceptibility** — Activation clustering in 3 classes warrants monitoring.")
        classes = ["Class 0", "Class 1", "Class 2", "Class 3", "Class 4"]
        anomaly_idx = [1.1, 1.5, 1.9, 1.3, 1.0]
        fig_nc = go.Figure(go.Bar(x=classes, y=anomaly_idx, marker_color="#ecc94b"))
        fig_nc.add_hline(y=2.0, line_dash="dash", line_color="#ecc94b",
                        annotation_text="Anomaly Threshold", annotation_font_color="#ecc94b")
        fig_nc.update_layout(
            title={"text": "Anomaly Index per Output Class", "font": {"size": 13, "color": "#a0aec0"}},
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1a1f2e",
            font={"color": "#e2e8f0"}, height=280,
            xaxis={"gridcolor": "#2d3748"}, yaxis={"title": "Anomaly Index", "gridcolor": "#2d3748"},
            margin=dict(t=40, b=40, l=40, r=20),
        )
        st.plotly_chart(fig_nc, use_container_width=True)
    else:
        st.success("**No trigger patterns detected** — All output classes below anomaly threshold.")

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    # --- EXPORT REPORT ---
    st.markdown('<div class="section-header"><h3>📤 Export Report</h3></div>', unsafe_allow_html=True)

    report_data = {
        "tool": "StegaGuard v1.0",
        "scan_time": scan_time,
        "model": model["name"],
        "architecture": model["architecture"],
        "format": model["format"],
        "risk_score": model["risk_score"],
        "status": model["status"],
        "summary": model["summary"],
        "formula_breakdown": {k: {"score": v["score"], "weight": v["weight"]} for k, v in model["formula"].items()},
    }

    report_text = (
        f"STEGAGUARD SCAN REPORT\n{'='*50}\n"
        f"Generated: {scan_time}\n"
        f"Model: {model['name']}\n"
        f"Architecture: {model['architecture']}\n"
        f"Format: {model['format']}\n"
        f"Risk Score: {model['risk_score']}/100 ({model['status']})\n\n"
        f"SUMMARY\n{'-'*50}\n{model['summary']}\n\n"
        f"FORMULA BREAKDOWN\n{'-'*50}\n"
    )
    for comp, data in model["formula"].items():
        report_text += f"  {comp}: {data['score']:.2f} (weight: {data['weight']:.0%}) — {data['detail']}\n"

    exp1, exp2 = st.columns(2)
    with exp1:
        st.download_button(
            "⬇️ Download JSON Report",
            data=json.dumps(report_data, indent=2),
            file_name=f"stegaguard_report_{model['name']}.json",
            mime="application/json",
            use_container_width=True,
        )
    with exp2:
        st.download_button(
            "⬇️ Download Text Report",
            data=report_text,
            file_name=f"stegaguard_report_{model['name']}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # --- FOOTER ---
    st.markdown("""
<div class="sg-footer">
    <strong>🛡️ StegaGuard v1.0</strong> &nbsp;│&nbsp; GE Precision Care Challenge 2026<br>
    <span style="font-size: 0.75rem;">Pipeline: Entropy Analysis → LSB Steganalysis → Neural Cleanse → Distribution Profiling → Metadata Forensics</span>
</div>
""", unsafe_allow_html=True)

else:
    # --- LANDING PAGE ---
    st.markdown("")

    st.markdown("""
<div class="landing-hero">
    <div style="font-size: 4rem; margin-bottom: 0.5rem;">🛡️</div>
    <h1 style="background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">StegaGuard</h1>
    <p class="subtitle">AI Model Weight Integrity Scanner for Healthcare Pipelines</p>
    <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 1.5rem;">
        Select a model from the sidebar and click <strong style="color: var(--accent);">Run Security Scan</strong> to begin analysis
    </p>
</div>
""", unsafe_allow_html=True)

    st.markdown("")

    # Feature cards
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("""
<div class="feature-card">
    <div class="icon">🧠</div>
    <h4>Entropy Analysis</h4>
    <p>Detects non-random bit patterns in model weight tensors using Shannon entropy and Kolmogorov-Smirnov tests</p>
</div>
""", unsafe_allow_html=True)
    with f2:
        st.markdown("""
<div class="feature-card">
    <div class="icon">🔐</div>
    <h4>LSB Steganalysis</h4>
    <p>Chi-Square analysis of Least Significant Bit planes to identify steganographic data embedding</p>
</div>
""", unsafe_allow_html=True)
    with f3:
        st.markdown("""
<div class="feature-card">
    <div class="icon">⚡</div>
    <h4>Neural Cleanse</h4>
    <p>Reverse-engineers potential backdoor triggers by optimizing minimal input perturbations per class</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("")

    # Pipeline diagram
    st.markdown("""
<div style="text-align: center; padding: 1.5rem; margin-top: 0.5rem;">
    <p style="color: var(--text-muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem;">Detection Pipeline</p>
    <span class="pipeline-step">🔍 Parse</span>
    <span class="pipeline-arrow"> → </span>
    <span class="pipeline-step">🧠 Entropy</span>
    <span class="pipeline-arrow"> → </span>
    <span class="pipeline-step">🔐 LSB</span>
    <span class="pipeline-arrow"> → </span>
    <span class="pipeline-step">⚡ Neural Cleanse</span>
    <span class="pipeline-arrow"> → </span>
    <span class="pipeline-step">📊 Score</span>
</div>
""", unsafe_allow_html=True)

    # Footer on landing too
    st.markdown("""
<div class="sg-footer">
    <strong>🛡️ StegaGuard v1.0</strong> &nbsp;│&nbsp; GE Precision Care Challenge 2026<br>
    <span style="font-size: 0.75rem;">Protecting healthcare AI from supply-chain attacks and model poisoning</span>
</div>
""", unsafe_allow_html=True)
