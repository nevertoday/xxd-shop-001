#!/usr/bin/env python3
"""Erase small stray marks (an extra ® or ™ beside a brand name) from a finished PNG.

The image model sometimes adds a tiny ® that no input had. Regenerating the whole
canvas for one symbol wastes a render and can break what was right, so the mark is
painted out locally instead: the box is refilled from the pixels just outside it,
with matching grain. No model is called and nothing outside the box changes.

  look  PNG --box x,y,w,h [--out crop.png]   enlarged crop with a coordinate grid, to find
                                             and check the mark (written to a temp file)
  erase PNG --box x,y,w,h [--box ...]        refill each box in place; the untouched file is
                                             kept in a temp folder and its path printed

Boxes are in the PNG's own pixels. Only small boxes are accepted (this is for a symbol,
not for repairing a picture); anything larger should be regenerated instead.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
import tempfile
from pathlib import Path

MAX_SIDE = 160          # px; a stray ® is rarely over ~60 px even on a 2048 canvas
MAX_AREA_SHARE = 0.004  # of the whole image
RING = 3                # px sampled outside each edge
OUTLIER = 16            # mean per-channel distance from the ring's median that marks a run as a stroke, not background
GRID = 10               # px between grid lines in `look`
TEMP = Path(tempfile.gettempdir()) / "xxd-shop-clean-marks"


def emit(payload: dict, *, error: bool = False) -> None:
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), file=sys.stderr if error else sys.stdout)


def parse_box(text: str) -> tuple[int, int, int, int]:
    try:
        x, y, w, h = (int(round(float(v))) for v in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError("box must be x,y,w,h") from None
    if w <= 0 or h <= 0:
        raise argparse.ArgumentTypeError("box width and height must be positive")
    return x, y, w, h


def load(path: Path):
    from PIL import Image
    if path.suffix.lower() != ".png" or not path.is_file():
        emit({"ok": False, "reason": "png_not_found", "path": str(path)}, error=True)
        raise SystemExit(2)
    image = Image.open(path)
    image.load()
    return image


def check_box(box, size, *, limit: bool) -> str | None:
    x, y, w, h = box
    if x < 0 or y < 0 or x + w > size[0] or y + h > size[1]:
        return "box_outside_image"
    if limit:
        if x < RING or y < RING or x + w > size[0] - RING or y + h > size[1] - RING:
            return "box_touches_edge"
        if w > MAX_SIDE or h > MAX_SIDE or w * h > MAX_AREA_SHARE * size[0] * size[1]:
            return "box_too_large_regenerate_instead"
    return None


def cmd_look(args) -> int:
    from PIL import Image, ImageDraw
    image = load(args.png).convert("RGB")
    x, y, w, h = args.box
    pad = max(max(w, h) // 2, 16)
    left, top = max(0, x - pad), max(0, y - pad)
    right, bottom = min(image.width, x + w + pad), min(image.height, y + h + pad)
    if right <= left or bottom <= top:
        emit({"ok": False, "reason": "box_outside_image"}, error=True)
        return 2
    zoom = max(1, min(12, 900 // max(right - left, bottom - top)))
    crop = image.crop((left, top, right, bottom)).resize(((right - left) * zoom, (bottom - top) * zoom), Image.Resampling.NEAREST)
    draw = ImageDraw.Draw(crop)
    for gx in range((left // GRID + 1) * GRID, right, GRID):
        major = gx % (GRID * 5) == 0
        draw.line([((gx - left) * zoom, 0), ((gx - left) * zoom, crop.height)], fill=(0, 160, 255) if major else (150, 210, 255))
        if major:
            draw.text(((gx - left) * zoom + 2, 2), str(gx), fill=(0, 90, 200))
    for gy in range((top // GRID + 1) * GRID, bottom, GRID):
        major = gy % (GRID * 5) == 0
        draw.line([(0, (gy - top) * zoom), (crop.width, (gy - top) * zoom)], fill=(0, 160, 255) if major else (150, 210, 255))
        if major:
            draw.text((2, (gy - top) * zoom + 2), str(gy), fill=(0, 90, 200))
    draw.rectangle([(x - left) * zoom, (y - top) * zoom, (x + w - left) * zoom - 1, (y + h - top) * zoom - 1], outline=(255, 0, 80))
    out = args.out or TEMP / f"look-{args.png.stem}-{x}-{y}-{w}-{h}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    crop.save(out)
    emit({"ok": True, "look": str(out.resolve()), "shown": [left, top, right - left, bottom - top], "zoom": zoom,
          "grid_px": GRID, "box": list(args.box)})
    return 0


def median(values: list[float]) -> float:
    values = sorted(values)
    mid = len(values) // 2
    return values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2


def runs(px, coords, bands: int, ref: tuple[float, ...]) -> list[tuple[float, ...]]:
    """Mean colour of each run of ring pixels (one run per row or column of the box).

    A run that is far from the ring's typical colour (a letter stroke or outline that
    reaches into the ring) is replaced by the nearest clean run on the same side, so
    the stroke does not bleed into the fill.
    """
    means = []
    for run in coords:
        vals = [px[c] for c in run]
        means.append(tuple(sum(v[k] for v in vals) / len(vals) for k in range(bands)))
    clean = [sum(abs(m[k] - ref[k]) for k in range(bands)) / bands <= OUTLIER for m in means]
    if not any(clean):
        return [ref] * len(means)
    out = []
    for i in range(len(means)):
        if clean[i]:
            out.append(means[i])
            continue
        near = min((j for j in range(len(means)) if clean[j]), key=lambda j: abs(j - i))
        out.append(means[near])
    return out


def grain(px, ring: list[tuple[int, int]], bands: int) -> list[float]:
    """Pixel-to-pixel noise along the ring, so the fill is not flatter than its surroundings.

    Uses the median absolute deviation of neighbour differences, so an edge crossing the
    ring does not read as noise.
    """
    sigma = []
    for k in range(bands):
        d = [px[a][k] - px[b][k] for a, b in zip(ring, ring[1:]) if abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1]
        if not d:
            sigma.append(0.0)
            continue
        m = median(d)
        sigma.append(min(6.0, 1.4826 * median([abs(v - m) for v in d]) / 2 ** 0.5))
    return sigma


def fill(image, box) -> None:
    """Coons-patch fill from the ring around the box, plus matched grain."""
    x, y, w, h = box
    px = image.load()
    bands = len(image.getbands())
    if bands == 1:
        get = px.__getitem__
        px = type("Grey", (), {"__getitem__": lambda _s, c: (get(c),)})()
    span = range(1, RING + 1)
    ring = [(x - 1 + i, y - 1) for i in range(w + 2)] + [(x + w, y + j) for j in range(h)] + \
           [(x + w - i, y + h) for i in range(w + 2)] + [(x - 1, y + h - 1 - j) for j in range(h)]
    ref = tuple(median([px[c][k] for c in ring]) for k in range(bands))
    top = runs(px, [[(x + i, y - d) for d in span] for i in range(w)], bands, ref)
    bottom = runs(px, [[(x + i, y + h - 1 + d) for d in span] for i in range(w)], bands, ref)
    left = runs(px, [[(x - d, y + j) for d in span] for j in range(h)], bands, ref)
    right = runs(px, [[(x + w - 1 + d, y + j) for d in span] for j in range(h)], bands, ref)
    corner = lambda cx, cy, sx, sy: runs(px, [[(cx + sx * d, cy + sy * e) for d in range(RING) for e in range(RING)]], bands, ref)[0]
    tl, tr = corner(x - 1, y - 1, -1, -1), corner(x + w, y - 1, 1, -1)
    bl, br = corner(x - 1, y + h, -1, 1), corner(x + w, y + h, 1, 1)
    sigma = grain(px, ring, bands)
    rng = random.Random(f"{x},{y},{w},{h}")
    out = image.load()
    for j in range(h):
        v = (j + 1) / (h + 1)
        for i in range(w):
            u = (i + 1) / (w + 1)
            value = []
            for k in range(bands):
                c = ((1 - v) * top[i][k] + v * bottom[i][k] + (1 - u) * left[j][k] + u * right[j][k]
                     - ((1 - u) * (1 - v) * tl[k] + u * (1 - v) * tr[k] + (1 - u) * v * bl[k] + u * v * br[k]))
                if sigma[k] and not (bands == 4 and k == 3):
                    c += rng.gauss(0, sigma[k])
                value.append(max(0, min(255, round(c))))
            out[x + i, y + j] = tuple(value) if bands > 1 else value[0]


def cmd_erase(args) -> int:
    image = load(args.png)
    if image.mode not in {"RGB", "RGBA", "L"}:
        image = image.convert("RGB")
    for box in args.box:
        problem = check_box(box, image.size, limit=True)
        if problem:
            emit({"ok": False, "reason": problem, "box": list(box), "image_size": list(image.size),
                  "max_side": MAX_SIDE}, error=True)
            return 2
    TEMP.mkdir(parents=True, exist_ok=True)
    before = TEMP / f"before-{args.png.stem}.png"
    n = 1
    while before.exists():
        n += 1
        before = TEMP / f"before-{args.png.stem}-{n}.png"
    shutil.copy2(args.png, before)
    for box in args.box:
        fill(image, box)
    extra = {"icc_profile": image.info["icc_profile"]} if image.info.get("icc_profile") else {}
    image.save(args.png, format="PNG", **extra)
    emit({"ok": True, "path": str(args.png.resolve()), "erased": [list(b) for b in args.box], "before": str(before),
          "size": list(image.size)})
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    look = sub.add_parser("look", help="enlarged crop with a pixel grid around a box")
    look.add_argument("png", type=Path)
    look.add_argument("--box", type=parse_box, required=True)
    look.add_argument("--out", type=Path)
    erase = sub.add_parser("erase", help="refill boxes in place from their surroundings")
    erase.add_argument("png", type=Path)
    erase.add_argument("--box", type=parse_box, action="append", required=True)
    args = ap.parse_args()
    try:
        return cmd_look(args) if args.cmd == "look" else cmd_erase(args)
    except ModuleNotFoundError:
        emit({"ok": False, "reason": "pillow_missing", "hint": "run with a Python that has Pillow"}, error=True)
        return 2


if __name__ == "__main__":
    sys.exit(main())
