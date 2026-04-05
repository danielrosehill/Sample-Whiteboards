#!/usr/bin/env python3
"""
Create before/after comparison graphics for whiteboard cleanups.
Stacks original (top) and cleaned (bottom) vertically with labels.
"""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent
WHITEBOARDS_DIR = SCRIPT_DIR.parent / "whiteboards"
GRAPHICS_DIR = SCRIPT_DIR.parent / "graphics"
COMPARISONS_DIR = SCRIPT_DIR.parent / "comparisons"

LABEL_HEIGHT = 60
PADDING = 20
BG_COLOR = (30, 30, 30)
LABEL_COLOR = (255, 255, 255)

# Mapping: (whiteboard filename, graphics suffix, style label)
PAIRS = [
    ("030426.jpg", "neon-sign", "Neon Sign"),
    ("IMG20260405125048.jpg", "corporate-clean", "Corporate Clean"),
    ("demo1_before.png", "chalkboard", "Chalkboard"),
    ("demo2_before.png", "blueprint", "Blueprint"),
    ("demo3_before.png", "pixel-art", "Pixel Art"),
]


def get_font(size: int):
    """Try to load a nice font, fall back to default."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-Bold.ttf",
    ]
    for fp in font_paths:
        if Path(fp).exists():
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def create_comparison(before_path: Path, after_path: Path, style_name: str, output_path: Path):
    """Stack before (top) and after (bottom) with labels."""
    before = Image.open(before_path).convert("RGB")
    after = Image.open(after_path).convert("RGB")

    # Normalize widths to the larger of the two
    target_w = max(before.width, after.width, 1024)

    def resize_to_width(img, w):
        ratio = w / img.width
        return img.resize((w, int(img.height * ratio)), Image.LANCZOS)

    before = resize_to_width(before, target_w)
    after = resize_to_width(after, target_w)

    total_h = LABEL_HEIGHT + before.height + PADDING + LABEL_HEIGHT + after.height + PADDING
    canvas = Image.new("RGB", (target_w, total_h), BG_COLOR)

    font = get_font(32)
    draw = ImageDraw.Draw(canvas)

    # Before label + image
    y = 0
    bbox = draw.textbbox((0, 0), "BEFORE", font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((target_w - tw) // 2, (LABEL_HEIGHT - (bbox[3] - bbox[1])) // 2),
              "BEFORE", fill=LABEL_COLOR, font=font)
    y += LABEL_HEIGHT
    canvas.paste(before, (0, y))
    y += before.height + PADDING

    # After label + image
    label = f"AFTER — {style_name}"
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((target_w - tw) // 2, y + (LABEL_HEIGHT - (bbox[3] - bbox[1])) // 2),
              label, fill=LABEL_COLOR, font=font)
    y += LABEL_HEIGHT
    canvas.paste(after, (0, y))

    canvas.save(output_path, "PNG")
    print(f"  -> {output_path.name} ({target_w}x{total_h})")


def main():
    COMPARISONS_DIR.mkdir(exist_ok=True)
    font = get_font(32)  # pre-check font availability

    created = 0
    for wb_name, suffix, style_label in PAIRS:
        before = WHITEBOARDS_DIR / wb_name
        stem = Path(wb_name).stem
        after = GRAPHICS_DIR / f"{stem}_{suffix}.png"

        if not before.exists():
            print(f"  SKIP {wb_name}: original not found")
            continue
        if not after.exists():
            print(f"  SKIP {wb_name}: cleaned version ({after.name}) not found yet")
            continue

        output = COMPARISONS_DIR / f"{stem}_comparison_{suffix}.png"
        print(f"  {wb_name} + {after.name} ...")
        create_comparison(before, after, style_label, output)
        created += 1

    print(f"Done. Created {created} comparison(s).")


if __name__ == "__main__":
    main()
