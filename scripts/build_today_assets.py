#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "today-assets"
SHEETS = ASSETS / "sheets"
SIZE = 720
GIF_FRAME_DURATION_MS = 360


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


def main() -> None:
    for sheet_path in sorted(SHEETS.glob("*.png")):
        if sheet_path.name.startswith("ai-reference"):
            continue
        slug = sheet_path.stem
        frames = crop_panels(Image.open(sheet_path))
        frames[0].save(ASSETS / f"{slug}.jpg", quality=94, optimize=True)
        sequence = frames + frames[-2:0:-1]
        sequence[0].save(
            ASSETS / f"{slug}.gif",
            save_all=True,
            append_images=sequence[1:],
            duration=GIF_FRAME_DURATION_MS,
            loop=0,
            optimize=True,
            disposal=2,
        )


if __name__ == "__main__":
    main()
