"""Render the issue-driven poll card (assets/poll-{dark,light}.svg) from data/poll.json."""
import json, os
from collections import Counter
from theme import THEMES, MUTED, RULE, RADIUS, esc, svg_open

ROOT = os.path.join(os.path.dirname(__file__), "..")
W = 985


def render(mode, cfg, poll):
    t = THEMES[mode]
    opts = cfg["poll"]["options"]
    tally = Counter(poll["votes"].values())
    total = sum(tally.values())
    top = max(tally.values() or [0])
    H = 70 + 40 * len(opts) + 34
    out = [svg_open(W, H, t, f"Poll: {cfg['poll']['question']} {total} votes")]
    out.append(f'<text x="24" y="38" font-size="15" font-weight="700" fill="{t["ink"]}"><tspan fill="{t["accent"]}">?</tspan> {esc(cfg["poll"]["question"])}</text>\n')
    out.append(f'<text x="{W-24}" y="38" text-anchor="end" font-size="12" fill="{t["ink"]}" fill-opacity="{MUTED}">{total} vote{"s" if total != 1 else ""} · one per GitHub account</text>\n')
    bx, bw = 470, W - 470 - 90
    for i, (k, label) in enumerate(opts.items()):
        y = 70 + i * 40
        n = tally.get(k, 0)
        share = n / total if total else 0
        lead = n and n == top
        out.append(f'<text x="24" y="{y+17}" font-size="13" fill="{t["ink"]}"><tspan font-weight="700" fill="{t["accent"]}">[{k}]</tspan> {esc(label)}</text>\n')
        out.append(f'<rect x="{bx}" y="{y+5}" width="{bw}" height="16" rx="{RADIUS}" fill="{t["ink"]}" fill-opacity="{RULE*.7}"/>\n')
        if n:
            out.append(f'<rect x="{bx}" y="{y+5}" width="{max(bw*share, 12):.0f}" height="16" rx="{RADIUS}" fill="{t["accent"]}" fill-opacity="{1 if lead else .45}"/>\n')
        out.append(f'<text x="{W-24}" y="{y+17}" text-anchor="end" font-size="13" fill="{t["ink"]}">{share*100:.0f}%</text>\n')
    out.append(f'<text x="24" y="{H-18}" font-size="11" fill="{t["ink"]}" fill-opacity="{MUTED}">vote with the links below · an Action counts it, redraws this card and closes your issue · last vote {esc(poll.get("updated_at") or "none yet")}</text>\n')
    out.append("</svg>\n")
    return "".join(out)


if __name__ == "__main__":
    cfg = json.load(open(os.path.join(ROOT, "config", "profile.json"), encoding="utf-8"))
    poll = json.load(open(os.path.join(ROOT, "data", "poll.json"), encoding="utf-8"))
    for mode in THEMES:
        open(os.path.join(ROOT, "assets", f"poll-{mode}.svg"), "w", encoding="utf-8").write(render(mode, cfg, poll))
    print("poll rendered")
