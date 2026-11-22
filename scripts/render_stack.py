"""Render the stack strip (assets/stack-{dark,light}.svg): three layers, monochrome, no logo soup."""
import json, os
from theme import THEMES, MUTED, RULE, RADIUS, esc, svg_open

ROOT = os.path.join(os.path.dirname(__file__), "..")
W, ROW = 985, 44


def render(mode, layers):
    t = THEMES[mode]
    H = 24 + ROW * len(layers)
    out = [svg_open(W, H, t, "Stack by layer: " + "; ".join(f"{n}: {', '.join(i)}" for n, i in layers))]
    for r, (name, items) in enumerate(layers):
        y = 12 + r * ROW
        if r:
            out.append(f'<line x1="20" x2="{W-20}" y1="{y}" y2="{y}" stroke="{t["ink"]}" stroke-opacity="{RULE}"/>\n')
        cy = y + ROW / 2
        out.append(f'<rect x="20" y="{cy-9}" width="3" height="18" rx="1.5" fill="{t["accent"]}"/>\n')
        out.append(f'<text x="34" y="{cy+4}" font-size="11" font-weight="700" letter-spacing="1.5" fill="{t["ink"]}" fill-opacity="{MUTED}">{esc(name)}</text>\n')
        x = 210
        for it in items:
            w = len(it) * 7.2 + 22
            out.append(f'<rect x="{x}" y="{cy-12}" width="{w:.0f}" height="24" rx="{RADIUS}" fill="none" stroke="{t["ink"]}" stroke-opacity="{RULE*1.6}"/>\n'
                       f'<text x="{x + w/2:.0f}" y="{cy+4}" text-anchor="middle" font-size="12" fill="{t["ink"]}">{esc(it)}</text>\n')
            x += w + 8
    out.append("</svg>\n")
    return "".join(out)


if __name__ == "__main__":
    cfg = json.load(open(os.path.join(ROOT, "config", "profile.json"), encoding="utf-8"))
    for mode in THEMES:
        open(os.path.join(ROOT, "assets", f"stack-{mode}.svg"), "w", encoding="utf-8").write(render(mode, cfg["stack"]))
    print("stack rendered")
