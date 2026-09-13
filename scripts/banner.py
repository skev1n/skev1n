#!/usr/bin/env python3
"""Regenerate assets/banner.svg and assets/banner-static.svg.

The constants below are copied from the skev.in source so this repo stands on
its own: MASTHEAD_ART and MASTHEAD_SIZING from src/masthead.ts, the ribbon and
the colours from src/styles.css. Run it from anywhere:

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
MAST_W = 14.619  # art width in em, the divisor the site sizes the mark from
MAST_TRACK = -0.1818  # em, letter-spacing: -100/550 units
MAST_LH = 0.909  # line-height: 500/550 units

# Departure Mono metrics, UPM 550, typo ascender 550, descender -150
FONT_ASCENT = 1.0  # em above baseline
FONT_DESCENT = 150 / 550  # em below baseline

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

BG = "#0b0c15"  # --bg
QUIET = "#81869f"  # --quiet
DRIFT_SECONDS = 8  # rgb-drift, 8s linear infinite

WIDTH = 1600
SIDE = 72
TOP = 72
GAP = 34  # art to the skev.in line
LABEL_SIZE = 22
BOTTOM = 40


def data_uri(name: str) -> str:
    raw = (FONTS / name).read_bytes()
    return "data:font/woff2;base64," + base64.b64encode(raw).decode("ascii")


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(animated: bool) -> str:
    size = (WIDTH - 2 * SIDE) / MAST_W
    line_step = MAST_LH * size
    art_h = len(MASTHEAD_ART) * line_step
    # Half leading, exactly as a CSS line box places the first baseline.
    first_baseline = TOP + (MAST_LH - (FONT_ASCENT + FONT_DESCENT)) / 2 * size + FONT_ASCENT * size
    label_baseline = TOP + art_h + GAP + LABEL_SIZE * 0.78
    height = round(TOP + art_h + GAP + LABEL_SIZE + BOTTOM)

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
        f'\n    <text class="art" x="{SIDE}" y="{first_baseline + i * line_step:.3f}"'
        f' xml:space="preserve">{esc(row)}</text>'
        for i, row in enumerate(MASTHEAD_ART)
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label="skev.in">
  <title>skev.in</title>
  <defs>
    <linearGradient id="ribbon" gradientUnits="userSpaceOnUse" spreadMethod="repeat"
      x1="0" y1="{TOP:.3f}" x2="0" y2="{TOP + 3 * art_h:.3f}">{stops}{drift}
    </linearGradient>
    <style>
      @font-face {{
        font-family: "Departure Mono";
        src: url({data_uri("DepartureMono-ascii.woff2")}) format("woff2");
        font-weight: 400;
        font-style: normal;
      }}
      @font-face {{
        font-family: "Commit Mono";
        src: url({data_uri("CommitMono-skevin.woff2")}) format("woff2");
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
      .label {{
        font-family: "Commit Mono", ui-monospace, monospace;
        font-size: {LABEL_SIZE}px;
        fill: {QUIET};
      }}
    </style>
  </defs>
  <rect width="{WIDTH}" height="{height}" fill="{BG}"/>
  <g>{lines}
  </g>
  <text class="label" x="{WIDTH - SIDE}" y="{label_baseline:.3f}" text-anchor="end">skev.in</text>
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
