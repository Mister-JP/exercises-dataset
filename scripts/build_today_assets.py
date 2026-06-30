#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ASSET_DIR = ROOT / "today-assets"
SIZE = 720
GIF_FRAME_DURATION_MS = 650


def contain_square(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGB")
    image.thumbnail((SIZE, SIZE), Image.Resampling.LANCZOS)
    out = Image.new("RGB", (SIZE, SIZE), "white")
    out.paste(image, ((SIZE - image.width) // 2, (SIZE - image.height) // 2))
    return out


def crop_panels(sheet: Image.Image) -> list[Image.Image]:
    width, height = sheet.size
    panels: list[Image.Image] = []
    for index in range(4):
        left = round(index * width / 4)
        right = round((index + 1) * width / 4)
        crop = sheet.crop((left, 0, right, height))
        panels.append(contain_square(crop))
    return panels


def build_asset_dir(asset_dir: Path) -> None:
    sheets_dir = asset_dir / "sheets"
    if not sheets_dir.exists():
        return
    for sheet_path in sorted(sheets_dir.glob("*.png")):
        if sheet_path.name.startswith("ai-reference"):
            continue
        slug = sheet_path.stem
        frames = crop_panels(Image.open(sheet_path))
        frames[0].save(asset_dir / f"{slug}.jpg", quality=94, optimize=True)
        sequence = frames + frames[-2:0:-1]
        sequence[0].save(
            asset_dir / f"{slug}.gif",
            save_all=True,
            append_images=sequence[1:],
            duration=GIF_FRAME_DURATION_MS,
            loop=0,
            optimize=True,
            disposal=2,
        )


def main() -> None:
    asset_dirs = [ROOT / arg for arg in sys.argv[1:]] or [DEFAULT_ASSET_DIR]
    for asset_dir in asset_dirs:
        build_asset_dir(asset_dir)


if __name__ == "__main__":
    main()
