"""Render the neofetch-style hero (assets/hero-{dark,light}.svg) from config + data snapshot."""
import json, os
from datetime import datetime, timezone, date
from theme import THEMES, MUTED, RULE, RADIUS, esc, svg_open

ROOT = os.path.join(os.path.dirname(__file__), "..")
W, H = 985, 466
CH = 7.8          # advance width of a 13px monospace glyph
LH = 18


def uptime(created, now):
    c = datetime.fromisoformat(created.replace("Z", "+00:00")).date()
    y, m, d = now.year - c.year, now.month - c.month, now.day - c.day
    if d < 0:
        m -= 1
        d += 30
    if m < 0:
        y -= 1
        m += 12
    p = lambda n, u: f"{n} {u}{'' if n == 1 else 's'}"
    return f"{p(y, 'year')}, {p(m, 'month')}, {p(d, 'day')}"


def levels(cal):
    """GraphQL gives counts; the audit snapshot gives GitHub's 0-4 levels. Normalise to 0-4."""
    vals = [c for _, c in cal]
    if max(vals or [0]) <= 4:
        return vals
    nz = sorted(v for v in vals if v)
    q = [nz[int(len(nz) * f)] for f in (.25, .5, .75)] if nz else [1, 2, 3]
    return [0 if v == 0 else 1 + sum(v > t for t in q) for v in vals]


THAI_FONT = "'Noto Sans Thai', 'Leelawadee UI', Thonburi, sans-serif"


def thai(s):
    """Escape, and put runs of Thai script in a Thai-capable font (monospace stacks rarely have Thai)."""
    import re
    return re.sub(r"([\u0E00-\u0E7F]+)", lambda m: f'<tspan font-family="{THAI_FONT}">{m.group(1)}</tspan>', esc(s))


def kv(x, y, key, val, t, width=74):
    dots = "." * max(2, width - len(key) - len(val) - 2)
    right = x + width * CH
    return (f'<text x="{x}" y="{y}" xml:space="preserve">'
            f'<tspan fill="{t["accent"]}">{esc(key)}</tspan><tspan fill="{t["ink"]}" fill-opacity="{MUTED}">:{dots}</tspan></text>'
            f'<text x="{right:.0f}" y="{y}" text-anchor="end" fill="{t["ink"]}">{thai(val)}</text>\n')


def rule(x, y, label, t, width=74):
    return (f'<text x="{x}" y="{y}" xml:space="preserve" fill="{t["ink"]}" fill-opacity="{MUTED}">'
            f'— <tspan fill="{t["ink"]}" font-weight="700">{esc(label)}</tspan> {"—" * (width - len(label) - 3)}</text>\n')


def render(mode, cfg, data, now):
    t = THEMES[mode]
    out = [svg_open(W, H, t, f"{cfg['legal_name']}: profile readout")]
    out.append(f'<g font-size="13">\n')
    # ASCII portrait (two tone: dense glyphs in accent, the rest in ink)
    art = open(os.path.join(ROOT, "assets", f"portrait-{mode}.txt"), encoding="utf-8").read().splitlines()
    out.append(f'<g font-size="11" fill="{t["ink"]}" fill-opacity="{MUTED}">\n')
    for i, line in enumerate(art):
        y = 30 + i * 14.6
        spans = "".join(f'<tspan fill="{t["accent"]}" fill-opacity="1">{esc(c)}</tspan>' if c in "#@%" else esc(c) for c in line)
        out.append(f'<text x="26" y="{y:.1f}" xml:space="preserve">{spans}</text>\n')
    out.append("</g>\n")

    x, y = 320, 38
    out.append(f'<text x="{x}" y="{y}" font-size="15" font-weight="700"><tspan fill="{t["accent"]}">tanat</tspan>'
               f'<tspan fill="{t["ink"]}">@github.com/{esc(cfg["login"])}</tspan>'
               f'<tspan fill="{t["ink"]}" fill-opacity="{MUTED}" font-weight="400">  ·  {esc(cfg["legal_name"])}  ·  {thai(cfg["thai_name"])}</tspan></text>\n')
    y += LH * 1.4
    for k, v in cfg["neofetch"]:
        out.append(kv(x, y, k, v, t)); y += LH
    y += 6
    out.append(rule(x, y, "GitHub", t)); y += LH
    langs = " · ".join(l for l, _ in data["languages"][:4])
    for k, v in [("Uptime", uptime(data["created_at"], now)),
                 ("Repos", f"{data['public_repos']}  ·  Stars {data['stars']}  ·  Followers {data['followers']}"),
                 ("Commits.Year", f"{data['contributions_last_year']} contributions in the last year"),
                 ("Languages", langs)]:
        out.append(kv(x, y, k, v, t)); y += LH
    y += 6
    out.append(rule(x, y, "Contact", t)); y += LH
    for k, v in cfg["contact"]:
        out.append(kv(x, y, k, v, t)); y += LH
    out.append("</g>\n")

    # 53-week heatmap, same accent, opacity steps only
    cal = data["calendar"][-371:]
    lv = levels(cal)
    if cal:
        first = date.fromisoformat(cal[0][0])
        off = (first.weekday() + 1) % 7          # GitHub weeks start on Sunday
        gx, gy, s, g = x, y + 2, 9, 2
        out.append('<g>\n')
        for i, l in enumerate(lv):
            col, row = divmod(i + off, 7)
            fill, op = (t["ink"], RULE * .8) if l == 0 else (t["accent"], (.3, .5, .75, 1)[l - 1])
            out.append(f'<rect x="{gx + col * (s + g)}" y="{gy + row * (s + g)}" width="{s}" height="{s}" rx="2" fill="{fill}" fill-opacity="{op}"/>\n')
        out.append('</g>\n')
    out.append(f'<text x="{W - 20}" y="{H - 14}" text-anchor="end" font-size="10" fill="{t["ink"]}" fill-opacity="{MUTED}">'
               f'refreshed {data["generated_at"][:10]} by GitHub Actions</text>\n')
    out.append("</svg>\n")
    return "".join(out)


if __name__ == "__main__":
    cfg = json.load(open(os.path.join(ROOT, "config", "profile.json"), encoding="utf-8"))
    data = json.load(open(os.path.join(ROOT, "data", "profile.json"), encoding="utf-8"))
    now = datetime.fromisoformat(data["generated_at"]).astimezone(timezone.utc)
    for mode in THEMES:
        with open(os.path.join(ROOT, "assets", f"hero-{mode}.svg"), "w", encoding="utf-8") as f:
            f.write(render(mode, cfg, data, now))
    print("hero rendered")
