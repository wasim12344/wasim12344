#!/usr/bin/env python3
"""
Generate an advanced terminal Neofetch card SVG (860 x 400) featuring:
- Traffic lights terminal window frame
- Left side: Embedded photo with animated falling snow particles and neon cyber glow
- Right side: Staggered Neofetch system specs with terminal color palette
Dimensions match contrib-heatmap.svg (860px width) perfectly.
"""
import base64
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
PHOTO_PATH = os.path.join(REPO_ROOT, "source-photo.jpg")
OUT_PATH = os.path.join(REPO_ROOT, "info-card.svg")

WIDTH = 860
HEIGHT = 410
TITLEBAR_H = 32

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
KEY_COLOR = "#58a6ff"       # Cyan
VAL_COLOR = "#e6edf3"       # Silver white
ACCENT_GREEN = "#3fb950"    # Emerald
MUTED_COLOR = "#8b949e"     # Gray

LINES = [
    ("OS", "Data Analytics & ML Linux Env"),
    ("Host", "Wasim Khan (@wasim12344)"),
    ("Role", "Data Analyst & Python Developer"),
    ("Kernel", "Python 3.12 • SQL • Pandas • NumPy"),
    ("Uptime", "Active Daily Contributor (2026)"),
    ("BI & Tools", "Power BI • Excel • Jupyter • Seaborn"),
    ("Projects", "dmart-sales-analysis, Vrinda-Store"),
    ("Focus", "Exploratory Data Analysis & BI Dashboards"),
]


def generate_snow_particles(count=32, box_w=250, box_h=300):
    random.seed(42)  # Deterministic seed for reproducible SVGs
    particles = []
    for i in range(count):
        x = round(random.uniform(5, box_w - 5), 1)
        r = round(random.uniform(1.0, 2.6), 1)
        opacity = round(random.uniform(0.4, 0.95), 2)
        dur = round(random.uniform(2.5, 5.5), 2)
        delay = round(random.uniform(0.0, 4.0), 2)
        drift = round(random.uniform(-15, 15), 1)
        
        # SMIL animation for pure GitHub SVG compatibility
        p_svg = f"""      <circle cx="{x}" cy="-10" r="{r}" fill="#ffffff" opacity="{opacity}">
        <animate attributeName="cy" from="-10" to="{box_h + 10}" dur="{dur}s" begin="{delay}s" repeatCount="indefinite" />
        <animate attributeName="cx" values="{x};{x + drift};{x}" dur="{dur * 1.5:.1f}s" begin="{delay}s" repeatCount="indefinite" />
      </circle>"""
        particles.append(p_svg)
    return "\n".join(particles)


