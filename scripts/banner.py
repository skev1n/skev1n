#!/usr/bin/env python3
"""Regenerate assets/banner.svg and assets/banner-static.svg.

The constants below are copied from the skev.in source so this repo stands on
its own: MASTHEAD_ART and MASTHEAD_SIZING from src/masthead.ts, the ribbon and
the colours from src/styles.css. The output is transparent and cropped to the
mark, because it sits on a GitHub README that is white on one theme and near
black on the other. Run it from anywhere:

    python3 scripts/banner.py
"""

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets"

# src/masthead.ts, figlet Slant, 32 x 5 cells
MASTHEAD_ART = [
    "         __               _",
    "   _____/ /_____ _   __  (_)___",
    "  / ___/ //_/ _ \\ | / / / / __ \\",
    " (__  ) ,< /  __/ |/ / / / / / /",
    "/____/_/|_|\\___/|___(_)_/_/ /_/",
]

# src/masthead.ts MASTHEAD_SIZING
MAST_TRACK = -0.1818  # em, letter-spacing: -100/550 units
MAST_LH = 0.909  # line-height: 500/550 units

# Ink box of the five rows, in em, measured by rasterising the art at a known
# size and taking the alpha bounds. Origin is the start of the first line and
# its baseline, so INK_TOP is negative (underscores sit just above it).
INK_LEFT = 0.09
INK_RIGHT = 14.64
INK_TOP = -0.09
INK_BOTTOM = 3.73

MARGIN = 0.15  # em of quiet space on all four sides

# src/styles.css .ascii, the seven stop chroma ribbon, top to bottom
RIBBON = [
    (0, "#ef6b6b"),  # coral
    (17, "#efbf5a"),  # amber
    (34, "#7fcf8a"),  # leaf
    (50, "#62c4d6"),  # teal
    (67, "#7c93f2"),  # periwinkle, the stop --accent is taken from
    (84, "#be85e6"),  # lilac
    (100, "#ef6b6b"),  # coral, closes the loop
]

DRIFT_SECONDS = 8  # rgb-drift, 8s linear infinite

WIDTH = 1600  # intrinsic width; the README scales it to the column


def data_uri(name: str) -> str:
    raw = (FONTS / name).read_bytes()
    return "data:font/woff2;base64," + base64.b64encode(raw).decode("ascii")


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(animated: bool) -> str:
    ink_w = INK_RIGHT - INK_LEFT
    ink_h = INK_BOTTOM - INK_TOP
    size = WIDTH / (ink_w + 2 * MARGIN)
    height = round((ink_h + 2 * MARGIN) * size)

    # Place the ink box at MARGIN from the top left corner.
    origin_x = (MARGIN - INK_LEFT) * size
    first_baseline = (MARGIN - INK_TOP) * size
    art_top = MARGIN * size
    art_h = ink_h * size
    line_step = MAST_LH * size

    # background-size: 100% 300%, so the ribbon is three art-heights tall and
    # drifts one full image height over 8s. Both ends are coral, so repeating
    # the gradient makes the loop seamless.
    stops = "".join(
        f'\n      <stop offset="{pos}%" stop-color="{color}"/>' for pos, color in RIBBON
    )
    drift = (
        ""
        if not animated
        else (
            f'\n      <animateTransform attributeName="gradientTransform" type="translate"'
            f'\n        from="0 0" to="0 {-3 * art_h:.3f}" dur="{DRIFT_SECONDS}s"'
            f'\n        repeatCount="indefinite" additive="sum"/>'
        )
    )

    lines = "".join(
        f'\n    <text class="art" x="{origin_x:.3f}" y="{first_baseline + i * line_step:.3f}"'
        f' xml:space="preserve">{esc(row)}</text>'
        for i, row in enumerate(MASTHEAD_ART)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label="skev.in">
  <title>skev.in</title>
  <defs>
    <linearGradient id="ribbon" gradientUnits="userSpaceOnUse" spreadMethod="repeat"
      x1="0" y1="{art_top:.3f}" x2="0" y2="{art_top + 3 * art_h:.3f}">{stops}{drift}
    </linearGradient>
    <style>
      @font-face {{
        font-family: "Departure Mono";
        src: url({data_uri("DepartureMono-ascii.woff2")}) format("woff2");
        font-weight: 400;
        font-style: normal;
      }}
      .art {{
        font-family: "Departure Mono", ui-monospace, monospace;
        font-size: {size:.3f}px;
        letter-spacing: {MAST_TRACK * size:.3f}px;
        fill: url(#ribbon);
        white-space: pre;
        text-rendering: geometricPrecision;
      }}
    </style>
  </defs>
  <g>{lines}
  </g>
</svg>
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, animated in (("banner.svg", True), ("banner-static.svg", False)):
        path = OUT / name
        path.write_text(build(animated), encoding="utf-8")
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
