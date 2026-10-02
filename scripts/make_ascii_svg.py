#!/usr/bin/env python3
"""
Convert an image into a terminal-styled monochrome ASCII art SVG with
a row-by-row SMIL typewriter animation and riding cursor that freezes when done.
"""
import html
import os
import sys
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "wasim-ascii.svg")

COLS = 100
ROWS = 53
CELL_W = 8
CELL_H = 15
RAMP = " .`:-=+*cs#%@"  # Bright (sparse) -> Dark (dense)

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30
ART_W = COLS * CELL_W   # 800
ART_H = ROWS * CELL_H   # 795
CANVAS_W = ART_W + PAD * 2  # 840
CANVAS_H = TITLEBAR_H + ART_H + STATUS_H + PAD  # 875

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
TITLE_TEXT = "#7d8590"
INK = "#c9d1d9"
CURSOR = "#c9d1d9"

ROW_DUR = 0.08  # Fast typing speed
STAGGER = 0.08  # Staggered per row


def main():
    if not os.path.exists(SRC):
        print(f"Error: Source image {SRC} not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {SRC} into ASCII grid ({COLS}x{ROWS})...")
    img = Image.open(SRC).convert("L")

    # Crop to aspect ratio if needed or focus on upper/center body
    w, h = img.size
    target_ratio = COLS / (ROWS * (CELL_H / CELL_W))  # ~ 100 / (53 * 1.875) ~ 1.006
    current_ratio = w / h
    
    if current_ratio > target_ratio:
        # Image is wider than needed, center crop width
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif current_ratio < target_ratio:
        # Image is taller than needed, focus on upper portion (head/chest)
        new_h = int(w / target_ratio)
        img = img.crop((0, 0, w, new_h))

    # Enhance contrast and sharpen features
    img = ImageEnhance.Contrast(img).enhance(1.4)
    img = ImageEnhance.Sharpness(img).enhance(1.5)
    img = img.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    px = img.load()

    # Generate ASCII rows
    ramp_len = len(RAMP)
    rows_txt = []
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            lum = px[x, y] / 255.0
            # Higher lum = brighter -> mapped to start of RAMP (space / sparse)
            idx = int((1.0 - lum) * (ramp_len - 1))
            idx = max(0, min(idx, ramp_len - 1))
            chars.append(RAMP[idx])
        rows_txt.append("".join(chars))

    # Build SVG content with SMIL animations
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '  <defs>',
        '    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">',
        f'      <stop offset="0" stop-color="{BG2}"/>',
        f'      <stop offset="1" stop-color="{BG}"/>',
        '    </linearGradient>',
        '  </defs>',
        f'  <rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#bg)"/>',
        f'  <rect x="0.5" y="0.5" width="{CANVAS_W - 1}" height="{CANVAS_H - 1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
        f'  <line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
        '  <circle cx="20" cy="15.0" r="5" fill="#ff5f56"/>',
        '  <circle cx="36" cy="15.0" r="5" fill="#ffbd2e"/>',
        '  <circle cx="52" cy="15.0" r="5" fill="#27c93f"/>',
        f'  <text x="{CANVAS_W / 2}" y="19.0" fill="{TITLE_TEXT}" font-size="12" text-anchor="middle">wasim@github: ~$ ./whoami.sh</text>',
    ]

    # Generate rows and typing cursors
    for i, line in enumerate(rows_txt):
        y_top = TITLEBAR_H + 7 + i * CELL_H
        baseline_y = y_top + 11.1
        t_start = i * STAGGER
        escaped_text = html.escape(line)

        # Clip path that wipes open left to right
        svg_parts.append(f'  <clipPath id="r{i}">')
        svg_parts.append(f'    <rect x="{PAD}" y="{y_top}" height="{CELL_H}" width="0">')
        svg_parts.append(f'      <animate attributeName="width" from="0" to="{ART_W}" begin="{t_start:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>')
        svg_parts.append('    </rect>')
        svg_parts.append('  </clipPath>')

        # Text element rendered within the clip path
        svg_parts.append(f'  <g clip-path="url(#r{i})">')
        svg_parts.append(f'    <text xml:space="preserve" x="{PAD}" y="{baseline_y}" fill="{INK}" font-size="12.9" textLength="{ART_W}" lengthAdjust="spacing">{escaped_text}</text>')
        svg_parts.append('  </g>')

        # Riding cursor block for this row
        cursor_y = y_top + 1
        svg_parts.append(f'  <rect y="{cursor_y}" width="8" height="{CELL_H - 2}" fill="{CURSOR}" opacity="0">')
        svg_parts.append(f'    <animate attributeName="x" from="{PAD}" to="{PAD + ART_W}" begin="{t_start:.3f}s" dur="{ROW_DUR:.2f}s" fill="freeze"/>')
        svg_parts.append(f'    <set attributeName="opacity" to="0.85" begin="{t_start:.3f}s"/>')
        svg_parts.append(f'    <set attributeName="opacity" to="0" begin="{(t_start + ROW_DUR):.3f}s"/>')
        svg_parts.append('  </rect>')

    # Status bar at the bottom
    total_time = len(rows_txt) * STAGGER
    status_y = CANVAS_H - 12
    svg_parts.append(f'  <line x1="0" y1="{CANVAS_H - STATUS_H}" x2="{CANVAS_W}" y2="{CANVAS_H - STATUS_H}" stroke="{FRAME}"/>')
    svg_parts.append(f'  <text x="{PAD}" y="{status_y}" fill="{TITLE_TEXT}" font-size="11">NORMAL</text>')
    svg_parts.append(f'  <text x="{CANVAS_W / 2}" y="{status_y}" fill="{TITLE_TEXT}" font-size="11" text-anchor="middle">ascii_portrait.art [RO]</text>')
    svg_parts.append(f'  <text x="{CANVAS_W - PAD}" y="{status_y}" fill="{TITLE_TEXT}" font-size="11" text-anchor="end">100% 53:100</text>')
    svg_parts.append('</svg>')

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))
    print(f"Monochrome ASCII SVG generated: {OUT}")


if __name__ == "__main__":
    main()
