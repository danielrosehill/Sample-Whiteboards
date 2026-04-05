#!/usr/bin/env python3
"""
Clean whiteboard photos using Fal AI Nano Banana 2 (image-to-image).

Processes all images in ../whiteboards/ and saves cleaned versions to ../graphics/.
Requires: FAL_API_KEY environment variable or ~/.config/nano-whiteboard-doctor/config.json
Dependencies: pip install requests
"""

import base64
import json
import os
import sys
import time
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
WHITEBOARDS_DIR = SCRIPT_DIR.parent / "whiteboards"
GRAPHICS_DIR = SCRIPT_DIR.parent / "graphics"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

FAL_SYNC_URL = "https://fal.run/fal-ai/nano-banana-2/edit"
FAL_QUEUE_URL = "https://queue.fal.run/fal-ai/nano-banana-2/edit"

PROMPT_FILE = SCRIPT_DIR.parent / "prompts" / "default.md"


def load_prompt() -> str:
    """Load prompt from the versioned markdown file, extracting the blockquote."""
    if PROMPT_FILE.exists():
        in_quote = False
        lines = []
        for line in PROMPT_FILE.read_text().splitlines():
            if line.startswith("> "):
                in_quote = True
                lines.append(line[2:])
            elif in_quote and line.strip():
                lines.append(line)
            elif in_quote:
                break
        if lines:
            return " ".join(lines)
    return (
        "Take this whiteboard photograph and convert it into a beautiful and polished "
        "graphic featuring clear labels and icons. Remove the physical whiteboard, "
        "markers, frame, and any background elements -- output only the diagram on a "
        "clean white background. Correct any perspective distortion so the output "
        "appears as a perfectly straight-on, top-down view regardless of the angle "
        "the original photo was taken from. Preserve all the original content, text, "
        "and diagrams. Keep the user's handwriting style and character but make it "
        "more legible and well-organized. The result should be a fully representative "
        "version of the whiteboard content that is much more visually attractive and "
        "easy to understand than the original photo."
    )


DEFAULT_PROMPT = load_prompt()


def get_api_key() -> str:
    """Get API key from env var or Nano Whiteboard Doctor config."""
    key = os.environ.get("FAL_API_KEY")
    if key:
        return key
    config_file = Path.home() / ".config" / "nano-whiteboard-doctor" / "config.json"
    if config_file.exists():
        with open(config_file) as f:
            key = json.load(f).get("api_key")
        if key:
            return key
    print("Error: Set FAL_API_KEY env var or configure via Nano Whiteboard Doctor.", file=sys.stderr)
    sys.exit(1)


def image_to_data_url(path: Path) -> str:
    mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                "webp": "image/webp", "bmp": "image/bmp"}
    mime = mime_map.get(path.suffix.lower().lstrip("."), "image/png")
    b64 = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{b64}"


def call_fal_api(img_path: Path, api_key: str, prompt: str) -> list[dict]:
    headers = {"Authorization": f"Key {api_key}", "Content-Type": "application/json"}
    payload = {
        "prompt": prompt,
        "image_urls": [image_to_data_url(img_path)],
        "output_format": "png",
        "resolution": "1K",
        "num_images": 1,
    }

    resp = requests.post(FAL_SYNC_URL, headers=headers, json=payload, timeout=300)
    resp.raise_for_status()
    result = resp.json()

    if "images" in result and result["images"]:
        return result["images"]

    request_id = result.get("request_id")
    if not request_id:
        return []

    for _ in range(120):
        time.sleep(2)
        status_resp = requests.get(
            f"{FAL_QUEUE_URL}/requests/{request_id}/status",
            headers=headers, timeout=30,
        )
        status_resp.raise_for_status()
        status = status_resp.json()
        if status.get("status") == "COMPLETED":
            result_resp = requests.get(
                f"{FAL_QUEUE_URL}/requests/{request_id}",
                headers=headers, timeout=30,
            )
            result_resp.raise_for_status()
            return result_resp.json().get("images", [])
        if status.get("status") in ("FAILED", "CANCELLED"):
            return []

    return []


def load_prompt_from_file(prompt_file: Path) -> str:
    """Load prompt from a given markdown file, extracting the blockquote."""
    in_quote = False
    lines = []
    for line in prompt_file.read_text().splitlines():
        if line.startswith("> "):
            in_quote = True
            lines.append(line[2:])
        elif in_quote and line.strip():
            lines.append(line)
        elif in_quote:
            break
    if lines:
        return " ".join(lines)
    raise ValueError(f"No blockquote prompt found in {prompt_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Clean whiteboard photos with Fal AI")
    parser.add_argument("--prompt-file", type=Path,
                        help="Path to a style prompt .md file (default: prompts/default.md)")
    parser.add_argument("--image", type=Path,
                        help="Process a single image instead of all in whiteboards/")
    parser.add_argument("--suffix", type=str, default="cleaned",
                        help="Output filename suffix (default: cleaned)")
    args = parser.parse_args()

    api_key = get_api_key()
    GRAPHICS_DIR.mkdir(exist_ok=True)

    # Determine prompt
    if args.prompt_file:
        prompt = load_prompt_from_file(args.prompt_file)
        style_name = args.prompt_file.stem
    else:
        prompt = DEFAULT_PROMPT
        style_name = "cleaned"

    suffix = args.suffix if args.suffix != "cleaned" else style_name

    # Determine images to process
    if args.image:
        if not args.image.exists():
            print(f"Error: Image not found: {args.image}", file=sys.stderr)
            sys.exit(1)
        images = [args.image]
    else:
        all_images = sorted(
            f for f in WHITEBOARDS_DIR.iterdir()
            if f.suffix.lower() in IMAGE_EXTS and not f.stem.endswith("_edited")
        )
        # Skip images that already have output with this suffix
        images = [
            f for f in all_images
            if not (GRAPHICS_DIR / f"{f.stem}_{suffix}.png").exists()
        ]
        if not images:
            print(f"No new whiteboard images to process ({len(all_images)} already done).")
            return

    print(f"Processing {len(images)} whiteboard(s) with style '{suffix}'...")

    for i, img in enumerate(images, 1):
        print(f"  [{i}/{len(images)}] {img.name} ... ", end="", flush=True)
        try:
            result_images = call_fal_api(img, api_key, prompt)
            if not result_images:
                print("FAILED (no output)")
                continue
            for img_data in result_images:
                img_resp = requests.get(img_data["url"], timeout=60)
                img_resp.raise_for_status()
                out_path = GRAPHICS_DIR / f"{img.stem}_{suffix}.png"
                out_path.write_bytes(img_resp.content)
                print(f"-> {out_path.name}")
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)

    print("Done.")


if __name__ == "__main__":
    main()
