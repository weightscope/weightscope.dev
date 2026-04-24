"""Generate weightscope assets from transparent-background source PNGs.

Source files (in the user's OneDrive):
  - horizontal logo - transparent background.png  (mark + "Weightscope" wordmark)
  - round logo - transparent background.png       (circular medallion)

Outputs to ../assets/:
  - weightscope_logo_horizontal.png                (full lockup, transparent)
  - weightscope_mark.png                           (mark-only, transparent)
  - weightscope_icon_{512,192,32}.png              (rounded-square on black)
  - weightscope_appicon_{512,192,32}.png           (squircle on black)
  - weightscope_icon_circle_{512,192,32}.png       (medallion, transparent)
  - favicon.ico                                    (16/32/48/64, from medallion)
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
SRC = Path(r"C:/Users/gcox0/OneDrive/Apps/Weightscope/horizontal logo - transparent background.png")
FAVICON_SRC = Path(r"C:/Users/gcox0/OneDrive/Apps/Weightscope/round logo - transparent background.png")

ASSETS.mkdir(exist_ok=True)


def save_png(im: Image.Image, path: Path) -> None:
    im.save(path, format="PNG", optimize=True)


def alpha_bbox(im: Image.Image) -> tuple[int, int, int, int] | None:
    """Bounding box of visible (non-transparent) pixels."""
    return im.split()[-1].point(lambda p: 255 if p > 3 else 0).getbbox()


def tight_crop(im: Image.Image, pad_frac: float = 0.0) -> Image.Image:
    bb = alpha_bbox(im)
    if bb is None:
        return im
    x0, y0, x1, y1 = bb
    px = int((x1 - x0) * pad_frac)
    py = int((y1 - y0) * pad_frac)
    W, H = im.size
    return im.crop((max(0, x0 - px), max(0, y0 - py), min(W, x1 + px), min(H, y1 + py)))


def square_canvas(im: Image.Image) -> Image.Image:
    """Place image on a transparent square canvas (side = max dim), centered."""
    w, h = im.size
    side = max(w, h)
    out = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    out.paste(im, ((side - w) // 2, (side - h) // 2), im)
    return out


def rounded_mask(size: int, radius: int) -> Image.Image:
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=255)
    return m


def compose_on_black(mark: Image.Image, size: int, shape: str, inset_frac: float = 0.04) -> Image.Image:
    """Place mark on a solid-black rounded shape (icon/appicon use case)."""
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    fit = int(size * (1 - 2 * inset_frac))
    m = mark.copy()
    m.thumbnail((fit, fit), Image.LANCZOS)
    bg.alpha_composite(m, ((size - m.width) // 2, (size - m.height) // 2))
    if shape == "square":
        mask = rounded_mask(size, radius=int(size * 0.18))
    elif shape == "squircle":
        mask = rounded_mask(size, radius=int(size * 0.225))
    else:
        raise ValueError(shape)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)
    return out


def extract_mark_from_horizontal(horiz: Image.Image) -> Image.Image:
    """Crop just the mark (left of the wordmark) using the alpha channel.
    Scans the left ~40% of the image."""
    w, h = horiz.size
    left = horiz.crop((0, 0, int(w * 0.42), h))
    mark = tight_crop(left)
    return square_canvas(mark)


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Missing source: {SRC}")
    if not FAVICON_SRC.exists():
        raise SystemExit(f"Missing source: {FAVICON_SRC}")

    # ---- horizontal lockup ----
    horiz = Image.open(SRC).convert("RGBA")
    horiz = tight_crop(horiz, pad_frac=0.02)
    save_png(horiz, ASSETS / "weightscope_logo_horizontal.png")

    # ---- mark only ----
    mark = extract_mark_from_horizontal(Image.open(SRC).convert("RGBA"))
    save_png(mark, ASSETS / "weightscope_mark.png")

    # ---- medallion (round icon source) ----
    medallion = Image.open(FAVICON_SRC).convert("RGBA")
    medallion = square_canvas(tight_crop(medallion))

    # ---- icon variants ----
    for sz in (512, 192, 32):
        inset = 0.04 if sz >= 192 else 0.02
        save_png(compose_on_black(mark, sz, "square", inset), ASSETS / f"weightscope_icon_{sz}.png")
        save_png(compose_on_black(mark, sz, "squircle", inset), ASSETS / f"weightscope_appicon_{sz}.png")
        circle_im = medallion.resize((sz, sz), Image.LANCZOS)
        save_png(circle_im, ASSETS / f"weightscope_icon_circle_{sz}.png")

    # ---- favicon ----
    base = medallion.resize((256, 256), Image.LANCZOS)
    base.save(
        ASSETS / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
    )

    print(f"Done. Wrote {len(list(ASSETS.iterdir()))} files to {ASSETS}")


if __name__ == "__main__":
    main()
