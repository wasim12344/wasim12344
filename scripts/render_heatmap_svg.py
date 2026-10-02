#!/usr/bin/env python3
"""
Render data/contributions.json into an animated GitHub contribution heatmap SVG.
Features:
- Terminal-styled window frame with traffic lights and command prompt
- 53-week x 7-day grid with GitHub green color ramps
- Diagonal staggered reveal animation (plays on load and holds)
- Accurate stats bar (Total contributions, streak, best day, legend)
"""
import datetime
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")

# GitHub-ish green ramp: empty -> level 1 -> level 2 -> level 3 -> level 4 -> level 5
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#56e379"]

CELL = 11
GAP = 3
STEP = CELL + GAP
PAD_LEFT = 38
PAD_TOP = 65
DAYS_OF_WEEK = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def level_for(count):
    if count == 0:
        return 0
    if count <= 1:
        return 1
    if count <= 3:
        return 2
    if count <= 6:
        return 3
    if count <= 10:
        return 4
    return 5


def build_grid(days):
    if not days:
        return []
    first = datetime.date.fromisoformat(days[0]["date"])
    # Sunday=0, Monday=1, ..., Saturday=6
    lead_pad = (first.weekday() + 1) % 7
    grid = []
    col = [None] * lead_pad
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        weekday = (date.weekday() + 1) % 7
        while len(col) < weekday:
            col.append(None)
        col.append((d["date"], d["count"], level_for(d["count"])))
        if len(col) == 7:
            grid.append(col)
            col = []
    if col:
        while len(col) < 7:
            col.append(None)
        grid.append(col)
    return grid


def render(data):
    days = data.get("days", [])
    total = data.get("total", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    username = data.get("username", "wasim12344")

    grid = build_grid(days)
    n_cols = len(grid)
    
    # SVG Dimensions
    width = 860
    height = 250

    # Collect month label positions
    month_labels = []
    seen_months = set()
    for ci, col in enumerate(grid):
        for cell in col:
            if cell is not None:
                d = datetime.date.fromisoformat(cell[0])
                key = (d.year, d.month)
                if key not in seen_months and d.day <= 7:
                    seen_months.add(key)
                    month_labels.append((ci, d.strftime("%b")))
                break

    # Build SVG cells
    cells_svg = []
    for ci, col in enumerate(grid):
        x = PAD_LEFT + ci * STEP
        for ri, cell in enumerate(col):
            if cell is None:
                continue
            date_str, count, lvl = cell
            y = PAD_TOP + ri * STEP
            color = PALETTE[lvl]
            # Diagonal stagger delay calculation
            delay = round(ci * 0.016 + ri * 0.035, 3)
            cell_elem = (
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{color}" style="animation-delay: {delay}s;">'
                f'<title>{date_str}: {count} contribution{"s" if count != 1 else ""}</title>'
                f'</rect>'
            )
            cells_svg.append(cell_elem)

    # Month labels SVG
    months_svg = []
    for ci, name in month_labels:
        mx = PAD_LEFT + ci * STEP
        my = PAD_TOP - 7
        months_svg.append(f'<text x="{mx}" y="{my}" class="lbl-month">{name}</text>')

    # Day labels SVG (Mon, Wed, Fri)
    day_labels_svg = []
    for ri, dname in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        dy = PAD_TOP + ri * STEP + 9
        day_labels_svg.append(f'<text x="{PAD_LEFT - 8}" y="{dy}" class="lbl-day">{dname}</text>')

    cells_content = "\n      ".join(cells_svg)
    months_content = "\n      ".join(months_svg)
    days_content = "\n      ".join(day_labels_svg)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <style>
      .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; rx: 12px; }}
      .titlebar {{ fill: #161b22; }}
      .title-text {{ fill: #8b949e; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 11px; }}
      .prompt-user {{ fill: #58a6ff; font-weight: 600; }}
      .prompt-cmd {{ fill: #c9d1d9; }}
      .lbl-month {{ fill: #7d8590; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 10px; }}
      .lbl-day {{ fill: #7d8590; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 9px; text-anchor: end; }}
      .stat-val {{ fill: #58a6ff; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 12px; font-weight: 600; }}
      .stat-lbl {{ fill: #8b949e; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 11px; }}
      .legend-text {{ fill: #7d8590; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 10px; }}
      .cell {{
        opacity: 0;
        transform: translateY(-4px);
        animation: revealCell 0.4s ease-out forwards;
      }}
      @keyframes revealCell {{
        to {{
          opacity: 1;
          transform: translateY(0);
        }}
      }}
    </style>
  </defs>

  <!-- Window Frame -->
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" class="bg" />
  
  <!-- Titlebar -->
  <path d="M 0.5,12.5 A 12,12 0 0,1 12.5,0.5 L {width - 12.5},0.5 A 12,12 0 0,1 {width - 0.5},12.5 L {width - 0.5},32 L 0.5,32 Z" class="titlebar" />
  <line x1="0" y1="32" x2="{width}" y2="32" stroke="#30363d" stroke-width="1" />

  <!-- Window Controls -->
  <circle cx="20" cy="16" r="5" fill="#ff5f56" />
  <circle cx="36" cy="16" r="5" fill="#ffbd2e" />
  <circle cx="52" cy="16" r="5" fill="#27c93f" />

  <!-- Command Prompt in Titlebar -->
  <text x="76" y="20" class="title-text">
    <tspan class="prompt-user">{username}@github</tspan>:<tspan fill="#7d8590">~</tspan>$ <tspan class="prompt-cmd">./contributions.sh --year 2026</tspan>
  </text>

  <!-- Labels -->
  {months_content}
  {days_content}

  <!-- Contribution Cells -->
  <g>
    {cells_content}
  </g>

  <!-- Divider Line -->
  <line x1="20" y1="184" x2="{width - 20}" y2="184" stroke="#21262d" stroke-width="1" />

  <!-- Stats & Legend Footer -->
  <g transform="translate({PAD_LEFT}, 214)">
    <text x="0" y="0">
      <tspan class="stat-val">{total}</tspan> <tspan class="stat-lbl">contributions in the last year</tspan>
      <tspan dx="24" class="stat-val">{current_streak}d</tspan> <tspan class="stat-lbl">current streak</tspan>
      <tspan dx="20" class="stat-val">{longest_streak}d</tspan> <tspan class="stat-lbl">longest streak</tspan>
    </text>

    <!-- Legend -->
    <g transform="translate({width - PAD_LEFT * 2 - 130}, -9)">
      <text x="-6" y="9" class="legend-text" text-anchor="end">Less</text>
      <rect x="0" y="0" width="10" height="10" rx="2" fill="{PALETTE[0]}" stroke="#30363d" stroke-width="0.5" />
      <rect x="14" y="0" width="10" height="10" rx="2" fill="{PALETTE[1]}" />
      <rect x="28" y="0" width="10" height="10" rx="2" fill="{PALETTE[2]}" />
      <rect x="42" y="0" width="10" height="10" rx="2" fill="{PALETTE[3]}" />
      <rect x="56" y="0" width="10" height="10" rx="2" fill="{PALETTE[4]}" />
      <rect x="70" y="0" width="10" height="10" rx="2" fill="{PALETTE[5]}" />
      <text x="88" y="9" class="legend-text">More</text>
    </g>
  </g>
</svg>"""

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Heatmap SVG rendered successfully: {OUT_PATH}")


def main():
    if not os.path.exists(IN_PATH):
        print(f"Error: {IN_PATH} not found. Run fetch_contributions.py first.")
        return
    with open(IN_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    render(data)


if __name__ == "__main__":
    main()
