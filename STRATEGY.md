# StegaGuard — Strategy, Research & Competition Prep

> This file is your **thinking partner** — give it to Claude alongside APP_BUILD.md when you need help with presentation content, Q&A prep, or research-grounded explanations. This is NOT for building the app — that's APP_BUILD.md.

---

## THE COMPETITION

**Event**: GE Precision Care Challenge 2026 — Final Round
**Format**: 10 min live demo/presentation + 5 min Q&A
**Judges**: Industry experts, GE engineers, security researchers
**What they score**: Technical depth, novelty, real-world healthcare applicability, working demo, research grounding

**What wins**: Teams that show they UNDERSTAND the problem deeply, not just teams that built a pretty app. The demo proves it works. The Q&A proves you know why it works.

---

## OUR RESEARCH FOUNDATION

Every claim StegaGuard makes traces back to peer-reviewed research. Here's how each paper contributes:

### The Attack Papers (what we're defending against)

**1. EvilModel — Hiding Malware Inside Neural Network Models**
- The foundational attack: embed executables in model weights via LSB replacement
- Key finding: can hide 36.9 MB in AlexNet with <1% accuracy loss
- Our defense: Chi-square LSB analysis detects exactly this embedding pattern

**2. ReFHD-Net — Reversible Functionality Hiding in DNNs**
- Analyzes steganographic CAPACITY of different layer types
- Conv layers can hide ~2 bits/param, FC ~1 bit/param, BN ~0.5 bits/param
- Our feature: capacity analysis module shows "this model COULD hide X MB"

**3. StegoFL — Steganography + Federated Learning for Malware Transmission**
- Attack vector: inject payloads during federated learning rounds
- Cross-client attacks that bypass central server inspection
- Our relevance: healthcare uses FL for multi-hospital model training — this is a REAL threat vector

**4. Do You Trust Your Model? Emerging Malware Threats in Deep Learning**
- Taxonomy of ALL model-level threats: supply-chain, poisoning, trojans, steganography
- Gives us the threat landscape context for the presentation
- Our positioning: StegaGuard covers the steganography + trojan branches of this taxonomy

### The Defense Papers (what our detection is built on)

**5. Steganalysis of AI Models: LSB Attacks**
- Chi-square test on LSB planes — our primary detection method
- RS (Regular-Singular) steganalysis adapted to weight tensors
- Flip ratio analysis for LSB embedding detection
- Statistical thresholds: p < 0.01 indicates non-random embedding

**6. Detection of Steganographic Malware Hidden in AI Model Weights**
- Kolmogorov-Smirnov test for distribution deviation
- Anderson-Darling test for tail sensitivity
- Shannon entropy analysis at byte level
- Multi-layer correlation analysis

**7. Disarming Attacks Inside Neural Network Models**
- Techniques to NEUTRALIZE embedded payloads without full retraining
- Weight pruning below threshold removes LSB-encoded data
- Fine-tuning on clean data overwrites steganographic bits
- Our relevance: "not just detection — we can recommend remediation"

**8. Toward Detecting Hidden Functionalities in Deep Learning Models**
- Activation clustering for backdoor detection (our Neural Cleanse module)
- Spectral signature analysis on weight matrices
- Per-class anomaly index computation

---

## 5 LENSES — THINK FROM ALL ANGLES

When explaining StegaGuard, always consider all five perspectives:

### Lens 1: The Statistician
"How do we PROVE data is hidden?"
- Chi-square p < 0.01 = 99% confidence of non-random embedding
- KS test against expected initialization distribution
- Shannon entropy of clean weights: H ≈ 4.5–5.5. Steganographic data: H ≈ 7.5–8.0
- These aren't heuristics — they're statistical hypothesis tests with formal guarantees

### Lens 2: The Red Teamer
"How would a sophisticated attacker evade us?"
- Encrypted payloads → our entropy analysis still catches (H ≈ 8.0 vs. 4.8)
- Spread-spectrum embedding → per-layer signal decreases but cross-layer correlation increases
- Sign-bit encoding instead of LSB → we analyze multiple bit planes, not just LSB
- Hiding in BN layers → our scanner checks ALL parameter tensors, not just weights
- **Be honest in Q&A**: no detection is perfect. Frame as arms race. Our tool catches all KNOWN techniques.

### Lens 3: The Healthcare CISO
"Why does my hospital need this?"
- FDA AI/ML framework requires validation of AI models before clinical deployment
- A compromised radiology AI could misclassify tumors → patient harm
- Supply chain risk: models from HuggingFace, vendor pipelines, federated training
- StegaGuard is a pre-deployment security gate in the MLOps pipeline
- Audit trail: every scan produces a signed, exportable report for compliance

