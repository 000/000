#!/usr/bin/env bash
# Local rebuild: (optional) fetch with a token, then render all assets, the README and PNG previews.
set -euo pipefail
cd "$(dirname "$0")"
[ -n "${GITHUB_TOKEN:-}" ] && python3 fetch_data.py || echo "no GITHUB_TOKEN: using data/profile.json snapshot"
python3 render_hero.py && python3 render_stack.py && python3 render_poll.py && python3 build_readme.py
python3 preview.py ../../previews 2>/dev/null || echo "previews need cairosvg or Chrome"