def render():
    if not os.path.exists(PHOTO_PATH):
        print(f"Error: Photo {PHOTO_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    with open(PHOTO_PATH, "rb") as f:
        photo_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Photo Box Coordinates
    av_x = 35
    av_y = 55
    av_w = 250
    av_h = 320
    av_rx = 14

    snow_svg = generate_snow_particles(count=36, box_w=av_w, box_h=av_h)

    # Right side Neofetch Specs
    specs_x = 320
    start_y = 125
    line_spacing = 28
    spec_rows = []

    for i, (key, val) in enumerate(LINES):
        delay = round(0.15 + i * 0.07, 2)
        y = start_y + i * line_spacing
        spec_rows.append(
            f'    <g class="spec-row" style="animation-delay: {delay}s;">\n'
            f'      <text x="{specs_x}" y="{y}" class="key">{key}:</text>\n'
            f'      <text x="{specs_x + 105}" y="{y}" class="val">{val}</text>\n'
            f'    </g>'
        )
    spec_content = "\n".join(spec_rows)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <linearGradient id="card-bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG2}"/>
      <stop offset="1" stop-color="{BG}"/>
    </linearGradient>

    <!-- Clip path for avatar image and snow container -->
    <clipPath id="avatar-clip">
      <rect x="0" y="0" width="{av_w}" height="{av_h}" rx="{av_rx}"/>
    </clipPath>

    <!-- Scanline beam animation -->
    <linearGradient id="scanline-grad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#58a6ff" stop-opacity="0"/>
      <stop offset="50%" stop-color="#58a6ff" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#58a6ff" stop-opacity="0"/>
    </linearGradient>

    <style>
      .bg {{ fill: url(#card-bg); stroke: {FRAME}; stroke-width: 1; rx: 14px; }}
      .titlebar {{ fill: #161b22; }}
      .title-text {{ fill: {MUTED_COLOR}; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 11px; }}
      .banner-user {{ fill: {ACCENT_GREEN}; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 18px; font-weight: 700; }}
      .banner-sep {{ fill: {MUTED_COLOR}; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 14px; }}
      .key {{ fill: {KEY_COLOR}; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13.5px; font-weight: 600; }}
      .val {{ fill: {VAL_COLOR}; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 13px; }}
      .spec-row {{
        opacity: 0;
        transform: translateY(6px);
        animation: fadeSlide 0.35s ease-out forwards;
      }}
      @keyframes fadeSlide {{
        to {{
          opacity: 1;
          transform: translateY(0);
        }}
      }}
      .neon-border {{
        animation: neonGlow 3s ease-in-out infinite alternate;
      }}
      @keyframes neonGlow {{
        0% {{ stroke: #58a6ff; opacity: 0.7; }}
        50% {{ stroke: #3fb950; opacity: 1; }}
        100% {{ stroke: #38bdf8; opacity: 0.8; }}
      }}
    </style>
  </defs>

  <!-- Window Frame -->
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" class="bg" />

  <!-- Titlebar -->
  <path d="M 0.5,14 A 14,14 0 0,1 14,0.5 L {WIDTH - 14},0.5 A 14,14 0 0,1 {WIDTH - 0.5},14 L {WIDTH - 0.5},{TITLEBAR_H} L 0.5,{TITLEBAR_H} Z" class="titlebar" />
  <line x1="0" y1="{TITLEBAR_H}" x2="{WIDTH}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-width="1" />

  <!-- Window Controls -->
  <circle cx="20" cy="16" r="5" fill="#ff5f56" />
  <circle cx="36" cy="16" r="5" fill="#ffbd2e" />
  <circle cx="52" cy="16" r="5" fill="#27c93f" />

  <!-- Window Title -->
  <text x="{WIDTH / 2}" y="20" class="title-text" text-anchor="middle">wasim@github: ~ (neofetch)</text>

  <!-- LEFT: Animated Avatar with Snow & Glow -->
  <g transform="translate({av_x}, {av_y})">
    <!-- Clip group containing image and animations -->
    <g clip-path="url(#avatar-clip)">
      <image href="data:image/jpeg;base64,{photo_b64}" x="0" y="0" width="{av_w}" height="{av_h}" preserveAspectRatio="xMidYMid slice" />
      
      <!-- Falling Snow Particles -->
{snow_svg}

      <!-- Animated Scanline Sweep -->
      <rect x="0" y="-30" width="{av_w}" height="40" fill="url(#scanline-grad)">
        <animate attributeName="y" from="-40" to="{av_h + 20}" dur="4s" repeatCount="indefinite" />
      </rect>
    </g>

    <!-- Outer Neon Border -->
    <rect x="0" y="0" width="{av_w}" height="{av_h}" rx="{av_rx}" fill="none" class="neon-border" stroke-width="2" />
  </g>

  <!-- RIGHT: Neofetch System Information -->
  <g transform="translate({specs_x}, 82)">
    <text x="0" y="0" class="banner-user">wasim<tspan fill="{MUTED_COLOR}">@</tspan>github</text>
    <text x="0" y="16" class="banner-sep">-------------------------------------</text>
  </g>

  <!-- Specs Rows -->
{spec_content}

  <!-- Divider Line -->
  <line x1="{specs_x}" y1="355" x2="{WIDTH - 35}" y2="355" stroke="{FRAME}" stroke-width="1" />

  <!-- Color Palette Dots & Footer -->
  <g transform="translate({specs_x}, 385)">
    <circle cx="10" cy="0" r="7" fill="#21262d" />
    <circle cx="32" cy="0" r="7" fill="#ff7b72" />
    <circle cx="54" cy="0" r="7" fill="#7ee787" />
    <circle cx="76" cy="0" r="7" fill="#f2cc60" />
    <circle cx="98" cy="0" r="7" fill="#58a6ff" />
    <circle cx="120" cy="0" r="7" fill="#bc8cff" />
    <circle cx="142" cy="0" r="7" fill="#39c5cf" />
    <circle cx="164" cy="0" r="7" fill="#ffffff" />
    <text x="{WIDTH - specs_x - 45}" y="4" fill="{MUTED_COLOR}" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="11" text-anchor="end">neofetch v7.1.0</text>
  </g>
</svg>"""

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Unified Neofetch card with animated snow generated: {OUT_PATH}")


if __name__ == "__main__":
    render()
