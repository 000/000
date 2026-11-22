"""Render PNG previews of every SVG in assets/.

Prefers headless Chrome (same text shaping and font fallback as a browser viewing GitHub, so Thai renders);
falls back to cairosvg. Usage: python scripts/preview.py OUTDIR
"""
import glob, os, re, shutil, subprocess, sys, tempfile

out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "previews")
os.makedirs(out, exist_ok=True)
chrome = next((c for c in ("google-chrome", "chromium", "chromium-browser") if shutil.which(c)), None)
for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "*.svg"))):
    png = os.path.join(out, os.path.basename(f)[:-4] + ".png")
    head = open(f, encoding="utf-8").read(400)
    w, h = (int(float(v)) for v in re.search(r'width="([\d.]+)" height="([\d.]+)"', head).groups())
    if chrome:
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as t:
            t.write(f'<html><body style="margin:0;background:transparent"><img src="file://{os.path.abspath(f)}" width="{w}" height="{h}"></body></html>')
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                        "--force-device-scale-factor=2", f"--window-size={w},{h}", "--default-background-color=00000000",
                        f"--screenshot={png}", f"file://{t.name}"], check=True, capture_output=True)
        os.unlink(t.name)
    else:
        import cairosvg
        cairosvg.svg2png(url=f, write_to=png, scale=2)
    print(png)
