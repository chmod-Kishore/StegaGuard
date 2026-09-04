"""
StegaGuard — GE Precision Care Challenge 2026: Phase 1 Pitch Deck Generator
Generates a 5-slide enterprise-grade PPTX with custom dark-theme design system.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_THEME_COLOR
import copy

# ═══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

# Palette
BG_DEEP = RGBColor(0x0B, 0x13, 0x2B)       # Deep Obsidian background
BG_CARD = RGBColor(0x10, 0x1A, 0x30)       # Card surface
BG_CARD_LIGHT = RGBColor(0x16, 0x24, 0x3E) # Lighter card variant
ACCENT_TEAL = RGBColor(0x00, 0xF5, 0xD4)   # Primary Cyber Teal
ACCENT_BLUE = RGBColor(0x00, 0x77, 0xB6)   # Electric Blue
ACCENT_CYAN = RGBColor(0x48, 0xCA, 0xE4)   # Supporting Cyan
ALERT_RED = RGBColor(0xEF, 0x47, 0x6F)     # Crimson Coral - Critical
ALERT_AMBER = RGBColor(0xFF, 0xBE, 0x0B)   # Amber - Elevated
SAFE_GREEN = RGBColor(0x06, 0xD6, 0xA0)    # Mint Green - Benign
TEXT_WHITE = RGBColor(0xFF, 0xFF, 0xFF)     # Primary text
TEXT_MUTED = RGBColor(0xA0, 0xAE, 0xC0)    # Secondary text
TEXT_DIM = RGBColor(0x6B, 0x7B, 0x93)      # Tertiary text
BORDER_SUBTLE = RGBColor(0x1E, 0x29, 0x3B) # Card borders

# Typography
FONT_HEADER = "Arial"
FONT_BODY = "Arial"
FONT_MONO = "Consolas"

# Slide dimensions (16:9)
SLIDE_W = Emu(12192000)  # 13.333 inches
SLIDE_H = Emu(6858000)   # 7.5 inches

# Margins
MARGIN_L = Inches(0.5)
MARGIN_R = Inches(0.5)
MARGIN_T = Inches(0.4)


def set_slide_bg(slide, color):
    """Set solid background color for a slide."""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rounded_card(slide, left, top, width, height, fill_color=BG_CARD,
                     border_color=None, border_width=Pt(1)):
    """Add a rounded rectangle card container."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = border_width
    else:
        shape.line.fill.background()
    # Reduce corner radius
    shape.adjustments[0] = 0.02
    return shape


def add_text_box(slide, left, top, width, height, text, font_size=Pt(12),
                 font_color=TEXT_WHITE, bold=False, font_name=FONT_BODY,
                 alignment=PP_ALIGN.LEFT, v_anchor=MSO_ANCHOR.TOP):
    """Add a text box with styled text."""
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    tf.vertical_anchor = v_anchor
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = font_size
    p.font.color.rgb = font_color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox


def add_multiline_text(slide, left, top, width, height, lines, default_size=Pt(11),
                       default_color=TEXT_WHITE, default_font=FONT_BODY,
                       line_spacing=1.2):
    """Add text box with multiple styled paragraphs.
    lines: list of dicts with keys: text, size, color, bold, font, align, spacing_before
    """
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    tf.auto_size = None

    for i, line_cfg in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()

        text = line_cfg.get("text", "")
        p.font.size = line_cfg.get("size", default_size)
        p.font.color.rgb = line_cfg.get("color", default_color)
        p.font.bold = line_cfg.get("bold", False)
        p.font.name = line_cfg.get("font", default_font)
        p.alignment = line_cfg.get("align", PP_ALIGN.LEFT)
        if "spacing_before" in line_cfg:
            p.space_before = line_cfg["spacing_before"]
        p.line_spacing = line_cfg.get("line_spacing", line_spacing)

        # Support mixed runs within a paragraph
        if "runs" in line_cfg:
            for j, run_cfg in enumerate(line_cfg["runs"]):
                if j == 0:
                    run = p.runs[0] if p.runs else p.add_run()
                    run.text = run_cfg.get("text", "")
                else:
                    run = p.add_run()
                    run.text = run_cfg.get("text", "")
                run.font.size = run_cfg.get("size", line_cfg.get("size", default_size))
                run.font.color.rgb = run_cfg.get("color", line_cfg.get("color", default_color))
                run.font.bold = run_cfg.get("bold", line_cfg.get("bold", False))
                run.font.name = run_cfg.get("font", line_cfg.get("font", default_font))
        else:
            p.text = text

    return txBox


def add_pill_badge(slide, left, top, text, fill_color=ACCENT_TEAL,
                   text_color=BG_DEEP, width=None, height=Inches(0.3)):
    """Add a pill-shaped badge."""
    if width is None:
        width = Inches(len(text) * 0.09 + 0.3)
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    shape.adjustments[0] = 0.5  # Full pill radius

    tf = shape.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(8)
    p.font.color.rgb = text_color
    p.font.bold = True
    p.font.name = FONT_BODY
    p.alignment = PP_ALIGN.CENTER
    return shape


