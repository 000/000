"""One design system for every asset: 3 colours (canvas, ink, accent), one radius, one type stack."""
from xml.sax.saxutils import escape

THEMES = {
    # canvas = GitHub's own page background, so cards sit flush on the profile.
    "dark":  {"canvas": "#0d1117", "ink": "#e6edf3", "accent": "#ff9e3d"},
    "light": {"canvas": "#ffffff", "ink": "#1f2328", "accent": "#bc4c00"},
}
RADIUS = 6            # matches GitHub's Primer radius
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', 'Noto Sans Thai', monospace"
MUTED = 0.62          # muted text = ink at this opacity (keeps the palette at 3 colours)
RULE = 0.16           # hairlines  = ink at this opacity


def esc(s):
    return escape(str(s), {'"': "&quot;"})


def svg_open(w, h, t, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{MONO}" style="font-variant-ligatures:none" role="img" aria-label="{esc(title)}">\n<title>{esc(title)}</title>\n'
            f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{RADIUS}" fill="{t["canvas"]}" '
            f'stroke="{t["ink"]}" stroke-opacity="{RULE}"/>\n')
