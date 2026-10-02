#!/usr/bin/env python3
"""
Generate a sleek, terminal-styled Neofetch info card SVG.
Canvas dimensions (1112 x 875) perfectly align with the ASCII portrait (840 x 875)
when placed side-by-side at 370px and 490px widths in GitHub markdown.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")

WIDTH = 1112
HEIGHT = 875
TITLEBAR_H = 40
PAD_X = 50
PAD_Y = 70

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
KEY_COLOR = "#58a6ff"       # Cyan/Blue
VAL_COLOR = "#e6edf3"       # Crisp white/silver
ACCENT_GREEN = "#3fb950"    # Emerald
MUTED_COLOR = "#8b949e"     # Gray

LINES = [
    ("OS", "Data Analytics & ML Linux Env (x86_64)"),
    ("Host", "Wasim Khan (@wasim12344)"),
    ("Role", "Data Analyst & Python Developer"),
    ("Kernel", "Python 3.12 • SQL • Pandas • NumPy"),
    ("Uptime", "Coding & Analyzing Data Daily"),
    ("Shell", "bash 5.2 / Git / GitHub CLI"),
    ("BI & Tools", "Power BI • Excel • Jupyter • Seaborn • Matplotlib"),
    ("Projects", "dmart-sales-analysis, Vrinda-Store-Data-Analysis"),
    ("Focus", "Exploratory Data Analysis • ETL Pipelines • Business Insights"),
    ("GitHub", "https://github.com/wasim12344"),
]


def render():
    css_delays = []
    line_svgs = []
    start_y = 175
    line_spacing = 54

    for i, (key, val) in enumerate(LINES):
        delay = round(0.1 + i * 0.08, 2)
        y = start_y + i * line_spacing
        line_svgs.append(
            f'    <g class="row" style="animation-delay: {delay}s;">\n'
            f'      <text x="{PAD_X}" y="{y}" class="key">{key}:</text>\n'
            f'      <text x="{PAD_X + 190}" y="{y}" class="val">{val}</text>\n'
            f'    </g>'
        )

    lines_block = "\n".join(line_svgs)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <linearGradient id="card-bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG2}"/>
      <stop offset="1" stop-color="{BG}"/>
    </linearGradient>
    <style>
      .bg {{ fill: url(#card-bg); stroke: {FRAME}; stroke-width: 1; rx: 16px; }}
      .titlebar {{ fill: #161b22; }}
      .title-text {{ fill: {MUTED_COLOR}; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 16px; }}
      .banner-user {{ fill: {ACCENT_GREEN}; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 26px; font-weight: 700; }}
      .banner-sep {{ fill: {MUTED_COLOR}; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 20px; }}
      .key {{ fill: {KEY_COLOR}; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 20px; font-weight: 600; }}
      .val {{ fill: {VAL_COLOR}; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 20px; }}
      .row {{
        opacity: 0;
        transform: translateY(8px);
        animation: fadeSlide 0.4s ease-out forwards;
      }}
      @keyframes fadeSlide {{
        to {{
          opacity: 1;
          transform: translateY(0);
        }}
      }}
    </style>
  </defs>

  <!-- Window Frame -->
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" class="bg" />

  <!-- Titlebar -->
  <path d="M 0.5,16 A 16,16 0 0,1 16,0.5 L {WIDTH - 16},0.5 A 16,16 0 0,1 {WIDTH - 0.5},16 L {WIDTH - 0.5},{TITLEBAR_H} L 0.5,{TITLEBAR_H} Z" class="titlebar" />
  <line x1="0" y1="{TITLEBAR_H}" x2="{WIDTH}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-width="1" />

  <!-- Window Controls -->
  <circle cx="26" cy="20" r="7" fill="#ff5f56" />
  <circle cx="48" cy="20" r="7" fill="#ffbd2e" />
  <circle cx="70" cy="20" r="7" fill="#27c93f" />

  <!-- Title -->
  <text x="{WIDTH / 2}" y="25" class="title-text" text-anchor="middle">wasim@github: ~ (neofetch)</text>

  <!-- Neofetch Header -->
  <g transform="translate({PAD_X}, 95)">
    <text x="0" y="0" class="banner-user">wasim<tspan fill="{MUTED_COLOR}">@</tspan>github</text>
    <text x="0" y="24" class="banner-sep">-----------------------------</text>
  </g>

  <!-- Staggered Rows -->
{lines_block}

  <!-- Divider -->
  <line x1="{PAD_X}" y1="735" x2="{WIDTH - PAD_X}" y2="735" stroke="{FRAME}" stroke-width="1" />

  <!-- Color Palette Dots -->
  <g transform="translate({PAD_X}, 780)">
    <circle cx="15" cy="0" r="14" fill="#21262d" />
    <circle cx="55" cy="0" r="14" fill="#ff7b72" />
    <circle cx="95" cy="0" r="14" fill="#7ee787" />
    <circle cx="135" cy="0" r="14" fill="#f2cc60" />
    <circle cx="175" cy="0" r="14" fill="#58a6ff" />
    <circle cx="215" cy="0" r="14" fill="#bc8cff" />
    <circle cx="255" cy="0" r="14" fill="#39c5cf" />
    <circle cx="295" cy="0" r="14" fill="#ffffff" />
    <text x="{WIDTH - PAD_X * 2}" y="7" fill="{MUTED_COLOR}" font-family="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" font-size="16" text-anchor="end">neofetch v7.1.0</text>
  </g>
</svg>"""

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Info card SVG generated: {OUT}")


if __name__ == "__main__":
    render()