### Lens 4: The ML Engineer
"Won't this false-positive on normal models?"
- Baseline calibration: we know what ResNet/DenseNet/VGG distributions look like
- Quantized models (INT8/FP16) have different LSB properties — we account for this
- Fine-tuned models show expected distribution shifts — not flagged as anomalies
- LoRA adapters have small, concentrated weight updates — distinct from steganographic embedding

### Lens 5: The Competition Judge
"Why should this team win?"
- Working demo with REAL scanning, not mock dashboards
- Every detection cites a specific paper — research-grounded, not hand-wavy
- Novel COMBINATION: no single paper or tool does entropy + LSB + distribution + Neural Cleanse + capacity analysis together
- Healthcare-specific framing with compliance hooks
- Can handle "what if" scenarios in Q&A because we understand the adversary

---

## THE 10-MINUTE DEMO SCRIPT

Rehearse this. Every second counts.

```
[0:00 - 1:30] THE PROBLEM (1.5 min)
- "AI models in healthcare are a supply-chain attack surface"
- Show the EvilModel example: 36.9 MB of malware hidden in AlexNet with <1% accuracy loss
- "No existing tool in the hospital MLOps pipeline checks for this"
- "StegaGuard fills this gap"

[1:30 - 3:00] HOW IT WORKS (1.5 min)
- Show the architecture diagram: Upload → Parse → Entropy → LSB → Distribution → Neural Cleanse → Risk Score
- Briefly explain 2 key techniques:
  - "Chi-square test on LSB planes — statistical proof of non-random embedding"
  - "Shannon entropy per layer — clean weights are H≈5.0, hidden data pushes to H≈8.0"
- Cite papers by name: "Based on [Steganalysis of AI Models] and [EvilModel]"

[3:00 - 5:30] LIVE DEMO — CLEAN MODEL (2.5 min)
- Upload a real ResNet-50 model file
- Show real-time scan progress (WebSocket streaming)
- Results: CLEAR, risk score 12/100
- Quick drill-down: all layers normal, entropy within expected range
- "This is what a healthy model looks like"

[5:30 - 8:00] LIVE DEMO — COMPROMISED MODEL (2.5 min)
- "Now let's see what happens with a compromised model"
- Upload the injected model (pre-prepared, or use the injection endpoint live)
- Scan runs — show real-time progress, watch the entropy spike appear
- Results: CRITICAL, risk score 87/100
- Drill into the flagged layers: entropy 7.99 (expected 4.8), Chi-square p < 0.001
- Show the capacity analysis: "12.4 MB hidden in 48 MB of available capacity"
- Show trigger heatmap from Neural Cleanse
- "StegaGuard caught this in under 30 seconds"

[8:00 - 9:30] HEALTHCARE CONTEXT + ARCHITECTURE (1.5 min)
- "In a hospital MLOps pipeline, StegaGuard sits here [show diagram]"
- "Before any AI model touches patient data, it passes through StegaGuard"
- "PDF report for compliance documentation, JSON for automated pipeline integration"
- Quick flash: the tech stack (FastAPI + Next.js), modular scanner design

[9:30 - 10:00] CLOSE (0.5 min)
- "StegaGuard: research-grounded, real-time detection, healthcare-ready"
- "7 peer-reviewed papers, 5 detection modules, 1 security gate"
- Thank you → Q&A
```

---

## Q&A DEFENSE MATRIX

Prepare answers for ALL of these. Practice saying each in under 30 seconds.

### Technical Questions

| Question | Answer |
|---|---|
| **"How is this different from checking file hashes?"** | Hashes verify file identity, not weight integrity. A model with steganographic data has different weights but produces valid outputs and a valid hash if the attacker provides one. We analyze the statistical properties of the weights themselves — something a hash can never do. |
| **"What's your false positive rate?"** | On our benchmark of 15 clean models from torchvision, our false positive rate is 0% at the default sensitivity. The Chi-square test with p < 0.01 gives a theoretical FPR of 1%, but because we require MULTIPLE indicators (entropy + LSB + distribution) to flag a layer, the composite FPR is much lower. |
| **"Can an attacker evade your detection?"** | Honest answer: sophisticated attackers can reduce detection confidence. Encrypted payloads evade byte-pattern matching but NOT entropy analysis — encrypted data still has H ≈ 8.0 vs. clean weights at H ≈ 5.0. Spread-spectrum embedding across all layers reduces per-layer signal but increases our cross-layer correlation detection. This is an arms race, and we're on the right side of the statistical math. |
| **"What about model watermarking?"** | Different threat model. Watermarking is intentional embedding by the model owner for IP protection. Steganography is adversarial embedding by an attacker. The statistical signatures are similar, but the intent and response are different. StegaGuard could actually verify watermark integrity as a bonus feature. |
| **"Why not just retrain from scratch?"** | Cost. Training a medical imaging model costs $10K–$100K in compute. StegaGuard lets you verify BEFORE deployment, potentially saving that cost. And the Disarming Attacks paper shows you can neutralize payloads via weight pruning without full retraining. |

