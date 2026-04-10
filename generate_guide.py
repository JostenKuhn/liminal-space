"""
Liminal Space — First Contact PDF Guide Generator
Creates a beautiful, dark-themed premium PDF guide.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import math
import random

# ── Brand Tokens ──
BG = HexColor("#0A0A0F")
BG2 = HexColor("#12121A")
CARD = HexColor("#1A1A26")
PRIMARY = HexColor("#5B4FE8")
GOLD = HexColor("#D4A852")
TEXT = HexColor("#F0EFF8")
MUTED = HexColor("#C0BDD4")
WHITE = HexColor("#FFFFFF")
DARK_LINE = HexColor("#2A2A3A")

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "product")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "First-Contact-Guide.pdf")

PAGE_W, PAGE_H = letter  # 612 x 792
MARGIN = 60
CONTENT_W = PAGE_W - 2 * MARGIN


# ── Helper: draw dark page background ──
def draw_bg(c, color=BG):
    c.setFillColor(color)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=True, stroke=False)


def draw_starfield(c, count=60, seed=42):
    """Draw random stars across the page background."""
    rng = random.Random(seed)
    for _ in range(count):
        x = rng.uniform(0, PAGE_W)
        y = rng.uniform(0, PAGE_H)
        r = rng.uniform(0.3, 1.2)
        alpha = rng.uniform(0.1, 0.35)
        c.setFillColor(WHITE)
        c.setFillAlpha(alpha)
        c.circle(x, y, r, fill=True, stroke=False)
    c.setFillAlpha(1)


def draw_sacred_geometry(c, cx, cy, radius, rings=6, alpha=0.08):
    """Draw a flower-of-life / sacred geometry pattern."""
    c.setStrokeColor(PRIMARY)
    c.setLineWidth(0.4)
    c.setStrokeAlpha(alpha)
    # Central circle
    c.circle(cx, cy, radius, fill=False, stroke=True)
    # 6 surrounding circles (flower of life)
    for i in range(rings):
        angle = math.radians(i * 60)
        px = cx + radius * math.cos(angle)
        py = cy + radius * math.sin(angle)
        c.circle(px, py, radius, fill=False, stroke=True)
    # Second ring
    for i in range(rings):
        angle = math.radians(i * 60 + 30)
        px = cx + radius * 1.73 * math.cos(angle)
        py = cy + radius * 1.73 * math.sin(angle)
        c.circle(px, py, radius, fill=False, stroke=True)
    c.setStrokeAlpha(1)


def draw_concentric_rings(c, cx, cy, num_rings=5, max_r=120, color=PRIMARY, base_alpha=0.06):
    """Draw expanding concentric rings — representing awareness expansion."""
    for i in range(num_rings):
        r = max_r * (i + 1) / num_rings
        a = base_alpha * (1 - i / num_rings)
        c.setStrokeColor(color)
        c.setStrokeAlpha(a + 0.02)
        c.setLineWidth(0.6)
        c.circle(cx, cy, r, fill=False, stroke=True)
    # Center dot
    c.setFillColor(color)
    c.setFillAlpha(0.3)
    c.circle(cx, cy, 3, fill=True, stroke=False)
    c.setStrokeAlpha(1)
    c.setFillAlpha(1)


def draw_brainwave(c, x_start, y, width, freq, amplitude=8, color=PRIMARY, alpha=0.5):
    """Draw a sine wave representing a brainwave frequency."""
    c.setStrokeColor(color)
    c.setStrokeAlpha(alpha)
    c.setLineWidth(1.2)
    p = c.beginPath()
    steps = int(width)
    for i in range(steps):
        px = x_start + i
        py = y + amplitude * math.sin(2 * math.pi * freq * i / width)
        if i == 0:
            p.moveTo(px, py)
        else:
            p.lineTo(px, py)
    c.drawPath(p, stroke=True, fill=False)
    c.setStrokeAlpha(1)


def draw_orbital(c, cx, cy, num_orbits=3, max_r=100, alpha=0.06):
    """Draw orbital ellipses — cosmic/scientific feel."""
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.4)
    for i in range(num_orbits):
        r = max_r * (i + 1) / num_orbits
        c.setStrokeAlpha(alpha + 0.01 * i)
        # Tilted ellipses
        c.saveState()
        c.translate(cx, cy)
        c.rotate(30 * i)
        c.ellipse(-r, -r * 0.4, r, r * 0.4, fill=False, stroke=True)
        c.restoreState()
    # Particles on orbits
    for i in range(num_orbits):
        r = max_r * (i + 1) / num_orbits
        angle = math.radians(60 + 90 * i)
        px = cx + r * math.cos(angle) * math.cos(math.radians(30 * i)) - r * 0.4 * math.sin(angle) * math.sin(math.radians(30 * i))
        py = cy + r * math.cos(angle) * math.sin(math.radians(30 * i)) + r * 0.4 * math.sin(angle) * math.cos(math.radians(30 * i))
        c.setFillColor(GOLD)
        c.setFillAlpha(0.3)
        c.circle(px, py, 2.5, fill=True, stroke=False)
    c.setStrokeAlpha(1)
    c.setFillAlpha(1)


def draw_nebula_glow(c, cx, cy, radius=150, color="#5B4FE8", layers=15):
    """Draw a soft nebula/cosmic glow effect."""
    for i in range(layers):
        r = radius * (1 - i / layers)
        alpha = 0.015 + 0.005 * i / layers
        c.setFillColor(HexColor(color))
        c.setFillAlpha(alpha)
        c.circle(cx, cy, r, fill=True, stroke=False)
    c.setFillAlpha(1)


def draw_constellation(c, seed=99, count=8, cx=None, cy=None, spread=150):
    """Draw a constellation pattern — connected dots."""
    rng = random.Random(seed)
    cx = cx or PAGE_W / 2
    cy = cy or PAGE_H / 2
    points = []
    for _ in range(count):
        px = cx + rng.uniform(-spread, spread)
        py = cy + rng.uniform(-spread, spread)
        points.append((px, py))

    # Draw connecting lines
    c.setStrokeColor(MUTED)
    c.setStrokeAlpha(0.1)
    c.setLineWidth(0.5)
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dist = math.sqrt((points[i][0] - points[j][0])**2 + (points[i][1] - points[j][1])**2)
            if dist < spread * 0.8:
                c.line(points[i][0], points[i][1], points[j][0], points[j][1])

    # Draw dots
    for px, py in points:
        brightness = rng.uniform(0.2, 0.5)
        size = rng.uniform(1.5, 3)
        c.setFillColor(WHITE)
        c.setFillAlpha(brightness)
        c.circle(px, py, size, fill=True, stroke=False)

    c.setStrokeAlpha(1)
    c.setFillAlpha(1)


def draw_eye_symbol(c, cx, cy, size=60, alpha=0.12):
    """Draw a stylized cosmic eye — the all-seeing awareness symbol."""
    c.setStrokeColor(GOLD)
    c.setStrokeAlpha(alpha)
    c.setLineWidth(0.8)
    # Upper and lower arcs of the eye
    p = c.beginPath()
    for i in range(100):
        t = i / 99.0
        angle = math.pi * t
        x = cx - size + 2 * size * t
        y = cy + size * 0.4 * math.sin(angle)
        if i == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    c.drawPath(p, stroke=True, fill=False)

    p = c.beginPath()
    for i in range(100):
        t = i / 99.0
        angle = math.pi * t
        x = cx - size + 2 * size * t
        y = cy - size * 0.4 * math.sin(angle)
        if i == 0:
            p.moveTo(x, y)
        else:
            p.lineTo(x, y)
    c.drawPath(p, stroke=True, fill=False)

    # Iris
    c.setStrokeAlpha(alpha * 1.5)
    c.circle(cx, cy, size * 0.25, fill=False, stroke=True)
    # Pupil
    c.setFillColor(GOLD)
    c.setFillAlpha(alpha * 2)
    c.circle(cx, cy, size * 0.08, fill=True, stroke=False)

    c.setStrokeAlpha(1)
    c.setFillAlpha(1)


IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")


def draw_image_bg(c, filename, opacity=0.35, y_offset=0, height=PAGE_H):
    """Draw an AI-generated image as a full-width page background with light overlay."""
    filepath = os.path.join(IMAGES_DIR, filename)
    if not os.path.exists(filepath):
        return  # graceful fallback if image missing

    # Draw image full-bleed at full strength
    c.saveState()
    c.drawImage(filepath, 0, y_offset, width=PAGE_W, height=height,
                preserveAspectRatio=True, anchor='c', mask='auto')
    c.restoreState()

    # Light overlay — just enough to keep text readable, not kill the image
    c.saveState()
    c.setFillColor(BG)
    c.setFillAlpha(opacity)  # opacity param now controls the OVERLAY darkness
    c.rect(0, 0, PAGE_W, PAGE_H, fill=True, stroke=False)
    c.restoreState()


def draw_image_section(c, filename, x, y, width, height, opacity=0.8, radius=10):
    """Draw an image in a specific area with rounded corners effect."""
    filepath = os.path.join(IMAGES_DIR, filename)
    if not os.path.exists(filepath):
        return

    c.saveState()
    # Clip to rounded rect
    p = c.beginPath()
    p.roundRect(x, y, width, height, radius)
    c.clipPath(p, stroke=0, fill=0)
    c.setFillAlpha(opacity)
    c.drawImage(filepath, x, y, width=width, height=height,
                preserveAspectRatio=True, anchor='c', mask='auto')
    c.restoreState()


def draw_gold_line(c, y, width=CONTENT_W, x=MARGIN):
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.line(x, y, x + width, y)


def draw_page_number(c, page_num):
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, 30, str(page_num))


def draw_section_label(c, label, y):
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN, y, label.upper())
    return y


def draw_title(c, text, y, size=28):
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", size)
    # Handle long titles by wrapping
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = current + " " + word if current else word
        if c.stringWidth(test, "Helvetica-Bold", size) > CONTENT_W:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)

    for line in lines:
        c.drawString(MARGIN, y, line)
        y -= size + 6
    return y


def draw_body(c, text, y, max_width=CONTENT_W, font="Helvetica", size=10.5, color=MUTED, leading=18):
    """Draw wrapped body text. Returns new y position."""
    c.setFillColor(color)
    c.setFont(font, size)

    paragraphs = text.split("\n\n")
    for para in paragraphs:
        words = para.split()
        current_line = ""
        for word in words:
            test = current_line + " " + word if current_line else word
            if c.stringWidth(test, font, size) > max_width:
                c.drawString(MARGIN, y, current_line)
                y -= leading
                current_line = word
                if y < 60:
                    return y  # hit bottom
            else:
                current_line = test
        if current_line:
            c.drawString(MARGIN, y, current_line)
            y -= leading
        y -= 6  # paragraph gap
    return y


def draw_bullet(c, text, y, indent=15, font="Helvetica", size=10.5, color=MUTED, leading=17):
    """Draw a bullet point with wrapping."""
    c.setFillColor(GOLD)
    c.setFont("Helvetica", size)
    c.drawString(MARGIN + 2, y + 1, "\u2022")
    c.setFillColor(color)
    c.setFont(font, size)

    max_w = CONTENT_W - indent
    words = text.split()
    current_line = ""
    first = True
    for word in words:
        test = current_line + " " + word if current_line else word
        if c.stringWidth(test, font, size) > max_w:
            x = MARGIN + indent
            c.drawString(x, y, current_line)
            y -= leading
            current_line = word
            first = False
            if y < 60:
                return y
        else:
            current_line = test
    if current_line:
        c.drawString(MARGIN + indent, y, current_line)
        y -= leading
    return y


def draw_subtitle(c, text, y, size=14):
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", size)
    c.drawString(MARGIN, y, text)
    return y - size - 10


# ══════════════════════════════════════════
# PAGE BUILDERS
# ══════════════════════════════════════════

def page_cover(c):
    draw_bg(c)
    draw_image_bg(c, "cover_cosmic_portal.jpg", opacity=0.3)  # cover: let it shine
    draw_starfield(c, count=40, seed=42)

    # Sacred geometry overlay
    draw_sacred_geometry(c, PAGE_W / 2, PAGE_H * 0.55, radius=90, rings=6, alpha=0.04)

    # Gold accent line
    line_y = PAGE_H * 0.58
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.5)
    c.line(PAGE_W / 2 - 80, line_y, PAGE_W / 2 + 80, line_y)

    # Section label
    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 9)
    label = "LIMINAL SPACE"
    c.drawCentredString(PAGE_W / 2, line_y + 20, label)

    # Title
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(PAGE_W / 2, line_y - 45, "The Liminal Field Manual")

    # Subtitle
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 13)
    c.drawCentredString(PAGE_W / 2, line_y - 72, "OBE Techniques \u00B7 Remote Viewing \u00B7 Consciousness Exploration")

    # Gold line below subtitle
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.3)
    c.line(PAGE_W / 2 - 80, line_y - 92, PAGE_W / 2 + 80, line_y - 92)

    # Bottom text
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawCentredString(PAGE_W / 2, 60, "Step-by-step methods from 50 years of consciousness research")

    c.showPage()


def page_welcome(c):
    draw_bg(c)
    draw_starfield(c, count=35, seed=101)
    draw_constellation(c, seed=55, count=7, cx=PAGE_W - 80, cy=PAGE_H - 120, spread=70)
    y = PAGE_H - 80

    draw_section_label(c, "Welcome", y)
    y -= 30
    y = draw_title(c, "Welcome to Liminal Space", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    body = (
        "What if you could leave your physical body, fully conscious, and explore reality "
        "from the outside? What if you could perceive events happening in distant locations "
        "without being there? What if the human mind had capabilities so extraordinary that "
        "governments spent decades and millions of dollars studying them in classified programs?"
    )
    y = draw_body(c, body, y, color=TEXT, size=11, leading=19)
    y -= 8

    body2 = (
        "This is not science fiction. The CIA studied it. The U.S. military built programs "
        "around it. The Monroe Institute has been training people to do it since 1971. "
        "Peer-reviewed neuroscience journals have published papers on the mechanisms behind it. "
        "And now, you are holding the keys."
    )
    y = draw_body(c, body2, y, color=MUTED)
    y -= 8

    body3 = (
        "This guide contains three precision-engineered binaural beat audio tracks and a "
        "step-by-step protocol based on the same techniques used in the CIA's Gateway Program. "
        "Out-of-body experiences. Remote viewing. Astral travel. Expanded consciousness. These "
        "are not beliefs. They are skills. And like any skill, they can be learned."
    )
    y = draw_body(c, body3, y, color=MUTED)
    y -= 8

    body3b = (
        "What you are about to learn is just the tip of the iceberg. The Focus levels in this "
        "guide are the first three stops on a map that extends far beyond what most people "
        "believe is possible. But everyone starts here."
    )
    y = draw_body(c, body3b, y, color=MUTED)
    y -= 16

    y = draw_subtitle(c, "What You Will Find Inside", y, size=14)
    y -= 4

    items = [
        "The neuroscience behind binaural beats and why governments spent millions studying them",
        "Step-by-step remote viewing technique (the Project Stargate method)",
        "Two full OBE separation techniques: the Rope and the Roll-Out",
        "Focus levels 10, 12, and 15: the foundational states of consciousness",
        "Common experiences during separation and how to handle them",
        "A seven-day progression plan and session journal prompts",
    ]
    for item in items:
        y = draw_bullet(c, item, y)
        y -= 2

    y -= 16
    body4 = (
        "Approach this with curiosity, not expectation. The most profound experiences tend to "
        "arrive when you stop trying to force them."
    )
    y = draw_body(c, body4, y, color=TEXT, font="Helvetica-Oblique", size=11)

    draw_page_number(c, 2)
    c.showPage()


def page_science_1(c):
    draw_bg(c)
    draw_image_bg(c, "science_brainwaves.jpg", opacity=0.5)  # text-heavy, slightly darker
    draw_starfield(c, count=25, seed=201)

    # Brainwave visualizations in background (bottom area)
    draw_brainwave(c, MARGIN, 90, CONTENT_W, freq=8, amplitude=6, color="#5B4FE8", alpha=0.12)
    draw_brainwave(c, MARGIN, 70, CONTENT_W, freq=4, amplitude=10, color="#D4A852", alpha=0.08)
    draw_brainwave(c, MARGIN, 50, CONTENT_W, freq=14, amplitude=4, color="#8B8AA0", alpha=0.06)

    y = PAGE_H - 80

    draw_section_label(c, "The Science", y)
    y -= 30
    y = draw_title(c, "How Binaural Beats Work", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    body = (
        "When you listen to two slightly different frequencies through headphones, one in each "
        "ear, your brain perceives a third frequency: the mathematical difference between the two. "
        "This is called a binaural beat. For example, if your left ear receives 200 Hz and your "
        "right ear receives 210 Hz, your brain generates an internal 10 Hz pulse."
    )
    y = draw_body(c, body, y)
    y -= 8

    body2 = (
        "This phenomenon, known as the frequency following response, causes your neural oscillations "
        "to synchronize with the perceived beat frequency. In simple terms: you can use sound to "
        "guide your brain into specific states of consciousness."
    )
    y = draw_body(c, body2, y)
    y -= 16

    y = draw_subtitle(c, "Brainwave States", y, size=14)
    y -= 4

    states = [
        ("Beta (13-30 Hz)", "Normal waking consciousness. Alert, focused, analytical thinking."),
        ("Alpha (8-13 Hz)", "Relaxed awareness. The state between waking and sleeping. Light meditation."),
        ("Theta (4-8 Hz)", "Deep meditation, hypnagogic imagery, vivid internal experiences. The gateway to non-ordinary states."),
        ("Delta (0.5-4 Hz)", "Deep dreamless sleep. In trained practitioners, conscious access to delta produces the most profound altered states."),
    ]
    for name, desc in states:
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, y, name)
        y -= 16
        y = draw_body(c, desc, y, size=10, leading=16)
        y -= 6

    y -= 8
    body3 = (
        "The audio tracks included with this guide are calibrated to produce beats at 10 Hz (alpha), "
        "7 Hz (theta), and 4 Hz (deep theta/delta). Each frequency corresponds to a specific "
        "Focus level in the Monroe Institute framework."
    )
    y = draw_body(c, body3, y)

    draw_page_number(c, 3)
    c.showPage()


def page_science_2(c):
    draw_bg(c)
    draw_image_bg(c, "cover_cosmic_portal.jpg", opacity=0.55)
    draw_starfield(c, count=25, seed=202)
    # Subtle orbital pattern behind text
    draw_orbital(c, PAGE_W - 90, PAGE_H - 100, num_orbits=3, max_r=70, alpha=0.04)
    y = PAGE_H - 80

    draw_section_label(c, "The Science", y)
    y -= 30
    y = draw_title(c, "The Research Behind This", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    y = draw_subtitle(c, "The Monroe Institute (1971-Present)", y, size=13)
    y -= 2
    body = (
        "Robert Monroe founded the Monroe Institute after years of personal research into "
        "out-of-body experiences. The Institute developed Hemi-Sync, a patented audio technology "
        "that uses binaural beats to synchronize left and right brain hemispheres. Over five decades, "
        "thousands of participants have reported reproducible altered states using their protocols."
    )
    y = draw_body(c, body, y)
    y -= 10

    y = draw_subtitle(c, "The CIA Gateway Analysis (1983)", y, size=13)
    y -= 2
    body2 = (
        "In 1983, U.S. Army Lieutenant Colonel Wayne McDonnell authored a classified analysis of "
        "the Gateway Process for the CIA. The report did not dismiss it. It concluded that "
        "the Monroe Institute's techniques could produce genuine altered states of consciousness "
        "and that the implications were significant enough to warrant serious study. The document "
        "describes how binaural beats synchronize brain hemispheres, how consciousness can "
        "operate beyond the physical body, and how reality itself may be far stranger than "
        "mainstream science acknowledges. It was declassified in 2003. You can read it yourself "
        "on the CIA's public reading room."
    )
    y = draw_body(c, body2, y)
    y -= 10

    y = draw_subtitle(c, "Project Stargate: Remote Viewing", y, size=13)
    y -= 2
    body3 = (
        "The CIA and Defense Intelligence Agency ran a classified program called Project Stargate "
        "for over twenty years. The program trained military personnel to perceive distant "
        "locations, objects, and events using only their minds, a technique called remote viewing. "
        "The results were significant enough that the program received continuous government "
        "funding from 1972 to 1995. When it was finally declassified, the statistical evidence "
        "was called significant by independent reviewers. Remote viewing is not mysticism. It "
        "is a trained skill, and the techniques in this guide lay the groundwork for developing it."
    )
    y = draw_body(c, body3, y)
    y -= 10

    y = draw_subtitle(c, "Tom Campbell: A Physicist's Model", y, size=13)
    y -= 2
    body4 = (
        "Tom Campbell is a physicist who worked with Robert Monroe in the early days of the "
        "Institute. His theory, My Big TOE (Theory of Everything), provides a rigorous scientific "
        "framework where consciousness is not a byproduct of the brain but the fundamental "
        "nature of reality itself. In Campbell's model, out-of-body experiences are not "
        "hallucinations. They are your consciousness accessing a larger information system "
        "that exists beyond physical spacetime. This is not philosophy. It is a testable, "
        "falsifiable model built by a working physicist."
    )
    y = draw_body(c, body4, y)

    draw_page_number(c, 4)
    c.showPage()


def page_beyond_body(c):
    draw_bg(c)
    draw_image_bg(c, "astral_separation.jpg", opacity=0.45)
    draw_starfield(c, count=30, seed=301)
    # Cosmic eye symbol overlay
    draw_eye_symbol(c, PAGE_W / 2, PAGE_H - 60, size=80, alpha=0.06)
    y = PAGE_H - 80

    draw_section_label(c, "Beyond the Body", y)
    y -= 30
    y = draw_title(c, "What Becomes Possible", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    body = (
        "Once you learn to shift your consciousness beyond the physical body, an entirely "
        "new landscape of human capability opens up. These are not theoretical. Each of "
        "these has been documented, studied, and in some cases, operationally deployed by "
        "military and intelligence agencies."
    )
    y = draw_body(c, body, y, color=TEXT, size=11, leading=19)
    y -= 16

    # Astral Travel / OBE
    c.setFillColor(CARD)
    c.roundRect(MARGIN - 10, y - 105, CONTENT_W + 20, 118, 8, fill=True, stroke=False)
    y -= 2
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN + 5, y, "DOCUMENTED SINCE ANCIENT EGYPT")
    y -= 20
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(MARGIN + 5, y, "Astral Travel / Out-of-Body Experience")
    y -= 20
    desc = (
        "Your conscious awareness separates from the physical body and operates independently. "
        "You can perceive your own body from above. You can move through walls. You can travel "
        "to locations both familiar and unknown. Robert Monroe documented thousands of these "
        "experiences with scientific rigor. This is the core skill that everything else builds "
        "upon, and it is exactly what the Focus levels in this guide prepare you for."
    )
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    words = desc.split()
    line = ""
    for word in words:
        test = line + " " + word if line else word
        if c.stringWidth(test, "Helvetica", 10) > CONTENT_W - 10:
            c.drawString(MARGIN + 5, y, line)
            y -= 15
            line = word
        else:
            line = test
    if line:
        c.drawString(MARGIN + 5, y, line)
        y -= 15

    y -= 22

    # Remote Viewing
    c.setFillColor(CARD)
    c.roundRect(MARGIN - 10, y - 105, CONTENT_W + 20, 118, 8, fill=True, stroke=False)
    y -= 2
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN + 5, y, "USED BY CIA / DIA FOR 23 YEARS")
    y -= 20
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(MARGIN + 5, y, "Remote Viewing")
    y -= 20
    desc2 = (
        "The ability to perceive people, places, and events at a distance using only the mind. "
        "The U.S. government's Project Stargate trained operatives to describe targets anywhere "
        "on Earth, sometimes with startling accuracy. Ingo Swann, one of the original remote "
        "viewers, described the rings of Jupiter before NASA's Pioneer 10 confirmed them. "
        "Remote viewing is a learnable protocol. The expanded awareness states in this guide "
        "are the starting point."
    )
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    words = desc2.split()
    line = ""
    for word in words:
        test = line + " " + word if line else word
        if c.stringWidth(test, "Helvetica", 10) > CONTENT_W - 10:
            c.drawString(MARGIN + 5, y, line)
            y -= 15
            line = word
        else:
            line = test
    if line:
        c.drawString(MARGIN + 5, y, line)
        y -= 15

    y -= 22

    # The bigger picture
    c.setFillColor(CARD)
    c.roundRect(MARGIN - 10, y - 75, CONTENT_W + 20, 88, 8, fill=True, stroke=False)
    y -= 2
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN + 5, y, "THE LIMINAL SPACE")
    y -= 20
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(MARGIN + 5, y, "Where You Become Limitless")
    y -= 20
    desc3 = (
        "The liminal space is the threshold between ordinary and extraordinary consciousness. "
        "It is where the rules change. Physical distance becomes irrelevant. Time becomes "
        "flexible. The boundaries of self expand until there are no boundaries at all. Every "
        "great explorer of consciousness, from Monroe to Campbell to the Stargate viewers, "
        "passed through this same threshold. You are standing at it now."
    )
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    words = desc3.split()
    line = ""
    for word in words:
        test = line + " " + word if line else word
        if c.stringWidth(test, "Helvetica", 10) > CONTENT_W - 10:
            c.drawString(MARGIN + 5, y, line)
            y -= 15
            line = word
        else:
            line = test
    if line:
        c.drawString(MARGIN + 5, y, line)
        y -= 15

    draw_page_number(c, 5)
    c.showPage()


def page_focus_1(c):
    draw_bg(c)
    draw_image_bg(c, "focus_levels_tunnel.jpg", opacity=0.45)
    draw_starfield(c, count=20, seed=401)
    # Expanding awareness rings
    draw_concentric_rings(c, PAGE_W - 80, 120, num_rings=7, max_r=100, color=PRIMARY, base_alpha=0.04)
    y = PAGE_H - 80

    draw_section_label(c, "The Focus Levels", y)
    y -= 30
    y = draw_title(c, "Mapping Consciousness", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    body = (
        "The Monroe Institute uses a numbered system called Focus levels to describe different "
        "states of consciousness. Think of them as coordinates on a map. The three tracks included "
        "in this guide target the foundational levels."
    )
    y = draw_body(c, body, y)
    y -= 16

    # Focus 10
    c.setFillColor(CARD)
    c.roundRect(MARGIN - 10, y - 130, CONTENT_W + 20, 145, 8, fill=True, stroke=False)
    y -= 5
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN + 5, y, "TRACK 1  \u2022  10 HZ ALPHA")
    y -= 22
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN + 5, y, "Focus 10 (Door 10): Mind Awake, Body Asleep")
    y -= 22

    desc = (
        "The foundational state. Your physical body enters complete relaxation while your mind "
        "remains alert and aware. Most people experience this as a floating sensation, a "
        "heaviness in the limbs, or a distinct shift in body awareness. You may notice "
        "hypnagogic imagery: flashes of color, geometric patterns, or brief dream-like scenes."
    )
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    words = desc.split()
    line = ""
    for word in words:
        test = line + " " + word if line else word
        if c.stringWidth(test, "Helvetica", 10) > CONTENT_W - 10:
            c.drawString(MARGIN + 5, y, line)
            y -= 15
            line = word
        else:
            line = test
    if line:
        c.drawString(MARGIN + 5, y, line)
        y -= 15

    y -= 24

    # Focus 12
    c.setFillColor(CARD)
    c.roundRect(MARGIN - 10, y - 130, CONTENT_W + 20, 145, 8, fill=True, stroke=False)
    y -= 5
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN + 5, y, "TRACK 2  \u2022  7 HZ THETA")
    y -= 22
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN + 5, y, "Focus 12 (Door 12): Expanded Awareness")
    y -= 22

    desc2 = (
        "A deeper state where your awareness expands beyond the physical body. The sense of "
        "having a body may diminish. Perceptions become more vivid, internal. People often "
        "report a sense of being larger than their physical form, heightened intuition, "
        "and the beginning of non-local perception."
    )
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    words = desc2.split()
    line = ""
    for word in words:
        test = line + " " + word if line else word
        if c.stringWidth(test, "Helvetica", 10) > CONTENT_W - 10:
            c.drawString(MARGIN + 5, y, line)
            y -= 15
            line = word
        else:
            line = test
    if line:
        c.drawString(MARGIN + 5, y, line)
        y -= 15

    draw_page_number(c, 6)
    c.showPage()


def page_focus_2(c):
    draw_bg(c)
    draw_image_bg(c, "remote_viewing_earth.jpg", opacity=0.45)
    draw_starfield(c, count=20, seed=402)
    # Larger expanding rings — deeper state
    draw_concentric_rings(c, 80, 100, num_rings=9, max_r=130, color=GOLD, base_alpha=0.03)
    y = PAGE_H - 80

    draw_section_label(c, "The Focus Levels", y)
    y -= 30
    y = draw_title(c, "The Deeper States", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    # Focus 15
    c.setFillColor(CARD)
    c.roundRect(MARGIN - 10, y - 130, CONTENT_W + 20, 145, 8, fill=True, stroke=False)
    y -= 5
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN + 5, y, "TRACK 3  \u2022  4 HZ THETA/DELTA")
    y -= 22
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN + 5, y, "Focus 15 (Door 15): The No-Time State")
    y -= 22

    desc = (
        "The most advanced state in this guide. Door 15 is described as existing outside of "
        "time. The normal sense of past, present, and future dissolves. Practitioners report "
        "a vast, empty awareness, a void that is simultaneously full of potential. This is the "
        "state from which the most profound experiences emerge: vivid non-physical environments, "
        "encounters with other forms of consciousness, and full out-of-body experiences."
    )
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    words = desc.split()
    line = ""
    for word in words:
        test = line + " " + word if line else word
        if c.stringWidth(test, "Helvetica", 10) > CONTENT_W - 10:
            c.drawString(MARGIN + 5, y, line)
            y -= 15
            line = word
        else:
            line = test
    if line:
        c.drawString(MARGIN + 5, y, line)
        y -= 15

    y -= 30
    y = draw_subtitle(c, "Your Progression Path", y, size=14)
    y -= 6

    body = (
        "These three Doors form a natural progression. Master Door 10 first. It is the "
        "foundation upon which everything else is built. Once you can reliably reach the "
        "mind-awake-body-asleep state, Door 12 becomes accessible naturally. Door 15 represents "
        "the edge of what most practitioners experience in their first months of practice."
    )
    y = draw_body(c, body, y)
    y -= 16

    body2 = (
        "There is no rush. The Monroe Institute's full program includes Focus levels up to 27 "
        "and beyond. The three Doors in this guide give you a solid launchpad."
    )
    y = draw_body(c, body2, y, color=TEXT, font="Helvetica-Oblique", size=11)

    # Visual: progression arrow
    y -= 30
    c.setStrokeColor(DARK_LINE)
    c.setLineWidth(1)
    arrow_y = y
    c.line(MARGIN + 40, arrow_y, PAGE_W - MARGIN - 40, arrow_y)
    # dots
    positions = [MARGIN + 40, PAGE_W / 2, PAGE_W - MARGIN - 40]
    labels = ["Door 10", "Door 12", "Door 15"]
    sublabels = ["Foundation", "Expansion", "Transcendence"]
    for i, (px, label, sub) in enumerate(zip(positions, labels, sublabels)):
        c.setFillColor(PRIMARY)
        c.circle(px, arrow_y, 6, fill=True, stroke=False)
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(px, arrow_y - 20, label)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawCentredString(px, arrow_y - 32, sub)

    draw_page_number(c, 7)
    c.showPage()


def page_first_session_1(c):
    draw_bg(c)
    draw_image_bg(c, "meditation_void.jpg", opacity=0.5)
    draw_starfield(c, count=15, seed=501)
    y = PAGE_H - 80

    draw_section_label(c, "Your First Session", y)
    y -= 30
    y = draw_title(c, "Step-by-Step Protocol", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    y = draw_subtitle(c, "1. Prepare Your Environment", y, size=13)
    y -= 4
    items = [
        "Choose a quiet, dark room where you will not be disturbed for 30 minutes",
        "Set your phone to airplane mode or do not disturb",
        "Use stereo headphones (not speakers). The binaural effect requires separate signals to each ear",
        "Lie down on your back in a comfortable position. A bed or yoga mat works well",
        "Use a light blanket. Your body temperature will drop as you relax",
        "Remove glasses, watches, or anything that creates physical distraction",
    ]
    for item in items:
        y = draw_bullet(c, item, y, size=10, leading=16)
        y -= 2

    y -= 14
    y = draw_subtitle(c, "2. The Preparation Ritual", y, size=13)
    y -= 4

    body = (
        "Before pressing play, spend two minutes on this preparation sequence. These steps "
        "come directly from the Monroe Institute's Gateway program."
    )
    y = draw_body(c, body, y, size=10)
    y -= 6

    # Resonant Energy Balloon
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Energy Conversion Box")
    y -= 16
    body2 = (
        "Visualize a sturdy box with a lid. Place all of your worries, concerns, and mental "
        "chatter inside this box. Close the lid. You can retrieve them later. This simple act "
        "of symbolic containment gives your subconscious permission to let go."
    )
    y = draw_body(c, body2, y, size=10, leading=16)
    y -= 6

    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Resonant Tuning")
    y -= 16
    body3 = (
        "Take three deep breaths. On each exhale, hum or vocalize a long, low tone. Feel the "
        "vibration in your chest and head. This activates the vagus nerve and shifts your "
        "nervous system from sympathetic (fight-or-flight) to parasympathetic (rest-and-digest)."
    )
    y = draw_body(c, body3, y, size=10, leading=16)
    y -= 6

    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN, y, "Affirmation")
    y -= 16
    body4 = (
        "State silently: \"I am more than my physical body. I deeply desire to expand my "
        "awareness beyond the limitations of my physical senses.\" The Monroe Institute uses "
        "this affirmation to set intention. Use your own words if you prefer."
    )
    y = draw_body(c, body4, y, size=10, leading=16)

    draw_page_number(c, 8)
    c.showPage()


def page_first_session_2(c):
    draw_bg(c)
    draw_starfield(c, count=20, seed=502)
    draw_constellation(c, seed=77, count=6, cx=80, cy=100, spread=60)
    y = PAGE_H - 80

    draw_section_label(c, "Your First Session", y)
    y -= 30
    y = draw_title(c, "During and After", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    y = draw_subtitle(c, "3. During the Session", y, size=13)
    y -= 4
    body = (
        "Press play on Door 10. Close your eyes. Allow the audio to guide your "
        "brainwaves. Your only job is passive observation."
    )
    y = draw_body(c, body, y, size=10)
    y -= 6

    items = [
        "Do not try to force anything. The harder you try, the more your analytical mind activates, which is the opposite of what you want",
        "If thoughts arise, notice them and let them pass. Return your attention to the sound",
        "Pay attention to any physical sensations: tingling, heaviness, warmth, vibration",
        "If you see colors, patterns, or images behind your closed eyes, observe them without grasping",
        "You may feel a shift, a moment where your body seems to drop away. This is Door 10. Stay calm",
    ]
    for item in items:
        y = draw_bullet(c, item, y, size=10, leading=16)
        y -= 2

    y -= 14
    y = draw_subtitle(c, "4. Common First-Session Experiences", y, size=13)
    y -= 4

    experiences = [
        ("Deep relaxation", "Nearly everyone experiences profound physical relaxation. This alone is valuable."),
        ("Hypnagogic imagery", "Flashes of light, geometric patterns, brief dreamlike scenes. Your brain is entering theta."),
        ("Vibrational sensations", "A buzzing or humming feeling throughout the body. This is significant. It often precedes deeper states."),
        ("Floating or sinking", "A sense that your body is lighter or heavier than normal, or that you are gently rocking."),
        ("Time distortion", "Twenty minutes may feel like five, or like an hour. This is a sign of altered state access."),
        ("Sleep", "Falling asleep is common and completely fine. Your brain is learning a new skill. It gets better with practice."),
    ]
    for name, desc in experiences:
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, name)
        y -= 15
        y = draw_body(c, desc, y, size=9.5, leading=15)
        y -= 4

    y -= 10
    y = draw_subtitle(c, "5. After the Session", y, size=13)
    y -= 4
    body2 = (
        "Open your eyes slowly. Take a moment before moving. Write down anything you experienced, "
        "no matter how small. These notes become invaluable as patterns emerge over multiple sessions."
    )
    y = draw_body(c, body2, y, size=10)

    draw_page_number(c, 9)
    c.showPage()


def page_journaling(c):
    draw_bg(c)
    draw_starfield(c, count=15, seed=601)
    y = PAGE_H - 80

    draw_section_label(c, "Your First Session", y)
    y -= 30
    y = draw_title(c, "Session Journal Prompts", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    body = (
        "After each session, spend five minutes with these prompts. Your journal is the most "
        "important tool for tracking progress and recognizing patterns."
    )
    y = draw_body(c, body, y)
    y -= 16

    prompts = [
        "What physical sensations did I notice? (heaviness, tingling, warmth, vibration)",
        "Did I see any imagery? Describe colors, shapes, scenes, however fleeting.",
        "Did I notice any shift in body awareness? A moment where the body felt distant?",
        "How did time feel? Faster? Slower? Did I lose track?",
        "Did I fall asleep? If so, at approximately what point?",
        "What was my emotional state during the session? Calm? Restless? Anxious? Peaceful?",
        "Did anything surprise me?",
        "On a scale of 1-10, how deep did the relaxation feel?",
    ]

    for i, prompt in enumerate(prompts):
        # Card background
        card_h = 42
        c.setFillColor(CARD)
        c.roundRect(MARGIN - 5, y - card_h + 14, CONTENT_W + 10, card_h, 6, fill=True, stroke=False)

        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN + 8, y, f"{i + 1}.")
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 10)

        # Wrap prompt text
        words = prompt.split()
        line = ""
        px = MARGIN + 28
        ly = y
        for word in words:
            test = line + " " + word if line else word
            if c.stringWidth(test, "Helvetica", 10) > CONTENT_W - 40:
                c.drawString(px, ly, line)
                ly -= 14
                line = word
            else:
                line = test
        if line:
            c.drawString(px, ly, line)

        y -= card_h + 8

    draw_page_number(c, 10)
    c.showPage()


def page_troubleshooting(c):
    draw_bg(c)
    draw_starfield(c, count=20, seed=701)
    y = PAGE_H - 80

    draw_section_label(c, "Troubleshooting", y)
    y -= 30
    y = draw_title(c, "Common Questions", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    faqs = [
        (
            "I keep falling asleep. Is that normal?",
            "Completely normal, especially in the first week. Your brain is accustomed to interpreting "
            "deep relaxation as a cue to sleep. Two techniques help: try sitting at a slight incline "
            "instead of lying flat, and practice at a time when you are alert, not tired. Morning "
            "sessions work well for many people."
        ),
        (
            "I did not feel anything significant.",
            "Adjust your expectations. The first few sessions are about training your brain to respond "
            "to the frequencies. Most people notice at least deep relaxation. Subtle shifts, a slight "
            "change in body awareness, a flicker of color, these are meaningful. Note them. "
            "Consistency matters more than intensity."
        ),
        (
            "I felt vibrations and it startled me.",
            "This is excellent. The vibrational state is a well-documented phenomenon that often "
            "precedes deeper experiences. It feels like a strong buzzing or electrical humming "
            "throughout your body. Next time, try to remain calm and observe. Let the vibrations "
            "intensify without resistance. You are on the right path."
        ),
        (
            "How long until I have a full out-of-body experience?",
            "This varies widely. Some people report experiences within the first few sessions. "
            "For most, it takes consistent practice over two to eight weeks. Focus on mastering "
            "Door 10 first. The mind-awake-body-asleep state is the foundation. Everything else "
            "follows from there."
        ),
        (
            "Is this safe? Can anything go wrong?",
            "In over fifty years of documented research at the Monroe Institute, there are no "
            "reports of harm from binaural beat meditation. The worst case is that you fall asleep "
            "or feel nothing. You are always in control. Any sudden intention to return to normal "
            "awareness brings you back immediately. Think of it as a lucid dream you can exit at will."
        ),
    ]

    for question, answer in faqs:
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, y, question)
        y -= 18
        y = draw_body(c, answer, y, size=9.5, leading=15)
        y -= 14

    draw_page_number(c, 11)
    c.showPage()


def page_protocol(c):
    draw_bg(c)
    draw_starfield(c, count=25, seed=801)
    # Brainwave showing progression
    draw_brainwave(c, MARGIN, 55, CONTENT_W, freq=10, amplitude=5, color="#5B4FE8", alpha=0.1)
    draw_brainwave(c, MARGIN, 42, CONTENT_W, freq=5, amplitude=7, color="#D4A852", alpha=0.08)
    y = PAGE_H - 80

    draw_section_label(c, "7-Day Protocol", y)
    y -= 30
    y = draw_title(c, "Your First Week", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    body = (
        "Follow this schedule for your first seven days. Each session is twenty minutes. "
        "Practice at the same time each day if possible. Consistency trains your brain to "
        "enter these states more quickly."
    )
    y = draw_body(c, body, y)
    y -= 20

    days = [
        ("Day 1", "Door 10", "Introduction. Follow the full preparation ritual. Observe what happens. Journal after.", "#5B4FE8"),
        ("Day 2", "Door 10", "Repeat. You may notice you relax faster. Pay attention to any new sensations.", "#5B4FE8"),
        ("Day 3", "Door 10", "Deepening. Try to notice the exact moment your body falls asleep while your mind stays awake.", "#5B4FE8"),
        ("Day 4", "Door 10", "Consolidation. By now you should be reaching relaxation faster. Note any imagery.", "#5B4FE8"),
        ("Day 5", "Door 12", "Expansion. Move to Door 12. The deeper frequency may feel unfamiliar. That is expected.", "#6E63F0"),
        ("Day 6", "Door 12", "Exploration. Your second session at this level. Allow your awareness to expand. Do not direct it.", "#6E63F0"),
        ("Day 7", "Door 15", "The deep end. Use Door 15. This is theta/delta territory. Let go completely.", "#D4A852"),
    ]

    for day, track, instruction, color in days:
        # Card
        card_h = 56
        c.setFillColor(CARD)
        c.roundRect(MARGIN - 5, y - card_h + 16, CONTENT_W + 10, card_h, 6, fill=True, stroke=False)

        # Day label
        c.setFillColor(HexColor(color))
        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN + 8, y, day)

        # Track
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(MARGIN + 65, y + 1, track)

        # Instruction
        y -= 17
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9.5)
        words = instruction.split()
        line = ""
        for word in words:
            test = line + " " + word if line else word
            if c.stringWidth(test, "Helvetica", 9.5) > CONTENT_W - 30:
                c.drawString(MARGIN + 8, y, line)
                y -= 14
                line = word
            else:
                line = test
        if line:
            c.drawString(MARGIN + 8, y, line)

        y -= card_h - 12

    y -= 16
    body2 = (
        "After completing this protocol, you will have a solid foundation in all three Focus "
        "levels. Most people find that their experiences deepen significantly between days 4 "
        "and 7. Continue practicing with whichever track resonates most."
    )
    y = draw_body(c, body2, y, color=TEXT, font="Helvetica-Oblique", size=10)

    draw_page_number(c, 12)
    c.showPage()


def page_remote_viewing(c):
    draw_bg(c)
    draw_image_bg(c, "remote_viewing_earth.jpg", opacity=0.5)
    draw_starfield(c, count=20, seed=601)
    draw_eye_symbol(c, PAGE_W - 80, PAGE_H - 80, size=50, alpha=0.06)
    y = PAGE_H - 80

    draw_section_label(c, "Technique 1", y)
    y -= 30
    y = draw_title(c, "Remote Viewing", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 25

    body = (
        "This is the method used in Project Stargate. It works by training your "
        "consciousness to perceive a target location without physically being there. "
        "The key distinction: when details arrive that you did not deliberately place, "
        "you are no longer imagining. You are viewing."
    )
    y = draw_body(c, body, y, color=TEXT, size=11, leading=18)
    y -= 12

    y = draw_subtitle(c, "The Target Projection Method", y, size=13)
    y -= 4

    steps = [
        ("Step 1: Reach Door 12", "Use the Door 12 audio session to enter the expanded awareness state. Wait until your body feels distant and your mind feels vast."),
        ("Step 2: Choose a target", "Pick a real location you know well. A room in your house, a friend's kitchen, a place you visit often. Start familiar."),
        ("Step 3: Build the scene", "Visualize the location in detail. The colours, the textures, the objects. Place yourself inside it mentally. See the walls. The floor. The light."),
        ("Step 4: Shift from imagining to perceiving", "This is the critical step. Stop constructing the scene. Instead, just observe. Let details arrive on their own. Notice things you did not deliberately put there. A shadow. A sound. An object in a new position."),
        ("Step 5: Move through the space", "Without forcing it, drift to another part of the location. Turn a corner. Look at something you would not normally notice. A book spine. A crack in paint. The pattern of light on a surface."),
        ("Step 6: Record everything", "Immediately after the session, write down every detail, especially the ones that surprised you. Later, verify what you can. This builds confidence and refines your accuracy."),
    ]
    for title, desc in steps:
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, title)
        y -= 16
        y = draw_body(c, desc, y, size=9.5, leading=15)
        y -= 6

    y -= 8
    tip = (
        "Start with locations you can verify. Remote view your own living room from another "
        "room. Ask a friend to place an object somewhere and try to perceive it. Verification "
        "is what transforms this from meditation into a skill."
    )
    y = draw_body(c, tip, y, color=TEXT, font="Helvetica-Oblique", size=10, leading=16)

    draw_page_number(c, 13)
    c.showPage()


def page_obe_techniques(c):
    draw_bg(c)
    draw_image_bg(c, "astral_separation.jpg", opacity=0.5)
    draw_starfield(c, count=20, seed=602)
    draw_concentric_rings(c, PAGE_W - 70, 100, num_rings=6, max_r=80, color=GOLD, base_alpha=0.04)
    y = PAGE_H - 80

    draw_section_label(c, "Technique 2", y)
    y -= 30
    y = draw_title(c, "OBE Separation Methods", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 25

    body = (
        "These are the two most reliable methods for achieving conscious out-of-body "
        "separation. Both were used by Robert Monroe and refined by decades of practitioners. "
        "Try both. One will feel more natural to you. Use that one."
    )
    y = draw_body(c, body, y, color=TEXT, size=11, leading=18)
    y -= 14

    # The Rope
    c.setFillColor(CARD)
    c.roundRect(MARGIN - 10, y - 175, CONTENT_W + 20, 188, 8, fill=True, stroke=False)
    y -= 5
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN + 5, y, "METHOD 1")
    y -= 20
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN + 5, y, "The Rope Technique")
    y -= 20

    rope_steps = [
        "Enter Door 15 using the audio session. Wait for the vibrational state.",
        "Imagine a thick rope hanging above you in the darkness, directly above your chest.",
        "Without moving your physical hands, reach up with your non-physical hands and grab the rope.",
        "Pull yourself upward, hand over hand. You are not moving muscles. You are moving intention.",
        "With each pull, vibrations may intensify. You may hear a rushing sound. Keep pulling.",
        "At some point you will feel a pop, a click, or a sudden lightness. That is separation.",
    ]
    for step in rope_steps:
        y = draw_bullet(c, step, y, size=9.5, leading=14, color=MUTED, indent=15)
        y -= 1

    y -= 20

    # The Roll-Out
    c.setFillColor(CARD)
    c.roundRect(MARGIN - 10, y - 155, CONTENT_W + 20, 168, 8, fill=True, stroke=False)
    y -= 5
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN + 5, y, "METHOD 2")
    y -= 20
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN + 5, y, "The Roll-Out Technique")
    y -= 20

    roll_steps = [
        "Enter Door 15. Wait for deep relaxation and the vibrational stage.",
        "Without moving your physical body, try to roll sideways, as if rolling out of bed.",
        "Use pure intention. No muscles. No physical movement. Just the feeling of rolling.",
        "You may feel resistance at first, as if stuck. Keep rolling gently but persistently.",
        "The vibrations will intensify. Then suddenly you will be free, beside or above your body.",
        "Stay calm. You are safe. You will always return. Simply open your physical eyes to come back.",
    ]
    for step in roll_steps:
        y = draw_bullet(c, step, y, size=9.5, leading=14, color=MUTED, indent=15)
        y -= 1

    draw_page_number(c, 14)
    c.showPage()


def page_obe_tips(c):
    draw_bg(c)
    draw_image_bg(c, "meditation_void.jpg", opacity=0.5)
    draw_starfield(c, count=20, seed=603)
    y = PAGE_H - 80

    draw_section_label(c, "Technique 2 (continued)", y)
    y -= 30
    y = draw_title(c, "Making Separation Work", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 25

    y = draw_subtitle(c, "Common Experiences During Separation", y, size=13)
    y -= 6

    experiences = [
        ("Vibrations", "A buzzing or humming sensation throughout your body. This is the vibrational state and it is the precursor to separation. Let it build. Do not resist it."),
        ("Rushing sounds", "A loud whooshing, roaring, or wind-like sound. This often accompanies the transition. It passes quickly."),
        ("Sleep paralysis", "If you feel unable to move, do not panic. This is your body in its natural sleep state. Your consciousness is simply awake during it. Use the Rope or Roll-Out from this state."),
        ("Floating sensation", "You may feel as though you are rising, hovering, or drifting upward. Go with it. This can lead directly to a full separation."),
        ("Seeing your own body", "If you separate successfully, you may perceive your physical body below or beside you. This is normal and one of the most commonly reported experiences."),
    ]
    for title, desc in experiences:
        c.setFillColor(TEXT)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, y, title)
        y -= 16
        y = draw_body(c, desc, y, size=9.5, leading=15)
        y -= 6

    y -= 10
    y = draw_subtitle(c, "Key Principles", y, size=13)
    y -= 4

    principles = [
        "Do not try harder. Effort activates the analytical mind, which blocks altered states. Let go.",
        "Consistency matters more than session length. Practice daily, same time if possible.",
        "If you fall asleep, that is normal. Your brain is learning the boundary between sleep and awareness.",
        "Fear blocks separation. If you feel fear, remind yourself: this is your consciousness, it is always safe, and you can return instantly by opening your eyes.",
        "Write everything down immediately after each session. Patterns emerge over days and weeks.",
    ]
    for principle in principles:
        y = draw_bullet(c, principle, y, size=9.5, leading=14, color=MUTED, indent=15)
        y -= 3

    draw_page_number(c, 15)
    c.showPage()


def page_whats_next(c):
    draw_bg(c)
    draw_image_bg(c, "focus_levels_tunnel.jpg", opacity=0.4)
    draw_starfield(c, count=30, seed=901)
    # Sacred geometry + nebula — the full potential
    draw_sacred_geometry(c, PAGE_W / 2, PAGE_H * 0.3, radius=100, rings=6, alpha=0.04)
    draw_nebula_glow(c, PAGE_W / 2, PAGE_H * 0.3, radius=160, color="#5B4FE8", layers=15)
    y = PAGE_H - 80

    draw_section_label(c, "What Comes Next", y)
    y -= 30
    y = draw_title(c, "This Was First Contact", y, size=26)
    y -= 10
    draw_gold_line(c, y)
    y -= 30

    body = (
        "You have taken the first step into a world that most people do not know exists. "
        "The vibrational sensations, the imagery, the shift in body awareness: these are "
        "not placebo effects. They are your consciousness beginning to recognize that it "
        "is not confined to your skull."
    )
    y = draw_body(c, body, y, color=TEXT, size=11, leading=19)
    y -= 8

    body2 = (
        "Door 10 through 15 is the launchpad. The Monroe Institute's full map extends "
        "through Focus 21, the bridge to other realities, Focus 27, a state described as "
        "a reception center for non-physical consciousness, and beyond. Remote viewing. "
        "Astral navigation. Communication with non-physical intelligence. Perception across "
        "time. These are not fantasies. They are documented capabilities that become available "
        "as you master progressively deeper states."
    )
    y = draw_body(c, body2, y, size=10.5)
    y -= 8

    body3 = (
        "The liminal space is where ordinary limits dissolve. Where physical distance, linear "
        "time, and the boundaries of the self become negotiable. Every advanced practitioner "
        "started exactly where you are now, with a pair of headphones and the willingness "
        "to discover what they are truly capable of."
    )
    y = draw_body(c, body3, y, size=10.5)
    y -= 16

    y = draw_subtitle(c, "The Full Exploration", y, size=14)
    y -= 6

    items = [
        "Complete binaural beat library: all Doors through 21 and beyond",
        "Remote viewing protocols: trained perception at a distance",
        "Advanced OBE techniques: phasing, energy body activation, astral navigation",
        "A growing library of consciousness exploration resources",
    ]
    for item in items:
        y = draw_bullet(c, item, y, color=MUTED, size=10.5)
        y -= 4

    y -= 20

    # CTA box
    c.setFillColor(CARD)
    c.setStrokeColor(PRIMARY)
    c.setLineWidth(1)
    c.roundRect(MARGIN + 20, y - 95, CONTENT_W - 40, 105, 10, fill=True, stroke=True)

    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(PAGE_W / 2, y - 18, "This Was First Contact.")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10.5)
    c.drawCentredString(PAGE_W / 2, y - 40, "What you have experienced is just the threshold.")
    c.drawCentredString(PAGE_W / 2, y - 56, "The full exploration is available at enterliminalspace.com")
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(PAGE_W / 2, y - 78, "Step through.")

    draw_page_number(c, 16)
    c.showPage()


def page_back_cover(c):
    draw_bg(c)
    draw_image_bg(c, "back_cover_cosmos.jpg", opacity=0.25)  # back cover: most visible
    draw_starfield(c, count=60, seed=999)
    draw_sacred_geometry(c, PAGE_W / 2, PAGE_H / 2, radius=120, rings=6, alpha=0.04)
    draw_concentric_rings(c, PAGE_W / 2, PAGE_H / 2, num_rings=5, max_r=200, color=PRIMARY, base_alpha=0.03)

    # Center content
    cy = PAGE_H / 2

    # Logo
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PAGE_W / 2 - 30, cy + 10, "Liminal")
    c.setFillColor(PRIMARY)
    c.drawCentredString(PAGE_W / 2 + 55, cy + 10, "Space")

    # Gold line
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.3)
    c.line(PAGE_W / 2 - 40, cy - 10, PAGE_W / 2 + 40, cy - 10)

    # URL
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 10)
    c.drawCentredString(PAGE_W / 2, cy - 30, "enterliminalspace.com")

    # Copyright
    c.setFillColor(HexColor("#555566"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(PAGE_W / 2, 50, "Copyright 2026 Liminal Space. All rights reserved.")
    c.drawCentredString(PAGE_W / 2, 38, "This guide is for personal use only. Do not redistribute.")

    c.showPage()


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    c = canvas.Canvas(OUTPUT_PATH, pagesize=letter)
    c.setTitle("The Liminal Field Manual")
    c.setAuthor("Liminal Space")
    c.setSubject("OBE techniques, remote viewing methods, and consciousness exploration")

    print("Generating The Liminal Field Manual...")

    page_cover(c)
    print("  Cover page")
    page_welcome(c)
    print("  Welcome")
    page_science_1(c)
    print("  Science (1/2)")
    page_science_2(c)
    print("  Science (2/2)")
    page_beyond_body(c)
    print("  Beyond the Body — remote viewing, astral travel")
    page_focus_1(c)
    print("  Focus levels (1/2)")
    page_focus_2(c)
    print("  Focus levels (2/2)")
    page_first_session_1(c)
    print("  First session (1/2)")
    page_first_session_2(c)
    print("  First session (2/2)")
    page_journaling(c)
    print("  Journal prompts")
    page_troubleshooting(c)
    print("  Troubleshooting")
    page_protocol(c)
    print("  7-day protocol")
    page_remote_viewing(c)
    print("  Remote viewing technique")
    page_obe_techniques(c)
    print("  OBE separation methods")
    page_obe_tips(c)
    print("  OBE tips and common experiences")
    page_whats_next(c)
    print("  What's next")
    page_back_cover(c)
    print("  Back cover")

    c.save()
    file_size = os.path.getsize(OUTPUT_PATH) / 1024
    print(f"\nSaved: {OUTPUT_PATH} ({file_size:.0f} KB, 14 pages)")


if __name__ == "__main__":
    main()
