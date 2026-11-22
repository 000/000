"""Fetch public profile data with the workflow's own GITHUB_TOKEN (GraphQL) and write data/profile.json.

No personal access token: only public data is used. Stdlib only.
"""
import json, os, sys, urllib.request
from collections import Counter
from datetime import datetime, timezone

LOGIN = os.environ.get("PROFILE_LOGIN", "000")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "profile.json")

QUERY = """
query($login: String!) {
  user(login: $login) {
    name login createdAt
    followers { totalCount }
    pinnedItems(first: 6, types: REPOSITORY) { nodes { ... on Repository {
      name description url isFork stargazerCount
      primaryLanguage { name }
      repositoryTopics(first: 8) { nodes { topic { name } } } } } }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name description url isFork pushedAt stargazerCount
        primaryLanguage { name }
        releases(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
          nodes { name tagName publishedAt url } }
      }
    }
    contributionsCollection { contributionCalendar { totalContributions
      weeks { contributionDays { date contributionCount } } } }
  }
}"""


def graphql(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-builder"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        sys.exit(f"GraphQL errors: {body['errors']}")
    return body["data"]["user"]


def repo_row(n):
    return {
        "name": n["name"], "description": n.get("description") or "", "url": n["url"],
        "fork": n.get("isFork", False), "stars": n.get("stargazerCount", 0),
        "language": (n.get("primaryLanguage") or {}).get("name"),
        "topics": [t["topic"]["name"] for t in (n.get("repositoryTopics") or {}).get("nodes", [])],
        "pushed_at": n.get("pushedAt"),
    }


def normalise(u):
    repos = u["repositories"]["nodes"]
    days = [d for w in u["contributionsCollection"]["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    langs = Counter(r["primaryLanguage"]["name"] for r in repos if r["primaryLanguage"] and not r["isFork"])
    releases = []
    for r in repos:
        for rel in r["releases"]["nodes"]:
            releases.append({"repo": r["name"], "name": rel["name"] or rel["tagName"],
                             "url": rel["url"], "published_at": rel["publishedAt"]})
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "graphql",
        "name": u["name"], "login": u["login"], "created_at": u["createdAt"],
        "followers": u["followers"]["totalCount"],
        "public_repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "languages": langs.most_common(5),
        "contributions_last_year": u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "calendar": [[d["date"], d["contributionCount"]] for d in days],
        "pinned": [repo_row(n) for n in u["pinnedItems"]["nodes"]],
        "pinned_source": "github",
        "repos": [repo_row(n) for n in repos],
        "releases": sorted(releases, key=lambda x: x["published_at"], reverse=True)[:5],
    }


if __name__ == "__main__":
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN not set; keeping the committed data/profile.json snapshot.")
    data = normalise(graphql(token))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"wrote {OUT}: {data['public_repos']} repos, {data['contributions_last_year']} contributions")
