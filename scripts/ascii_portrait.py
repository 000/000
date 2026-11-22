"""One-off: turn the GitHub avatar into two ASCII portraits (dark/light canvases). Needs Pillow.

Run locally when the avatar changes:  python scripts/ascii_portrait.py path/to/avatar.png
"""
import sys
from PIL import Image, ImageOps

COLS, ROWS = 40, 28
RAMP = " .,:;-=+*cxo%#@"      # sparse -> dense


def render(img, invert):
    g = ImageOps.equalize(img.convert("L")).resize((COLS, ROWS), Image.LANCZOS)
    lines = []
    for y in range(ROWS):
        row = ""
        for x in range(COLS):
            v = g.getpixel((x, y)) / 255
            v = 1 - v if invert else v
            # elliptical vignette: blank the busy office background, keep head & shoulders
            dx, dy = (x - COLS * .47) / (COLS * .40), (y - ROWS * .55) / (ROWS * .62)
            if dx * dx + dy * dy > 1:
                v = 0
            row += RAMP[min(int(v * len(RAMP)), len(RAMP) - 1)]
        lines.append(row.rstrip())
    return "\n".join(lines)


if __name__ == "__main__":
    im = Image.open(sys.argv[1])
    w, h = im.size
    im = im.crop((int(w * .20), int(h * .0), int(w * .90), int(h * .95)))   # head & shoulders
    open("assets/portrait-dark.txt", "w").write(render(im, invert=False))   # light pixels = dense ink on dark canvas
    open("assets/portrait-light.txt", "w").write(render(im, invert=True))
    print(render(im, False))
