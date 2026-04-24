"""Generate weightscope logo assets (SVG + PNG) and favicon.ico.

Outputs to ../assets/:
  weightscope_logo_horizontal.{svg,png}
  weightscope_icon_{512,192,32}.{svg,png}
  weightscope_icon_circle_{512,192,32}.{svg,png}
  weightscope_appicon_{512,192,32}.{svg,png}
  favicon.ico
"""
from __future__ import annotations

import io
from pathlib import Path

import resvg_py
from PIL import Image

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
ASSETS.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Gradient + style defs shared by every variant
# ---------------------------------------------------------------------------
DEFS = """
<defs>
  <radialGradient id="sphere" cx="38%" cy="34%" r="70%">
    <stop offset="0%"  stop-color="#ffffff"/>
    <stop offset="22%" stop-color="#e8ecf0"/>
    <stop offset="55%" stop-color="#8a9099"/>
    <stop offset="85%" stop-color="#2b2f36"/>
    <stop offset="100%" stop-color="#0d0f12"/>
  </radialGradient>

  <linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"  stop-color="#f4f6f8"/>
    <stop offset="35%" stop-color="#c6ccd3"/>
    <stop offset="50%" stop-color="#7f858c"/>
    <stop offset="65%" stop-color="#c6ccd3"/>
    <stop offset="100%" stop-color="#3a3e44"/>
  </linearGradient>

  <linearGradient id="chromeH" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%"  stop-color="#6a6f76"/>
    <stop offset="50%" stop-color="#eaedf0"/>
    <stop offset="100%" stop-color="#6a6f76"/>
  </linearGradient>

  <radialGradient id="bgDark" cx="50%" cy="40%" r="80%">
    <stop offset="0%"  stop-color="#1a1d22"/>
    <stop offset="100%" stop-color="#08090b"/>
  </radialGradient>
</defs>
"""


def build_mark(cx: float, cy: float, scale: float = 1.0, with_rays: bool = True) -> str:
    """Render the mark (sphere + wings + rays) centered on (cx, cy).

    Base dimensions chosen so the mark fills a 420x320 box at scale=1.
    """
    s = scale
    # Sphere
    sphere_r = 52 * s
    # Wing bars: 3 per side.
    bar_h = 13 * s
    bar_gap = 9 * s  # vertical gap between adjacent bars
    # Distances from sphere center for bar inner/outer edges
    inner = 62 * s
    outer = 220 * s

    # Left wing bars — top & bottom slightly shorter than middle
    lw_top    = (cx - outer + 16 * s, cy - bar_h - bar_gap / 2, outer - inner - 16 * s, bar_h)
    lw_mid    = (cx - outer,          cy - bar_h / 2,            outer - inner,          bar_h)
    lw_bot    = (cx - outer + 16 * s, cy + bar_gap / 2,          outer - inner - 16 * s, bar_h)
    rw_top    = (cx + inner + 0 * s,  cy - bar_h - bar_gap / 2, outer - inner - 16 * s, bar_h)
    rw_mid    = (cx + inner,          cy - bar_h / 2,            outer - inner,          bar_h)
    rw_bot    = (cx + inner + 0 * s,  cy + bar_gap / 2,          outer - inner - 16 * s, bar_h)

    def bar(xywh):
        x, y, w, h = xywh
        return (
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'rx="{h/2:.2f}" ry="{h/2:.2f}" fill="url(#chrome)" '
            f'stroke="#1a1c20" stroke-width="{0.8*s:.2f}"/>'
        )

    bars = "".join(bar(b) for b in (lw_top, lw_mid, lw_bot, rw_top, rw_mid, rw_bot))

    # Rays (top + bottom). Zia-style: taller center, shorter sides.
    rays_svg = ""
    if with_rays:
        ray_heights = [40, 52, 62, 52, 40]
        ray_offsets = [-46, -23, 0, 23, 46]
        ray_w = 7 * s
        ray_gap = 18 * s  # gap between sphere and start of ray
        for dx, h in zip(ray_offsets, ray_heights):
            h = h * s
            x = cx + dx * s - ray_w / 2
            # top
            y_top = cy - sphere_r - ray_gap - h
            rays_svg += (
                f'<rect x="{x:.2f}" y="{y_top:.2f}" width="{ray_w:.2f}" height="{h:.2f}" '
                f'rx="{ray_w/2:.2f}" fill="url(#chrome)"/>'
            )
            # bottom
            y_bot = cy + sphere_r + ray_gap
            rays_svg += (
                f'<rect x="{x:.2f}" y="{y_bot:.2f}" width="{ray_w:.2f}" height="{h:.2f}" '
                f'rx="{ray_w/2:.2f}" fill="url(#chrome)"/>'
            )

    # Sphere + glossy highlight
    sphere_svg = (
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{sphere_r:.2f}" fill="url(#sphere)" '
        f'stroke="#0a0b0d" stroke-width="{1.2*s:.2f}"/>'
        # specular highlight
        f'<ellipse cx="{cx - sphere_r*0.35:.2f}" cy="{cy - sphere_r*0.42:.2f}" '
        f'rx="{sphere_r*0.28:.2f}" ry="{sphere_r*0.18:.2f}" fill="#ffffff" opacity="0.75"/>'
        # subtle rim shadow at bottom
        f'<ellipse cx="{cx + sphere_r*0.18:.2f}" cy="{cy + sphere_r*0.62:.2f}" '
        f'rx="{sphere_r*0.55:.2f}" ry="{sphere_r*0.14:.2f}" fill="#000000" opacity="0.35"/>'
    )

    return rays_svg + bars + sphere_svg


def build_mark_compact(cx: float, cy: float, size: int) -> str:
    """Simplified mark for small canvases (<= 64px): big sphere + one bar each side."""
    sphere_r = size * 0.22
    bar_h = max(2.0, size * 0.10)
    bar_w = size * 0.28
    bar_y = cy - bar_h / 2
    gap = size * 0.04
    lw = f'<rect x="{cx - sphere_r - gap - bar_w:.2f}" y="{bar_y:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" rx="{bar_h/2:.2f}" fill="url(#chrome)"/>'
    rw = f'<rect x="{cx + sphere_r + gap:.2f}" y="{bar_y:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" rx="{bar_h/2:.2f}" fill="url(#chrome)"/>'
    sphere = (
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{sphere_r:.2f}" fill="url(#sphere)"/>'
        f'<ellipse cx="{cx - sphere_r*0.35:.2f}" cy="{cy - sphere_r*0.40:.2f}" '
        f'rx="{sphere_r*0.30:.2f}" ry="{sphere_r*0.20:.2f}" fill="#ffffff" opacity="0.8"/>'
    )
    return lw + rw + sphere


def bg_rect(w: int, h: int, r: float) -> str:
    return (
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="{r}" ry="{r}" fill="url(#bgDark)"/>'
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{r}" ry="{r}" '
        f'fill="none" stroke="#ffffff" stroke-opacity="0.08" stroke-width="1"/>'
    )


def bg_circle(size: int) -> str:
    cx = cy = size / 2
    r = size / 2
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#bgDark)"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r-0.5}" fill="none" '
        f'stroke="#ffffff" stroke-opacity="0.08" stroke-width="1"/>'
    )


def _mark_for(size: int, cx: float, cy: float) -> str:
    if size <= 64:
        return build_mark_compact(cx, cy, size)
    return build_mark(cx, cy, scale=size / 512.0, with_rays=True)


def make_icon_square(size: int, radius_frac: float = 0.18) -> str:
    """Square icon with rounded corners."""
    r = size * radius_frac
    cx = cy = size / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">'
        + DEFS
        + bg_rect(size, size, r)
        + _mark_for(size, cx, cy)
        + "</svg>"
    )


