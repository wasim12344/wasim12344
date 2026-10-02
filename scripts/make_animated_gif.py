#!/usr/bin/env python3
"""
Generate a smooth looping animated GIF (wasim.gif) from source-photo.jpg.
Overlays realistic falling snow particles and soft winter ambiance
matching the winter Ichigo anime aesthetic, formatted like tensei.gif in Koustubh's profile.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "source-photo.jpg")
OUT = os.path.join(HERE, "..", "wasim.gif")

WIDTH = 320
HEIGHT = 320
NUM_FRAMES = 24
FPS = 15
FRAME_DUR = int(1000 / FPS)  # ~66ms per frame


def generate_animated_gif():
    if not os.path.exists(SRC):
        print(f"Error: {SRC} not found")
        return

    base_img = Image.open(SRC).convert("RGBA")
    
    # Square crop focusing on Ichigo's profile
    w, h = base_img.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    base_img = base_img.crop((left, top, left + min_dim, top + min_dim))
    base_img = base_img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    # Pre-generate snow flake paths for seamless looping
    random.seed(1337)
    num_flakes = 45
    flakes = []
    for _ in range(num_flakes):
        start_x = random.uniform(0, WIDTH)
        speed = random.uniform(2.5, 6.0)
        size = random.uniform(1.2, 3.2)
        alpha = random.randint(120, 240)
        drift_amp = random.uniform(5, 18)
        drift_freq = random.uniform(1, 3)
        drift_phase = random.uniform(0, math.pi * 2)
        # Distance traveled in 1 full loop = speed * NUM_FRAMES
        # To make it loop seamlessly, start_y and loop wrap around
        start_y = random.uniform(0, HEIGHT)
        flakes.append({
            "x": start_x,
            "y": start_y,
            "speed": speed,
            "size": size,
            "alpha": alpha,
            "amp": drift_amp,
            "freq": drift_freq,
            "phase": drift_phase,
        })

    frames = []
    total_fall = HEIGHT + 40

    for f in range(NUM_FRAMES):
        t = f / NUM_FRAMES
        # Subtle breathing ambiance glow
        glow_factor = 1.0 + 0.05 * math.sin(t * 2 * math.pi)
        frame = ImageEnhance.Brightness(base_img.convert("RGB")).enhance(glow_factor).convert("RGBA")

        # Snow layer
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        for flake in flakes:
            # Seamless loop displacement
            fall_dist = (f * flake["speed"] * 4) % total_fall
            cy = (flake["y"] + fall_dist) % total_fall - 20
            cx = flake["x"] + flake["amp"] * math.sin(t * 2 * math.pi * flake["freq"] + flake["phase"])
            cx = cx % WIDTH

            r = flake["size"]
            # Soft glowing snowflake
            draw.ellipse(
                [(cx - r, cy - r), (cx + r, cy + r)],
                fill=(255, 255, 255, flake["alpha"])
            )
            if r > 2.0:
                # Add slight halo for larger flakes
                draw.ellipse(
                    [(cx - r - 1, cy - r - 1), (cx + r + 1, cy + r + 1)],
                    fill=(220, 240, 255, flake["alpha"] // 3)
                )

        composite = Image.alpha_composite(frame, overlay)
        # Convert to P mode with adaptive palette for crisp small GIF
        quantized = composite.convert("RGB").quantize(colors=128, method=Image.Resampling.LANCZOS)
        frames.append(quantized)

    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DUR,
        loop=0,
        optimize=True
    )
    print(f"Successfully generated animated GIF: {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    generate_animated_gif()
