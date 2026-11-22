"""simonw-style README injection: rewrite the blocks between <!-- name:start --> / <!-- name:end --> markers."""
import json, os, re
from urllib.parse import quote

ROOT = os.path.join(os.path.dirname(__file__), "..")
cfg = json.load(open(os.path.join(ROOT, "config", "profile.json"), encoding="utf-8"))
data = json.load(open(os.path.join(ROOT, "data", "profile.json"), encoding="utf-8"))


def replace(text, name, body):
    pat = re.compile(rf"(<!-- {name}:start -->).*?(<!-- {name}:end -->)", re.S)
    return pat.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", text)


def featured():
    rows = []
    for r in data["pinned"][:6]:
        line = cfg["featured_overrides"].get(r["name"]) or r["description"] or "PLACEHOLDER: add a one-line description to this repo."
        meta = " · ".join(x for x in [r.get("language"), f"★ {r['stars']}" if r.get("stars") else None] if x)
        rows.append(f"- **[{r['name']}]({r['url']})**: {line}" + (f" <sub>{meta}</sub>" if meta else ""))
    return "\n".join(rows)


def shipped():
    own = [r for r in data["repos"] if not r["fork"] and r["name"] != cfg["login"]][:5]
    return "\n".join(f"- [{r['name']}]({r['url']}) <sub>{r['pushed_at'][:10]}</sub>" for r in own)


def releases():
    if not data["releases"]:
        return "- <sub>No tagged releases yet. Tag one and it appears here on the next daily run.</sub>"
    return "\n".join(f"- [{r['repo']} {r['name']}]({r['url']}) <sub>{r['published_at'][:10]}</sub>" for r in data["releases"])


def papers():
    return "\n".join(f"- [{p['title']}]({p['url']}) <sub>{p['venue']}</sub>" for p in cfg["papers"])


def poll_links():
    base = f"https://github.com/{cfg['login']}/{cfg['login']}/issues/new"
    body = quote("Just press **Submit new issue**. A GitHub Action counts your vote, redraws the poll and closes this issue.")
    from html import escape
    return " · ".join(f'<a href="{base}?title={quote("poll: " + k)}&amp;body={body}"><b>{k}</b> {escape(v)}</a>'
                      for k, v in cfg["poll"]["options"].items())


if __name__ == "__main__":
    p = os.path.join(ROOT, "README.md")
    text = open(p, encoding="utf-8").read()
    for name, body in [("positioning", f"<p align=\"center\"><b>{cfg['positioning']}</b></p>"),
                       ("featured", featured()), ("shipped", shipped()), ("releases", releases()),
                       ("papers", papers()), ("poll", f"<p align=\"center\"><sub>Vote: {poll_links()}</sub></p>")]:
        text = replace(text, name, body)
    open(p, "w", encoding="utf-8").write(text)
    print("README rebuilt")
