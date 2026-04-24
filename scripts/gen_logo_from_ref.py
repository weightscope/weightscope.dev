"""Generate weightscope assets from the provided reference PNG.

Takes the full horizontal logo (mark + wordmark) and produces:
  - weightscope_logo_horizontal.{png}
  - weightscope_icon_{512,192,32}.png           (square, rounded corners, mark cropped)
  - weightscope_icon_circle_{512,192,32}.png   (circle mask, mark cropped)
  - weightscope_appicon_{512,192,32}.png       (squircle, mark cropped)
  - favicon.ico                                 (16/32/48)

The old handmade SVGs are left in place for reference but not shipped.
"""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
SRC = Path(r"C:/Users/gcox0/.claude/image-cache/3f586108-ef67-42b4-a478-798a418f5a21/4.png")
FAVICON_SRC = Path(r"C:/Users/gcox0/.claude/image-cache/3f586108-ef67-42b4-a478-798a418f5a21/5.png")

ASSETS.mkdir(exist_ok=True)


def save_png(im: Image.Image, path: Path) -> None:
    im.save(path, format="PNG", optimize=True)


def find_mark_bbox(im: Image.Image) -> tuple[int, int, int, int]:
    """Find the square bounding box of just the mark (sphere + wings + rays),
    excluding the wordmark. We scan the left half of the image for bright
    (non-black) pixels and square up the bbox."""
    gray = im.convert("L")
    w, h = gray.size
    # Only look at the left ~45% so the wordmark is excluded
    crop = gray.crop((0, 0, int(w * 0.45), h))
    bbox = crop.point(lambda p: 255 if p > 30 else 0).getbbox()
    if bbox is None:
        raise RuntimeError("Could not detect mark in reference image")
    x0, y0, x1, y1 = bbox
    # Square it up, centered on the bbox, with a little breathing room
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    half = max(x1 - x0, y1 - y0) / 2
    pad = half * 0.08
    half += pad
    return (
        int(max(0, cx - half)),
        int(max(0, cy - half)),
        int(min(w, cx + half)),
        int(min(h, cy + half)),
    )


def rounded_mask(size: int, radius: int) -> Image.Image:
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    return m


def circle_mask(size: int) -> Image.Image:
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.ellipse((0, 0, size - 1, size - 1), fill=255)
    return m


def tile_background(size: int) -> Image.Image:
    """Solid black background matching the reference."""
    return Image.new("RGB", (size, size), (0, 0, 0))


def compose_icon(
    mark: Image.Image,
    size: int,
    shape: str,
    inset_frac: float = 0.14,
) -> Image.Image:
    """Place the mark onto a dark background with the requested shape mask."""
    bg = tile_background(size).convert("RGBA")
    # Resize mark so it fits within (1 - 2*inset) of the canvas
    fit = int(size * (1 - 2 * inset_frac))
    m = mark.copy()
    m.thumbnail((fit, fit), Image.LANCZOS)
    # Center the mark
    mx = (size - m.width) // 2
    my = (size - m.height) // 2
    bg.alpha_composite(m, (mx, my))
    # Shape mask
    if shape == "square":
        mask = rounded_mask(size, radius=int(size * 0.18))
    elif shape == "squircle":
        mask = rounded_mask(size, radius=int(size * 0.225))
    elif shape == "circle":
        mask = circle_mask(size)
    else:
        raise ValueError(shape)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)
    return out


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Source not found: {SRC}")

    full = Image.open(SRC).convert("RGBA")

    # 1. Horizontal lockup — save verbatim (also trim tight vertical bbox for compactness)
    gray = full.convert("L")
    nb = gray.point(lambda p: 255 if p > 30 else 0).getbbox()
    if nb:
        # Add margin
        x0, y0, x1, y1 = nb
        pad_x = int((x1 - x0) * 0.02)
        pad_y = int((y1 - y0) * 0.08)
        W, H = full.size
        horizontal = full.crop(
            (
                max(0, x0 - pad_x),
                max(0, y0 - pad_y),
                min(W, x1 + pad_x),
                min(H, y1 + pad_y),
            )
        )
    else:
        horizontal = full
    save_png(horizontal, ASSETS / "weightscope_logo_horizontal.png")

    # 1b. Transparent-background version of the horizontal lockup for use on
    # already-dark pages. Uses luminance as alpha so only the bright chrome
    # pixels are visible; any pure black bleeds away.
    hgray = horizontal.convert("L")
    alpha = hgray.point(lambda p: 0 if p < 6 else min(255, p + 40))
    transparent = Image.new("RGBA", horizontal.size, (0, 0, 0, 0))
    transparent.paste(horizontal.convert("RGB"), (0, 0))
    transparent.putalpha(alpha)
    save_png(transparent, ASSETS / "weightscope_logo_horizontal_transparent.png")

    # 2. Mark-only square crop for icons
    bx = find_mark_bbox(full)
    mark = full.crop(bx)
    # Ensure truly square (it already should be roughly)
    m_w, m_h = mark.size
    side = max(m_w, m_h)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(mark, ((side - m_w) // 2, (side - m_h) // 2))
    mark = canvas

    # 3. Favicon & circle/appicon source: use the round medallion directly.
    #    The medallion already has a silver rim + black disc, so we just resize it.
    medallion = Image.open(FAVICON_SRC).convert("RGBA")
    # Trim to tight square bbox
    mgray = medallion.convert("L")
    mbb = mgray.point(lambda p: 255 if p > 10 else 0).getbbox()
    if mbb:
        medallion = medallion.crop(mbb)
    mw, mh = medallion.size
    mside = max(mw, mh)
    mcanvas = Image.new("RGBA", (mside, mside), (0, 0, 0, 0))
    mcanvas.paste(medallion, ((mside - mw) // 2, (mside - mh) // 2))
    medallion = mcanvas

    # 4. Icon variants
    for sz in (512, 192, 32):
        # Square icon: mark on solid black with rounded-square crop
        inset = 0.04 if sz >= 192 else 0.02
        im = compose_icon(mark, sz, "square", inset_frac=inset)
        save_png(im, ASSETS / f"weightscope_icon_{sz}.png")

        # App icon (squircle): same mark-on-black composition
        im = compose_icon(mark, sz, "squircle", inset_frac=inset)
        save_png(im, ASSETS / f"weightscope_appicon_{sz}.png")

        # Circle icon: use the medallion artwork directly
        circle_im = medallion.resize((sz, sz), Image.LANCZOS)
        save_png(circle_im, ASSETS / f"weightscope_icon_circle_{sz}.png")

    # 5. Favicon (16/32/48/64) — from the medallion.
    # Pillow ICO save auto-downsizes the source to all specified sizes, so feed
    # it a high-res image and let it generate each entry.
    base = medallion.resize((256, 256), Image.LANCZOS)
    base.save(
        ASSETS / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
    )

    print(f"Done. Wrote {len(list(ASSETS.iterdir()))} files to {ASSETS}")


if __name__ == "__main__":
    main()