def make_icon_circle(size: int) -> str:
    cx = cy = size / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">'
        + DEFS
        + bg_circle(size)
        + _mark_for(size, cx, cy)
        + "</svg>"
    )


def make_appicon(size: int) -> str:
    """iOS-style squircle: higher corner radius."""
    return make_icon_square(size, radius_frac=0.225)


def make_horizontal(width: int = 1400, height: int = 320) -> str:
    """Horizontal lockup: mark on left, wordmark on right, transparent bg."""
    mark_cx = 210
    mark_cy = height / 2
    mark_scale = 0.62
    text_x = 440
    text_y = height / 2 + 48   # baseline offset so caps sit centered
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
{DEFS}
{build_mark(mark_cx, mark_cy, scale=mark_scale, with_rays=True)}
<text x="{text_x}" y="{text_y}" font-family="system-ui, -apple-system, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
      font-size="150" font-weight="300" letter-spacing="-1"
      fill="url(#chromeH)" stroke="#0a0b0d" stroke-width="1.1">Weightscope</text>
</svg>'''


# ---------------------------------------------------------------------------
# Render pipeline
# ---------------------------------------------------------------------------
def write_svg(path: Path, svg: str) -> None:
    path.write_text(svg, encoding="utf-8")


def rasterize(svg: str, width: int, height: int) -> bytes:
    """Render SVG string to PNG bytes at the given size."""
    return bytes(resvg_py.svg_to_bytes(svg_string=svg, width=width, height=height))


def write_png(path: Path, svg: str, w: int, h: int) -> None:
    path.write_bytes(rasterize(svg, w, h))


def build_favicon(out: Path) -> None:
    """Multi-res ICO from the rounded-square icon at 16/32/48."""
    imgs = []
    for size in (16, 32, 48):
        svg = make_icon_square(size, radius_frac=0.22)
        png_bytes = rasterize(svg, size, size)
        imgs.append(Image.open(io.BytesIO(png_bytes)).convert("RGBA"))
    imgs[0].save(out, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)], append_images=imgs[1:])


def main() -> None:
    # Horizontal lockup
    horiz = make_horizontal()
    write_svg(ASSETS / "weightscope_logo_horizontal.svg", horiz)
    write_png(ASSETS / "weightscope_logo_horizontal.png", horiz, 1200, 320)

    sizes = [512, 192, 32]
    for sz in sizes:
        svg = make_icon_square(sz)
        write_svg(ASSETS / f"weightscope_icon_{sz}.svg", svg)
        write_png(ASSETS / f"weightscope_icon_{sz}.png", svg, sz, sz)

        svg = make_icon_circle(sz)
        write_svg(ASSETS / f"weightscope_icon_circle_{sz}.svg", svg)
        write_png(ASSETS / f"weightscope_icon_circle_{sz}.png", svg, sz, sz)

        svg = make_appicon(sz)
        write_svg(ASSETS / f"weightscope_appicon_{sz}.svg", svg)
        write_png(ASSETS / f"weightscope_appicon_{sz}.png", svg, sz, sz)

    # Favicon
    build_favicon(ASSETS / "favicon.ico")
    print(f"Wrote {len(list(ASSETS.iterdir()))} files to {ASSETS}")


if __name__ == "__main__":
    main()