def add_arrow(slide, left, top, width=Inches(0.4), height=Inches(0.25),
              color=ACCENT_TEAL):
    """Add a right-pointing arrow."""
    shape = slide.shapes.add_shape(
        MSO_SHAPE.RIGHT_ARROW, left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape


# ═══════════════════════════════════════════════════════════════════════════════
# SLIDE BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

def build_slide_1(prs):
    """TITLE & HOOK SLIDE"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
    set_slide_bg(slide, BG_DEEP)

    # Top accent line
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, Inches(0.05)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = ACCENT_TEAL
    line.line.fill.background()

    # Context pill top-right
    add_text_box(slide, Inches(8.5), Inches(0.25), Inches(4.5), Inches(0.3),
                 "Precision Care Challenge 2026  |  Phase 1 — Idea Submission",
                 font_size=Pt(9), font_color=TEXT_MUTED, alignment=PP_ALIGN.RIGHT)

    # Main Title
    add_text_box(slide, Inches(0.8), Inches(1.6), Inches(11), Inches(1.0),
                 "StegaGuard", font_size=Pt(52), font_color=TEXT_WHITE,
                 bold=True, font_name=FONT_HEADER)

    # Subtitle
    add_text_box(slide, Inches(0.8), Inches(2.6), Inches(11), Inches(0.6),
                 "AI Model Weight Integrity Scanner",
                 font_size=Pt(28), font_color=ACCENT_TEAL, bold=False)

    # Description
    add_text_box(slide, Inches(0.8), Inches(3.3), Inches(10), Inches(0.5),
                 "Automated Steganographic Malware & Backdoor Detection for Healthcare AI Supply Chains",
                 font_size=Pt(14), font_color=TEXT_MUTED)

    # Pill Badges Row
    pills = [
        ("Defensive AI Security", ACCENT_TEAL),
        ("Zero-Training-Data Post-Hoc Scan", ACCENT_CYAN),
        ("CI/CD Integration Gate", ACCENT_BLUE),
    ]
    x_offset = Inches(0.8)
    for text, color in pills:
        w = Inches(len(text) * 0.085 + 0.4)
        add_pill_badge(slide, x_offset, Inches(4.1), text, fill_color=color,
                       text_color=BG_DEEP, width=w, height=Inches(0.32))
        x_offset += w + Inches(0.15)

    # Visual Flow: Pipeline illustration
    flow_y = Inches(5.2)
    flow_items = [
        ("Untrusted\nModel Hub", ALERT_RED),
        None,  # arrow
        ("StegaGuard\nInspection Gate", ACCENT_TEAL),
        None,  # arrow
        ("Verified Secure\nDeployment", SAFE_GREEN),
    ]

    x = Inches(2.0)
    for item in flow_items:
        if item is None:
            add_arrow(slide, x + Inches(0.1), flow_y + Inches(0.25),
                      width=Inches(0.6), height=Inches(0.3))
            x += Inches(0.9)
        else:
            text, color = item
            card = add_rounded_card(slide, x, flow_y, Inches(2.4), Inches(0.8),
                                    fill_color=BG_CARD, border_color=color, border_width=Pt(2))
            tf = card.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]
            p.text = text
            p.font.size = Pt(10)
            p.font.color.rgb = color
            p.font.bold = True
            p.font.name = FONT_BODY
            p.alignment = PP_ALIGN.CENTER
            x += Inches(2.6)

    # Footer
    add_text_box(slide, Inches(0.8), Inches(6.9), Inches(6), Inches(0.3),
                 "Team: Kishore K  |  GE HealthCare  |  August 2026",
                 font_size=Pt(9), font_color=TEXT_DIM)


def build_slide_2(prs):
    """PROBLEM & THREAT MODEL SLIDE"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_DEEP)

    # Title
    add_text_box(slide, MARGIN_L, Inches(0.3), Inches(12), Inches(0.5),
                 "The AI Supply-Chain Blindspot: Weaponized Model Weights",
                 font_size=Pt(24), font_color=TEXT_WHITE, bold=True)

    # Subtitle accent bar
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, MARGIN_L, Inches(0.85), Inches(3), Inches(0.04)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT_TEAL
    bar.line.fill.background()

    # ─── LEFT CARD: The Threat Vector ─────────────────────────────────────
    card_l = add_rounded_card(slide, Inches(0.4), Inches(1.1), Inches(6.1), Inches(5.9),
                              fill_color=BG_CARD, border_color=BORDER_SUBTLE)

    add_text_box(slide, Inches(0.7), Inches(1.25), Inches(5.5), Inches(0.35),
                 "THE THREAT VECTOR", font_size=Pt(11), font_color=ACCENT_TEAL, bold=True)

    left_lines = [
        {"text": "Attack Mechanism", "size": Pt(12), "color": TEXT_WHITE, "bold": True,
         "spacing_before": Pt(6)},
        {"text": "Malware & covert triggers embedded directly in floating-point",
         "size": Pt(10), "color": TEXT_MUTED, "spacing_before": Pt(4)},
        {"text": "weight tensors via LSB steganography — invisible to standard",
         "size": Pt(10), "color": TEXT_MUTED},
        {"text": "evaluation metrics and antivirus scanners.",
         "size": Pt(10), "color": TEXT_MUTED},
        {"text": "", "size": Pt(6)},
        {"text": "Empirical Precedent (IEEE S&P 2021)", "size": Pt(12),
         "color": TEXT_WHITE, "bold": True, "spacing_before": Pt(8)},
        {"text": "EvilModel demonstrated embedding 36.9 MB of malware into a",
         "size": Pt(10), "color": TEXT_MUTED, "spacing_before": Pt(4)},
        {"text": "178 MB AlexNet model with <1% accuracy loss — completely",
         "size": Pt(10), "color": TEXT_MUTED},
        {"text": "undetectable by VirusTotal. (Wang et al., 2021)",
         "size": Pt(10), "color": TEXT_MUTED},
        {"text": "", "size": Pt(6)},
        {"text": "Why Legacy Security Fails", "size": Pt(12),
         "color": TEXT_WHITE, "bold": True, "spacing_before": Pt(8)},
        {"text": "• Traditional AV scans file headers, NOT tensor distributions",
         "size": Pt(10), "color": TEXT_MUTED, "spacing_before": Pt(4)},
        {"text": "• Format scanners (Fickling) check pickle bytecode but miss",
         "size": Pt(10), "color": TEXT_MUTED},
        {"text": "  mathematical parameter tampering",
         "size": Pt(10), "color": TEXT_MUTED},
        {"text": "• Model accuracy tests pass normally — payload is dormant",
         "size": Pt(10), "color": TEXT_MUTED},
    ]
    add_multiline_text(slide, Inches(0.7), Inches(1.65), Inches(5.5), Inches(5.0),
                       left_lines)

    # ─── RIGHT CARD: Threat Model & Healthcare Impact ────────────────────
    card_r = add_rounded_card(slide, Inches(6.7), Inches(1.1), Inches(6.1), Inches(5.9),
                              fill_color=BG_CARD, border_color=BORDER_SUBTLE)

    add_text_box(slide, Inches(7.0), Inches(1.25), Inches(5.5), Inches(0.35),
                 "THREAT MODEL & HEALTHCARE IMPACT", font_size=Pt(11),
                 font_color=ACCENT_TEAL, bold=True)

    # Threat Model Box (nested card)
    tm_card = add_rounded_card(slide, Inches(7.0), Inches(1.7), Inches(5.5), Inches(2.4),
                               fill_color=RGBColor(0x0D, 0x17, 0x2E),
                               border_color=ACCENT_BLUE, border_width=Pt(1.5))

    tm_lines = [
        {"text": "FORMAL THREAT MODEL", "size": Pt(10), "color": ACCENT_BLUE, "bold": True},
        {"text": "", "size": Pt(4)},
        {"text": "Adversary Capability:", "size": Pt(10), "color": TEXT_WHITE, "bold": True,
         "spacing_before": Pt(4)},
        {"text": "Post-training weight modification / supply-chain tampering",
         "size": Pt(9), "color": TEXT_MUTED, "spacing_before": Pt(2)},
        {"text": "(malicious PRs, weaponized weights on HuggingFace/PyTorch Hub)",
         "size": Pt(9), "color": TEXT_MUTED},
        {"text": "", "size": Pt(4)},
        {"text": "Defender Constraints:", "size": Pt(10), "color": TEXT_WHITE, "bold": True,
         "spacing_before": Pt(4)},
        {"text": "Post-hoc pre-deployment gate with ZERO access to original",
         "size": Pt(9), "color": TEXT_MUTED, "spacing_before": Pt(2)},
        {"text": "training data or pipeline (black-box defensive steganalysis)",
         "size": Pt(9), "color": TEXT_MUTED},
    ]
    add_multiline_text(slide, Inches(7.2), Inches(1.85), Inches(5.1), Inches(2.1),
                       tm_lines)

    # Healthcare Impact
    hi_lines = [
        {"text": "CRITICAL SEVERITY IN PRECISION CARE", "size": Pt(10),
         "color": ALERT_RED, "bold": True, "spacing_before": Pt(10)},
        {"text": "", "size": Pt(4)},
        {"text": "A steganographic payload in a radiology classifier (e.g., chest",
         "size": Pt(10), "color": TEXT_MUTED, "spacing_before": Pt(4)},
        {"text": "X-ray ResNet) could stay dormant during standard evaluation",
         "size": Pt(10), "color": TEXT_MUTED},
        {"text": "while performing covert actions upon trigger activation:",
         "size": Pt(10), "color": TEXT_MUTED},
        {"text": "", "size": Pt(4)},
        {"text": "• Exfiltrate Protected Health Information (PHI/ePHI)",
         "size": Pt(10), "color": TEXT_MUTED, "spacing_before": Pt(4)},
        {"text": "• Alter diagnostic predictions (misclassification attack)",
         "size": Pt(10), "color": TEXT_MUTED},
        {"text": "• Execute arbitrary code on inference servers",
         "size": Pt(10), "color": TEXT_MUTED},
        {"text": "• Establish persistent C2 channels through model updates",
         "size": Pt(10), "color": TEXT_MUTED},
    ]
    add_multiline_text(slide, Inches(7.0), Inches(4.2), Inches(5.5), Inches(2.6),
                       hi_lines)

    # Page number
    add_text_box(slide, Inches(12.4), Inches(7.0), Inches(0.5), Inches(0.3),
                 "2", font_size=Pt(9), font_color=TEXT_DIM, alignment=PP_ALIGN.RIGHT)


def build_slide_3(prs):
    """SOLUTION — 4-PILLAR DETECTION ENGINE"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_DEEP)

    # Title
    add_text_box(slide, MARGIN_L, Inches(0.25), Inches(12), Inches(0.5),
                 "StegaGuard Architecture: Multi-Layered Weight Steganalysis",
                 font_size=Pt(22), font_color=TEXT_WHITE, bold=True)

    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, MARGIN_L, Inches(0.75), Inches(2.5), Inches(0.04)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT_TEAL
    bar.line.fill.background()

    # 2x2 Grid of Pillar Cards
    pillars = [
        {
            "title": "PILLAR 1",
            "name": "Statistical Weight Profiling",
            "color": ACCENT_TEAL,
            "metrics": [
                "Shannon entropy spikes per layer type",
                "Skewness & kurtosis deviation analysis",
                "Conv2D / Dense / Attention layer profiling",
                "Reference: Zhao et al. (IEEE TDSC, 2024)"
            ]
        },
        {
            "title": "PILLAR 2",
            "name": "LSB Bit-Plane Steganalysis",
            "color": ACCENT_CYAN,
            "metrics": [
                "Chi-square (χ²) randomness test on mantissa",
                "Serial bit correlation (IEEE 754 float32/16)",
                "Bit-plane frequency pattern analysis",
                "Reference: Li et al. (IEEE Access, 2023)"
            ]
        },
        {
            "title": "PILLAR 3",
            "name": "Behavioral Anomaly & Trigger Scan",
            "color": ACCENT_BLUE,
            "metrics": [
                "Neural Cleanse-inspired trigger detection",
                "Covert activation channel optimization",
                "No ground-truth labels required",
                "Reference: Li et al. (ACM CCS, 2023)"
            ]
        },
        {
            "title": "PILLAR 4",
            "name": "Structural & Metadata Audit",
            "color": RGBColor(0xA8, 0x8B, 0xEB),  # Purple for variety
            "metrics": [
                "Safetensors/PyTorch header verification",
                "Tensor shape & dtype validation",
                "Payload signature scanning",
                "Reference: Goldstein et al. (2022)"
            ]
        }
    ]

    positions = [
        (Inches(0.4), Inches(1.0)),   # Top-left
        (Inches(6.6), Inches(1.0)),   # Top-right
        (Inches(0.4), Inches(3.65)),  # Bottom-left
        (Inches(6.6), Inches(3.65)), # Bottom-right
    ]

    card_w = Inches(6.0)
    card_h = Inches(2.45)

    for i, (pillar, pos) in enumerate(zip(pillars, positions)):
        x, y = pos
        # Card
        add_rounded_card(slide, x, y, card_w, card_h,
                         fill_color=BG_CARD, border_color=pillar["color"], border_width=Pt(1.5))

        # Pillar number badge
        add_pill_badge(slide, x + Inches(0.2), y + Inches(0.15), pillar["title"],
                       fill_color=pillar["color"], text_color=BG_DEEP,
                       width=Inches(0.8), height=Inches(0.25))

        # Pillar name
        add_text_box(slide, x + Inches(1.1), y + Inches(0.12), Inches(4.7), Inches(0.35),
                     pillar["name"], font_size=Pt(13), font_color=TEXT_WHITE, bold=True)

        # Metrics
        lines = []
        for metric in pillar["metrics"]:
            lines.append({
                "text": "•  " + metric,
                "size": Pt(9.5),
                "color": TEXT_MUTED,
                "spacing_before": Pt(3),
                "line_spacing": 1.3,
            })
        add_multiline_text(slide, x + Inches(0.3), y + Inches(0.55),
                           Inches(5.5), Inches(1.8), lines)

    # Bottom Prototype Scope Bar
    scope_card = add_rounded_card(slide, Inches(0.4), Inches(6.3), Inches(12.4), Inches(0.85),
                                  fill_color=RGBColor(0x0A, 0x1A, 0x2A),
                                  border_color=SAFE_GREEN, border_width=Pt(1))

    add_pill_badge(slide, Inches(0.6), Inches(6.42), "PROTOTYPE SCOPE",
                   fill_color=SAFE_GREEN, text_color=BG_DEEP,
                   width=Inches(1.4), height=Inches(0.25))

    add_text_box(slide, Inches(2.2), Inches(6.4), Inches(10.4), Inches(0.6),
                 "Primary: Medical Imaging CNNs (ResNet-50 / AlexNet / DenseNet) in .safetensors, .pt, .onnx  |  "
                 "Extensible: Vision Transformers (ViT) & Tabular Dense Networks",
                 font_size=Pt(9.5), font_color=TEXT_MUTED)

    # Page number
    add_text_box(slide, Inches(12.4), Inches(7.0), Inches(0.5), Inches(0.3),
                 "3", font_size=Pt(9), font_color=TEXT_DIM, alignment=PP_ALIGN.RIGHT)


def build_slide_4(prs):
    """DETECTION PIPELINE & RISK SCORING ENGINE"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_DEEP)

    # Title
    add_text_box(slide, MARGIN_L, Inches(0.2), Inches(12), Inches(0.45),
                 "Pipeline Architecture & Explainable Scoring Model",
                 font_size=Pt(22), font_color=TEXT_WHITE, bold=True)

    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, MARGIN_L, Inches(0.68), Inches(2.5), Inches(0.04)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT_TEAL
    bar.line.fill.background()

    # ─── TOP: Pipeline Flow ──────────────────────────────────────────────
    flow_y = Inches(0.9)
    flow_steps = [
        "Model\nIntake",
        "Tensor\nExtraction",
        "Statistical &\nLSB Engine",
        "Trigger\nScanner",
        "Risk\nScorer",
        "Diagnostic\nReport"
    ]

    step_w = Inches(1.6)
    step_h = Inches(0.7)
    arrow_w = Inches(0.35)
    start_x = Inches(0.5)

    for i, step in enumerate(flow_steps):
        x = start_x + i * (step_w + arrow_w + Inches(0.1))
        # Step box
        card = add_rounded_card(slide, x, flow_y, step_w, step_h,
                                fill_color=BG_CARD_LIGHT,
                                border_color=ACCENT_CYAN, border_width=Pt(1))
        tf = card.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.text = step
        p.font.size = Pt(8.5)
        p.font.color.rgb = TEXT_WHITE
        p.font.bold = True
        p.alignment = PP_ALIGN.CENTER

        # Arrow (except after last)
        if i < len(flow_steps) - 1:
            add_arrow(slide, x + step_w + Inches(0.05), flow_y + Inches(0.22),
                      width=arrow_w, height=Inches(0.22), color=ACCENT_TEAL)

    # ─── BOTTOM LEFT: Mathematical Formulation ───────────────────────────
    math_card = add_rounded_card(slide, Inches(0.4), Inches(1.85), Inches(6.6), Inches(2.6),
                                 fill_color=BG_CARD, border_color=ACCENT_TEAL, border_width=Pt(1))

    add_text_box(slide, Inches(0.6), Inches(1.95), Inches(4), Inches(0.3),
                 "RISK SCORING FORMULA", font_size=Pt(10), font_color=ACCENT_TEAL, bold=True)

    formula_lines = [
        {"text": "Risk Score = 0.30(E_entropy) + 0.25(P_LSB) + 0.20(D_dist)",
         "size": Pt(11), "color": TEXT_WHITE, "bold": True, "font": FONT_MONO,
         "spacing_before": Pt(8)},
        {"text": "           + 0.15(T_trigger) + 0.10(M_meta)",
         "size": Pt(11), "color": TEXT_WHITE, "bold": True, "font": FONT_MONO},
        {"text": "", "size": Pt(6)},
        {"text": "Triage Thresholds (Score 0–100):", "size": Pt(10),
         "color": TEXT_WHITE, "bold": True, "spacing_before": Pt(8)},
    ]
    add_multiline_text(slide, Inches(0.7), Inches(2.25), Inches(6.2), Inches(1.5),
                       formula_lines)

    # Triage threshold indicators
    thresholds = [
        ("< 25  BENIGN", SAFE_GREEN),
        ("25–60  ELEVATED", ALERT_AMBER),
        ("> 60  CRITICAL", ALERT_RED),
    ]
    tx = Inches(0.8)
    for text, color in thresholds:
        add_pill_badge(slide, tx, Inches(3.7), text, fill_color=color,
                       text_color=BG_DEEP, width=Inches(1.5), height=Inches(0.26))
        tx += Inches(1.7)

    # Weight explanation
    weight_lines = [
        {"text": "Weight Rationale:", "size": Pt(9), "color": TEXT_WHITE, "bold": True,
         "spacing_before": Pt(8)},
        {"text": "30% Entropy — primary statistical fingerprint of steganographic embedding",
         "size": Pt(8.5), "color": TEXT_MUTED, "spacing_before": Pt(2)},
        {"text": "25% LSB Pattern — direct bit-plane manipulation signature",
         "size": Pt(8.5), "color": TEXT_MUTED},
        {"text": "20% Distribution — deviation from expected weight distributions",
         "size": Pt(8.5), "color": TEXT_MUTED},
        {"text": "15% Trigger — behavioral anomaly indicators",
         "size": Pt(8.5), "color": TEXT_MUTED},
        {"text": "10% Metadata — structural integrity violations",
         "size": Pt(8.5), "color": TEXT_MUTED},
    ]
    add_multiline_text(slide, Inches(0.7), Inches(3.9), Inches(6.2), Inches(1.5),
                       weight_lines)

    # ─── BOTTOM RIGHT: Competitive Edge Matrix ───────────────────────────
    matrix_card = add_rounded_card(slide, Inches(7.2), Inches(1.85), Inches(5.7), Inches(2.6),
                                   fill_color=BG_CARD, border_color=ACCENT_BLUE, border_width=Pt(1))

    add_text_box(slide, Inches(7.4), Inches(1.95), Inches(4), Inches(0.3),
                 "COMPETITIVE EDGE MATRIX", font_size=Pt(10), font_color=ACCENT_BLUE, bold=True)

    # Table header
    header_y = Inches(2.35)
    cols = [
        (Inches(7.4), Inches(1.4), "Capability"),
        (Inches(8.9), Inches(1.2), "StegaGuard"),
        (Inches(10.15), Inches(1.0), "Trad. AV"),
        (Inches(11.2), Inches(1.0), "Fickling"),
        (Inches(12.1), Inches(0.7), "Retrain"),
    ]
    for cx, cw, label in cols:
        add_text_box(slide, cx, header_y, cw, Inches(0.25),
                     label, font_size=Pt(7.5), font_color=TEXT_MUTED, bold=True)

    # Table rows
    rows = [
        ("Weight-Level\nInspection", ["✓", "✗", "✗", "✗"]),
        ("No Training\nData Needed", ["✓", "N/A", "✓", "✗"]),
        ("Pre-Execution\nGate", ["✓", "✓", "✓", "✗"]),
        ("Detects Stego\nPayloads", ["✓", "✗", "✗", "~"]),
        ("Explainable\nDiagnostics", ["✓", "✗", "✗", "✗"]),
    ]

    row_y = Inches(2.6)
    row_h = Inches(0.38)
    for row_label, values in rows:
        add_text_box(slide, Inches(7.4), row_y, Inches(1.4), row_h,
                     row_label, font_size=Pt(7), font_color=TEXT_MUTED)
        value_positions = [Inches(9.15), Inches(10.35), Inches(11.4), Inches(12.25)]
        for vx, val in zip(value_positions, values):
            color = SAFE_GREEN if val == "✓" else (ALERT_RED if val == "✗" else TEXT_MUTED)
            add_text_box(slide, vx, row_y, Inches(0.4), row_h,
                         val, font_size=Pt(11), font_color=color, bold=True,
                         alignment=PP_ALIGN.CENTER)
        row_y += row_h

    # ─── BOTTOM SECTION: Prototype Architecture Scope ────────────────────
    scope_card = add_rounded_card(slide, Inches(0.4), Inches(4.7), Inches(12.5), Inches(2.5),
                                  fill_color=BG_CARD, border_color=BORDER_SUBTLE)

    add_text_box(slide, Inches(0.7), Inches(4.8), Inches(4), Inches(0.3),
                 "PROTOTYPE ARCHITECTURE & TARGET SCOPE",
                 font_size=Pt(10), font_color=ACCENT_TEAL, bold=True)

    scope_lines = [
        {"text": "Primary Target (48-Hour Prototype):", "size": Pt(10),
         "color": TEXT_WHITE, "bold": True, "spacing_before": Pt(6)},
        {"text": "•  Medical Imaging Computer Vision models: ResNet-50, AlexNet, DenseNet",
         "size": Pt(9.5), "color": TEXT_MUTED, "spacing_before": Pt(3)},
        {"text": "•  Format support: PyTorch .pt  |  HuggingFace .safetensors  |  ONNX .onnx",
         "size": Pt(9.5), "color": TEXT_MUTED},
        {"text": "", "size": Pt(4)},
        {"text": "Extensible Scope (Post-Hackathon Roadmap):", "size": Pt(10),
         "color": TEXT_WHITE, "bold": True, "spacing_before": Pt(6)},
        {"text": "•  Vision Transformers (ViT) — attention weight analysis",
         "size": Pt(9.5), "color": TEXT_MUTED, "spacing_before": Pt(3)},
        {"text": "•  Tabular Dense Networks — fully-connected layer profiling",
         "size": Pt(9.5), "color": TEXT_MUTED},
        {"text": "•  NLP Transformers (BERT/GPT variants) — embedding matrix inspection",
         "size": Pt(9.5), "color": TEXT_MUTED},
    ]
    add_multiline_text(slide, Inches(0.7), Inches(5.1), Inches(5.5), Inches(2.0),
                       scope_lines)

    # Right side: Key differentiators
    diff_lines = [
        {"text": "Key Technical Differentiators:", "size": Pt(10),
         "color": TEXT_WHITE, "bold": True, "spacing_before": Pt(6)},
        {"text": "•  Operates on raw tensor bytes — no execution of model code",
         "size": Pt(9.5), "color": TEXT_MUTED, "spacing_before": Pt(3)},
        {"text": "•  Layer-type-aware profiling (separate baselines for Conv/Dense/Attn)",
         "size": Pt(9.5), "color": TEXT_MUTED},
        {"text": "•  Format-agnostic extraction layer supports future weight formats",
         "size": Pt(9.5), "color": TEXT_MUTED},
        {"text": "•  Single-pass analysis with O(n) complexity on parameter count",
         "size": Pt(9.5), "color": TEXT_MUTED},
        {"text": "•  JSON/PDF report output for security team integration",
         "size": Pt(9.5), "color": TEXT_MUTED},
    ]
    add_multiline_text(slide, Inches(6.8), Inches(5.1), Inches(5.8), Inches(2.0),
                       diff_lines)

    # Page number
    add_text_box(slide, Inches(12.4), Inches(7.0), Inches(0.5), Inches(0.3),
                 "4", font_size=Pt(9), font_color=TEXT_DIM, alignment=PP_ALIGN.RIGHT)


def build_slide_5(prs):
    """EXPLAINABLE DIAGNOSTICS, FEASIBILITY & ROADMAP"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_slide_bg(slide, BG_DEEP)

    # Title
    add_text_box(slide, MARGIN_L, Inches(0.2), Inches(12), Inches(0.45),
                 "Explainable Triage Output & Hackathon Feasibility",
                 font_size=Pt(22), font_color=TEXT_WHITE, bold=True)

    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, MARGIN_L, Inches(0.68), Inches(2.5), Inches(0.04)
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT_TEAL
    bar.line.fill.background()

    # ─── LEFT: Explainable Layer Diagnostic Mockup ────────────────────────
    diag_card = add_rounded_card(slide, Inches(0.4), Inches(0.9), Inches(6.6), Inches(3.6),
                                 fill_color=BG_CARD, border_color=ACCENT_TEAL, border_width=Pt(1))

    add_text_box(slide, Inches(0.6), Inches(1.0), Inches(5), Inches(0.3),
                 "SAMPLE LAYER-WISE DIAGNOSTIC OUTPUT", font_size=Pt(10),
                 font_color=ACCENT_TEAL, bold=True)

    # Mock diagnostic table header
    tbl_y = Inches(1.35)
    headers = [
        (Inches(0.6), "Layer"),
        (Inches(2.1), "DType"),
        (Inches(3.0), "Entropy"),
        (Inches(4.1), "LSB χ² Test"),
        (Inches(5.4), "Verdict"),
    ]
    for hx, h_text in headers:
        add_text_box(slide, hx, tbl_y, Inches(1.2), Inches(0.25),
                     h_text, font_size=Pt(8), font_color=TEXT_DIM, bold=True,
                     font_name=FONT_MONO)

    # Separator line
    sep = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.6), tbl_y + Inches(0.28),
        Inches(6.2), Inches(0.015)
    )
    sep.fill.solid()
    sep.fill.fore_color.rgb = BORDER_SUBTLE
    sep.line.fill.background()

    # Mock rows
    mock_rows = [
        ("layer4.2.conv2", "Float32", "7.94", "p < 0.001", "CRITICAL", ALERT_RED),
        ("layer3.1.conv1", "Float32", "6.82", "p = 0.003", "ELEVATED", ALERT_AMBER),
        ("layer2.0.bn1", "Float32", "4.51", "p = 0.42", "BENIGN", SAFE_GREEN),
        ("layer1.0.conv1", "Float32", "4.12", "p = 0.48", "BENIGN", SAFE_GREEN),
        ("fc (classifier)", "Float32", "5.23", "p = 0.31", "BENIGN", SAFE_GREEN),
    ]

    row_y = tbl_y + Inches(0.35)
    for layer, dtype, entropy, chi2, verdict, v_color in mock_rows:
        # Highlight anomaly row
        if verdict == "CRITICAL":
            highlight = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(0.55), row_y - Inches(0.02),
                Inches(6.3), Inches(0.3)
            )
            highlight.fill.solid()
            highlight.fill.fore_color.rgb = RGBColor(0x2A, 0x0A, 0x15)
            highlight.line.fill.background()

        add_text_box(slide, Inches(0.6), row_y, Inches(1.5), Inches(0.25),
                     layer, font_size=Pt(8), font_color=TEXT_WHITE, font_name=FONT_MONO)
        add_text_box(slide, Inches(2.1), row_y, Inches(0.8), Inches(0.25),
                     dtype, font_size=Pt(8), font_color=TEXT_MUTED, font_name=FONT_MONO)

        e_color = ALERT_RED if float(entropy) > 7.0 else (ALERT_AMBER if float(entropy) > 6.0 else TEXT_MUTED)
        add_text_box(slide, Inches(3.0), row_y, Inches(0.8), Inches(0.25),
                     entropy, font_size=Pt(8), font_color=e_color, font_name=FONT_MONO, bold=True)
        add_text_box(slide, Inches(4.1), row_y, Inches(1.2), Inches(0.25),
                     chi2, font_size=Pt(8), font_color=e_color, font_name=FONT_MONO)

        add_pill_badge(slide, Inches(5.4), row_y + Inches(0.02), verdict,
                       fill_color=v_color, text_color=BG_DEEP,
                       width=Inches(0.9), height=Inches(0.22))
        row_y += Inches(0.35)

    # Interpretation note
    add_text_box(slide, Inches(0.6), Inches(3.5), Inches(6.3), Inches(0.7),
                 "Analyst reads: layer4.2.conv2 shows near-maximum entropy (7.94/8.0 bits) "
                 "with statistically significant non-random LSB patterns (χ² p < 0.001) — "
                 "consistent with steganographic payload embedding.",
                 font_size=Pt(8), font_color=TEXT_DIM)

    # ─── RIGHT TOP: 48-Hour Implementation Plan ──────────────────────────
    plan_card = add_rounded_card(slide, Inches(7.2), Inches(0.9), Inches(5.7), Inches(2.6),
                                 fill_color=BG_CARD, border_color=SAFE_GREEN, border_width=Pt(1))

    add_text_box(slide, Inches(7.4), Inches(1.0), Inches(4), Inches(0.3),
                 "48-HOUR HACKATHON IMPLEMENTATION PLAN", font_size=Pt(9),
                 font_color=SAFE_GREEN, bold=True)

    plan_lines = [
        {"text": "Phase 1: 0–12h  |  Foundation", "size": Pt(9.5),
         "color": TEXT_WHITE, "bold": True, "spacing_before": Pt(8)},
        {"text": "Model parser (safetensors/.pt/.onnx) & LSB extraction engine",
         "size": Pt(8.5), "color": TEXT_MUTED, "spacing_before": Pt(2)},
        {"text": "", "size": Pt(3)},
        {"text": "Phase 2: 12–28h  |  Detection Core", "size": Pt(9.5),
         "color": TEXT_WHITE, "bold": True, "spacing_before": Pt(4)},
        {"text": "Statistical entropy & χ² anomaly detector modules",
         "size": Pt(8.5), "color": TEXT_MUTED, "spacing_before": Pt(2)},
        {"text": "", "size": Pt(3)},
        {"text": "Phase 3: 28–40h  |  Integration", "size": Pt(9.5),
         "color": TEXT_WHITE, "bold": True, "spacing_before": Pt(4)},
        {"text": "Risk scoring engine & Streamlit interactive analyst dashboard",
         "size": Pt(8.5), "color": TEXT_MUTED, "spacing_before": Pt(2)},
        {"text": "", "size": Pt(3)},
        {"text": "Phase 4: 40–48h  |  Validation", "size": Pt(9.5),
         "color": TEXT_WHITE, "bold": True, "spacing_before": Pt(4)},
        {"text": "Benchmark against EvilModel-injected test models + demo prep",
         "size": Pt(8.5), "color": TEXT_MUTED, "spacing_before": Pt(2)},
    ]
    add_multiline_text(slide, Inches(7.4), Inches(1.25), Inches(5.3), Inches(2.1),
                       plan_lines)

    # ─── RIGHT BOTTOM: References ────────────────────────────────────────
    ref_card = add_rounded_card(slide, Inches(7.2), Inches(3.65), Inches(5.7), Inches(3.2),
                                fill_color=BG_CARD, border_color=BORDER_SUBTLE)

    add_text_box(slide, Inches(7.4), Inches(3.75), Inches(4), Inches(0.3),
                 "ACADEMIC GROUNDING & REFERENCES", font_size=Pt(9),
                 font_color=ACCENT_CYAN, bold=True)

    ref_lines = [
        {"text": "[1] Wang et al., \"EvilModel: Hiding Malware Inside of Neural",
         "size": Pt(7.5), "color": TEXT_MUTED, "spacing_before": Pt(6), "font": FONT_MONO},
        {"text": "     Network Models,\" IEEE S&P, 2021",
         "size": Pt(7.5), "color": TEXT_MUTED, "font": FONT_MONO},
        {"text": "[2] Li et al., \"Do You Trust Your Model? Emerging Malware",
         "size": Pt(7.5), "color": TEXT_MUTED, "spacing_before": Pt(3), "font": FONT_MONO},
        {"text": "     Threats in the DL Ecosystem,\" IEEE Access, 2023",
         "size": Pt(7.5), "color": TEXT_MUTED, "font": FONT_MONO},
        {"text": "[3] Chen et al., \"StegoFL: Steganography & Federated Learning",
         "size": Pt(7.5), "color": TEXT_MUTED, "spacing_before": Pt(3), "font": FONT_MONO},
        {"text": "     to Transmit Malware,\" 2024",
         "size": Pt(7.5), "color": TEXT_MUTED, "font": FONT_MONO},
        {"text": "[4] Goldstein et al., \"Disarming Attacks Inside Neural Network",
         "size": Pt(7.5), "color": TEXT_MUTED, "spacing_before": Pt(3), "font": FONT_MONO},
        {"text": "     Models,\" 2022",
         "size": Pt(7.5), "color": TEXT_MUTED, "font": FONT_MONO},
        {"text": "[5] Zhao et al., \"Toward Detecting Hidden Functionalities in",
         "size": Pt(7.5), "color": TEXT_MUTED, "spacing_before": Pt(3), "font": FONT_MONO},
        {"text": "     Deep Learning Models,\" IEEE TDSC, 2024",
         "size": Pt(7.5), "color": TEXT_MUTED, "font": FONT_MONO},
        {"text": "[6] Li et al., \"Detection of Steganographic Malware Hidden",
         "size": Pt(7.5), "color": TEXT_MUTED, "spacing_before": Pt(3), "font": FONT_MONO},
        {"text": "     in AI Model Weights,\" ACM CCS, 2023",
         "size": Pt(7.5), "color": TEXT_MUTED, "font": FONT_MONO},
        {"text": "[7] Liu et al., \"ReFHD-Net: A Reversible Functionality Hiding",
         "size": Pt(7.5), "color": TEXT_MUTED, "spacing_before": Pt(3), "font": FONT_MONO},
        {"text": "     Framework for DNNs,\" 2024",
         "size": Pt(7.5), "color": TEXT_MUTED, "font": FONT_MONO},
    ]
    add_multiline_text(slide, Inches(7.4), Inches(4.0), Inches(5.3), Inches(2.7),
                       ref_lines)

    # ─── BOTTOM LEFT: Uniqueness Statement ───────────────────────────────
    uniq_card = add_rounded_card(slide, Inches(0.4), Inches(4.7), Inches(6.6), Inches(2.5),
                                 fill_color=BG_CARD, border_color=ACCENT_BLUE, border_width=Pt(1))

    add_text_box(slide, Inches(0.6), Inches(4.8), Inches(5), Inches(0.3),
                 "UNIQUENESS & INNOVATION", font_size=Pt(9),
                 font_color=ACCENT_BLUE, bold=True)

    uniq_lines = [
        {"text": "StegaGuard is NOVEL — no existing commercial or open-source tool",
         "size": Pt(9.5), "color": TEXT_WHITE, "bold": True, "spacing_before": Pt(6)},
        {"text": "performs automated steganalysis of neural network weight tensors.",
         "size": Pt(9.5), "color": TEXT_WHITE, "bold": True},
        {"text": "", "size": Pt(4)},
        {"text": "Improvement Over Prior Art:", "size": Pt(9), "color": TEXT_MUTED,
         "bold": True, "spacing_before": Pt(4)},
        {"text": "• EvilModel (2021) proved the ATTACK — we build the DEFENSE",
         "size": Pt(9), "color": TEXT_MUTED, "spacing_before": Pt(2)},
        {"text": "• Fickling scans pickle bytecode — we scan mathematical weights",
         "size": Pt(9), "color": TEXT_MUTED},
        {"text": "• Neural Cleanse needs retraining — we need ZERO training data",
         "size": Pt(9), "color": TEXT_MUTED},
        {"text": "• First tool combining statistical + bit-plane + behavioral",
         "size": Pt(9), "color": TEXT_MUTED},
        {"text": "  analysis in a single pre-deployment gate",
         "size": Pt(9), "color": TEXT_MUTED},
    ]
    add_multiline_text(slide, Inches(0.6), Inches(5.05), Inches(6.2), Inches(2.0),
                       uniq_lines)

    # Page number
    add_text_box(slide, Inches(12.4), Inches(7.0), Inches(0.5), Inches(0.3),
                 "5", font_size=Pt(9), font_color=TEXT_DIM, alignment=PP_ALIGN.RIGHT)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    print("[1/5] Building Title & Hook slide...")
    build_slide_1(prs)

    print("[2/5] Building Problem & Threat Model slide...")
    build_slide_2(prs)

    print("[3/5] Building 4-Pillar Detection Engine slide...")
    build_slide_3(prs)

    print("[4/5] Building Pipeline & Risk Scoring slide...")
    build_slide_4(prs)

    print("[5/5] Building Diagnostics, Feasibility & Roadmap slide...")
    build_slide_5(prs)

    output_path = "PCC_2026_StegaGuard_Submission.pptx"
    prs.save(output_path)
    print(f"\n{'='*60}")
    print(f"  SUCCESS: {output_path} generated")
    print(f"  Slides: 5 | Format: 16:9 | Theme: Dark Obsidian")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
