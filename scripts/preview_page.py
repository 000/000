"""Full-page README mock (dark + light) via GitHub's public /markdown renderer + headless Chrome.
Usage: python scripts/preview_page.py OUTDIR   (read-only: the markdown API only renders text)"""
import json, os, re, subprocess, sys, urllib.request

out_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "previews")
root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
md = open(os.path.join(root, "README.md"), encoding="utf-8").read()
req = urllib.request.Request("https://api.github.com/markdown", data=json.dumps({"text": md, "mode": "gfm"}).encode(),
                             headers={"Accept": "application/vnd.github+json", "User-Agent": "preview"})
html = urllib.request.urlopen(req).read().decode().replace("./assets/", f"file://{root}/assets/")
html = re.sub(r"<picture>(?:(?!</picture>).)*?raw\.githubusercontent\.com(?:(?!</picture>).)*?</picture>",
              '<div style="border:1px dashed currentColor;opacity:.5;padding:18px;text-align:center;font:12px monospace;border-radius:6px">'
              "[snake SVG: baked daily by Platane/snk into the output branch; appears after the first run]</div>", html, flags=re.S)
for mode, bg, fg, link, border in [("dark", "#0d1117", "#e6edf3", "#4493f8", "#30363d"), ("light", "#ffffff", "#1f2328", "#0969da", "#d0d7de")]:
    css = (f'body{{background:{bg};color:{fg};font:14px/1.5 -apple-system,"Segoe UI","Noto Sans","Noto Sans Thai",Helvetica,Arial,sans-serif;margin:0;padding:24px}}'
           f".box{{border:1px solid {border};border-radius:6px;padding:24px;max-width:880px;margin:auto}}"
           f".hdr{{font:12px monospace;opacity:.7;margin:-8px 0 16px}}a{{color:{link};text-decoration:none}}h3,h4{{margin:24px 0 8px}}"
           f"h3{{border-bottom:1px solid {border};padding-bottom:6px}}table{{border-collapse:collapse;width:100%}}td{{border:1px solid {border};padding:6px 13px}}"
           "img{max-width:100%}ul{padding-left:2em}")
    f = f"/tmp/readme-{mode}.html"
    open(f, "w", encoding="utf-8").write(f'<html><head><meta charset="utf-8"><style>{css}</style></head><body><div class="box">'
                                         f'<div class="hdr">000 / README.md: prototype preview ({mode} mode)</div>{html}</div></body></html>')
    png = os.path.join(out_dir, f"README-page-{mode}.png")
    subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--blink-settings=preferredColorScheme={0 if mode == 'dark' else 1}", "--force-device-scale-factor=1.5",
                    "--window-size=930,1850", f"--screenshot={png}", f"file://{f}"], check=True, capture_output=True)
    print(png)