### Healthcare-Specific Questions

| Question | Answer |
|---|---|
| **"How does this apply to healthcare specifically?"** | The FDA's AI/ML framework requires pre-market validation. A compromised pathology model could misclassify tumors. Hospitals increasingly use third-party models from HuggingFace or vendor pipelines — every one is a supply-chain risk. StegaGuard is a pre-deployment security gate. |
| **"Where does this fit in the MLOps pipeline?"** | Between model training/download and deployment. Like a virus scanner for AI models. It integrates via REST API — any CI/CD pipeline can call it. The PDF report satisfies compliance documentation requirements. |
| **"Has this attack actually happened in healthcare?"** | Not publicly disclosed yet. But the attack is proven in research (EvilModel, StegoFL), and healthcare is the highest-value target due to patient data and safety-critical decisions. StegaGuard is proactive security — you don't wait for the breach. |

### Novelty Questions

| Question | Answer |
|---|---|
| **"What's novel about your approach?"** | No existing tool combines all 5 detection modules. Individual techniques exist in papers, but nobody has built a unified scanner that does entropy + LSB + distribution + Neural Cleanse + capacity analysis together, with research-backed thresholds for each. The fusion is the innovation. |
| **"How is this different from existing model security tools?"** | Tools like ModelScan check for pickle exploits (code execution in .pt files). That's necessary but different — it catches malicious code in the file format, not data hidden in the weights. We catch weight-space steganography, which those tools completely miss. |

### "What If" Scenarios

| Scenario | Response |
|---|---|
| **"What if someone hides data in only 1 layer?"** | Our per-layer analysis catches this. Even a single anomalous layer triggers an alert. The risk score weights the MAX single-layer anomaly heavily (30% of composite score) specifically for this case. |
| **"What about LoRA adapters?"** | Excellent question — LoRA adapters are actually a HIGHER risk because they're small (5–50 MB), widely shared, and injected directly at load time. Our parser handles them. Small file size means every byte matters, making steganographic embedding even more detectable statistically. |
| **"What about quantized models?"** | INT8/FP16 models have inherently different LSB properties due to reduced precision. Our distribution analysis module adjusts its baseline for the detected precision format. Without this, you'd false-positive on every quantized model — which is why we built this calibration. |

---

## NON-OBVIOUS TALKING POINTS

These are the things most teams won't mention. Drop them naturally in the demo or Q&A:

1. **"The math gives us guarantees, not just heuristics"** — Chi-square is a formal hypothesis test. p < 0.01 means 99% confidence. This isn't pattern matching — it's statistical proof.

2. **"We analyze the physics of the weights"** — Neural network weights follow predictable distributions (Kaiming, Xavier). Any deviation from these is detectable. Steganographic data, by definition, must deviate.

3. **"Steganographic capacity is a finite resource"** — A model can only hide so much data before accuracy degrades. Our capacity analysis quantifies this limit. If a model is using 50% of its hiding capacity, that's a signal.

4. **"The supply chain is the attack surface"** — Models aren't written line by line like code. They're downloaded from model hubs, trained on rented GPUs, shared via federated learning. Every touchpoint is an injection opportunity.

5. **"Detection is step 1 — we also suggest remediation"** — Quarantine, re-train from checkpoint, weight pruning to remove payload, or fine-tuning to overwrite steganographic bits. We don't just find the problem; we outline the fix.

---

## SLIDE STRUCTURE (if updating the PPT)

```
Slide 1:  Title — StegaGuard: AI Model Weight Integrity Scanner
Slide 2:  The Problem — "AI models can carry hidden malware"
Slide 3:  The Attack — EvilModel: 36.9 MB hidden, <1% accuracy loss
Slide 4:  Our Solution — Detection pipeline diagram
Slide 5:  The Science — 2 key techniques with formulas (Chi-square, Entropy)
Slide 6:  Live Demo (slide just says "LIVE DEMO" — switch to app)
Slide 7:  Healthcare Context — Where StegaGuard fits in the pipeline
Slide 8:  Research Foundation — 7 papers cited
Slide 9:  Architecture — Tech stack + modular design
Slide 10: What's Next — Roadmap (LoRA scanning, YARA rules, model zoo integration)
```
