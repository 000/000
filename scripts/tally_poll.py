"""Record one poll vote from an issue. Called by .github/workflows/poll.yml.

Inputs come from env (never interpolated into shell): ISSUE_TITLE, ISSUE_USER.
Prints a one-line result for the bot comment. Exit code 0 = counted, 2 = ignored.
"""
import json, os, re, sys
from datetime import datetime, timezone

ROOT = os.path.join(os.path.dirname(__file__), "..")
cfg = json.load(open(os.path.join(ROOT, "config", "profile.json"), encoding="utf-8"))
path = os.path.join(ROOT, "data", "poll.json")
poll = json.load(open(path, encoding="utf-8"))

title, user = os.environ.get("ISSUE_TITLE", ""), os.environ.get("ISSUE_USER", "")
m = re.fullmatch(r"\s*poll:\s*([A-Za-z])\s*", title)
opt = m and m.group(1).upper()
if not opt or opt not in cfg["poll"]["options"] or not re.fullmatch(r"[A-Za-z0-9-]{1,39}", user):
    print("Not a valid vote (title must be `poll: A`…). Nothing recorded.")
    sys.exit(2)
prev = poll["votes"].get(user)
poll["votes"][user] = opt
poll["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
json.dump(poll, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
label = cfg["poll"]["options"][opt]
print(f"Thanks @{user}! Counted your vote for **[{opt}] {label}**" + (f" (moved from {prev})." if prev and prev != opt else "."))
