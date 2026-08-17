"""Generate the Ember Profile artwork from GitHub's public REST API.

No third-party stats service and no Python packages are required.

    python scripts/generate.py          # live GitHub data
    python scripts/generate.py --demo   # deterministic preview data
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
CONFIG = ROOT / "config.json"

# Warm, theme-safe colors chosen to stay readable on both GitHub themes.
BG = "#09080d"
SHELL = "#16131d"
CORE = "#100e16"
CARD = "#191620"
BORDER = "#393143"
CORAL = "#ff6b4a"
ORANGE = "#ff9f43"
GOLD = "#ffd166"
CREAM = "#fff8ef"
MUTED = "#b7afbf"
CYAN = "#5dd9f5"

DEMO = {
    "public_repos": 86,
    "followers": 34,
    "following": 18,
    "stars": 119,
    "languages": [["TypeScript", 36], ["JavaScript", 28], ["Python", 17], ["CSS", 11], ["Other", 8]],
    "repos": [
        {"name": "Zeropoint-website", "description": "A sharp digital home for an ambitious product team.", "language": "TypeScript", "stargazers_count": 42, "forks_count": 8},
        {"name": "Jenesyx-Website", "description": "Personal portfolio, experiments and selected client work.", "language": "JavaScript", "stargazers_count": 31, "forks_count": 5},
        {"name": "TodoList", "description": "A focused task system with a clean interaction model.", "language": "TypeScript", "stargazers_count": 27, "forks_count": 4},
        {"name": "404Error-page", "description": "A playful, responsive not-found page concept.", "language": "CSS", "stargazers_count": 19, "forks_count": 3},
    ],
}


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def request_json(url: str) -> object:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "ember-profile"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=25) as response:
        return json.load(response)


def live_data(username: str, featured: list[str]) -> dict:
    user = request_json(f"https://api.github.com/users/{username}")
    repos = request_json(f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated")
    if not isinstance(user, dict) or not isinstance(repos, list):
        raise RuntimeError("Unexpected response from GitHub")

    original = [repo for repo in repos if not repo.get("fork")]
    by_name = {repo.get("name", "").lower(): repo for repo in original}
    chosen = [by_name[name.lower()] for name in featured if name.lower() in by_name]
    chosen_names = {repo.get("name") for repo in chosen}
    ranked = sorted(
        original,
        key=lambda item: (item.get("stargazers_count", 0), item.get("updated_at", "")),
        reverse=True,
    )
    for repo in ranked:
        if repo.get("name") not in chosen_names and len(chosen) < 4:
            chosen.append(repo)

    language_counts: dict[str, int] = {}
    for repo in original:
        language = repo.get("language")
        if language:
            language_counts[language] = language_counts.get(language, 0) + 1
    languages = sorted(language_counts.items(), key=lambda item: item[1], reverse=True)[:5]

    return {
        "public_repos": user.get("public_repos", len(repos)),
        "followers": user.get("followers", 0),
        "following": user.get("following", 0),
        "stars": sum(repo.get("stargazers_count", 0) for repo in original),
        "languages": languages,
        "repos": chosen[:4],
    }


def clip(value: object, length: int) -> str:
    text = " ".join(str(value or "").split())
    return text if len(text) <= length else text[: length - 1].rstrip() + "…"


def hero_svg(config: dict, stats: dict) -> str:
    skill_nodes = "".join(
        f'<g transform="translate({42 + index * 108} 282)">'
        f'<rect width="98" height="28" rx="14" fill="{CARD}" stroke="{BORDER}"/>'
        f'<text x="49" y="18" text-anchor="middle" class="tag">{escape(skill)}</text></g>'
        for index, skill in enumerate(config["skills"][:5])
    )
    role_line = f"{config['role']}  ·  {config['location']}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="340" viewBox="0 0 900 340" role="img" aria-label="Profile banner for {escape(config['name'])}">
<defs>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop stop-color="{CORAL}"/><stop offset=".55" stop-color="{ORANGE}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>
  <radialGradient id="flare" cx="83%" cy="35%" r="55%"><stop offset="0" stop-color="{CORAL}" stop-opacity=".22"/><stop offset=".5" stop-color="{ORANGE}" stop-opacity=".07"/><stop offset="1" stop-color="{BG}" stop-opacity="0"/></radialGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="8" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <style>.display{{font:700 54px 'Segoe UI',Inter,sans-serif;fill:{CREAM};letter-spacing:-1.8px}}.role{{font:600 18px 'Segoe UI',Inter,sans-serif;fill:{CREAM}}}.body{{font:15px 'Segoe UI',Inter,sans-serif;fill:{MUTED}}}.label{{font:700 11px 'Segoe UI',Inter,sans-serif;fill:{ORANGE};letter-spacing:1.7px}}.tag{{font:600 12px 'Segoe UI',Inter,sans-serif;fill:{CREAM}}}.metric{{font:700 35px 'Segoe UI',Inter,sans-serif;fill:{CREAM}}}.meta{{font:700 10px 'Segoe UI',Inter,sans-serif;fill:{MUTED};letter-spacing:1.2px}}@keyframes appear{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}@keyframes breathe{{50%{{opacity:.55}}}}.intro{{animation:appear .55s cubic-bezier(.16,1,.3,1) both}}.pulse{{animation:breathe 3.6s ease-in-out infinite}}@media(prefers-reduced-motion:reduce){{.intro,.pulse{{animation:none}}}}</style>
</defs>
<rect width="900" height="340" rx="26" fill="{SHELL}"/>
<rect x="7" y="7" width="886" height="326" rx="21" fill="{CORE}" stroke="{BORDER}"/>
<rect x="7" y="7" width="886" height="326" rx="21" fill="url(#flare)"/>
<path d="M28 8h844" stroke="url(#accent)" stroke-width="3" stroke-linecap="round"/>
<g class="intro">
  <circle cx="43" cy="43" r="5" fill="{CORAL}" class="pulse" filter="url(#glow)"/>
  <text x="57" y="47" class="label">DEVELOPER PROFILE  /  @{escape(config['username'].upper())}</text>
  <text x="42" y="117" class="display">{escape(config['name'])}</text>
  <text x="42" y="151" class="role">{escape(role_line)}</text>
  <text x="42" y="196" class="body">{escape(clip(config['status'], 62))}</text>
  <text x="42" y="231" class="label">BUILDING NOW</text>
  <text x="42" y="255" class="body">{escape(clip(config['focus'], 72))}</text>
  {skill_nodes}
</g>
<g transform="translate(616 53)">
  <rect width="242" height="234" rx="22" fill="{CARD}" stroke="{BORDER}"/>
  <text x="22" y="34" class="label">LIVE SNAPSHOT</text>
  <circle cx="206" cy="29" r="4" fill="{GOLD}" class="pulse"/>
  <path d="M22 52h198" stroke="{BORDER}"/>
  <text x="22" y="104" class="metric">{stats['public_repos']}</text>
  <text x="22" y="125" class="meta">REPOSITORIES</text>
  <text x="139" y="104" class="metric">{stats['stars']}</text>
  <text x="139" y="125" class="meta">TOTAL STARS</text>
  <path d="M22 147h198" stroke="{BORDER}"/>
  <text x="22" y="191" class="metric">{stats['followers']}</text>
  <text x="22" y="212" class="meta">FOLLOWERS</text>
  <path d="M139 181h67" stroke="{BORDER}" stroke-width="6" stroke-linecap="round"/>
  <path d="M139 181h{min(67, 16 + int(stats['followers']) % 52)}" stroke="url(#accent)" stroke-width="6" stroke-linecap="round"/>
</g>
<text x="858" y="317" text-anchor="end" class="meta">LIVE PUBLIC DATA  /  AUTO-REFRESHED</text>
</svg>'''


def signal_svg(config: dict, stats: dict) -> str:
    metrics = [
        ("PUBLIC REPOSITORIES", stats["public_repos"], CORAL),
        ("TOTAL STARS", stats["stars"], ORANGE),
        ("FOLLOWERS", stats["followers"], GOLD),
        ("FOLLOWING", stats["following"], CYAN),
    ]
    metric_nodes = []
    for index, (label, value, color) in enumerate(metrics):
        x = 32 + (index % 2) * 432
        y = 70 + (index // 2) * 106
        metric_nodes.append(
            f'<g transform="translate({x} {y})" class="reveal" style="animation-delay:{index * .06:.2f}s">'
            f'<rect width="404" height="88" rx="16" fill="{CARD}" stroke="{BORDER}"/>'
            f'<circle cx="378" cy="25" r="5" fill="{color}"/>'
            f'<text x="20" y="29" class="label">{label}</text>'
            f'<text x="20" y="69" class="metric">{value}</text>'
            f'<path d="M310 66h68" stroke="{BORDER}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M310 66h{min(68, 18 + int(value) % 51)}" stroke="{color}" stroke-width="7" stroke-linecap="round"/>'
            f'</g>'
        )

    languages = stats["languages"][:5] or [["No language data", 1]]
    total = max(1, sum(int(count) for _, count in languages))
    language_colors = [CORAL, ORANGE, GOLD, CYAN, "#a78bfa"]
    language_segments = []
    language_legend = []
    used_width = 0
    for index, (language, count) in enumerate(languages):
        width = 836 - used_width if index == len(languages) - 1 else round(836 * int(count) / total)
        color = language_colors[index]
        language_segments.append(
            f'<rect x="{32 + used_width}" y="347" width="{max(1, width)}" height="18" fill="{color}" class="bar" style="animation-delay:{index * .06:.2f}s"/>'
        )
        percent = round(int(count) / total * 100)
        legend_x = 32 + index * 168
        language_legend.append(
            f'<circle cx="{legend_x + 5}" cy="391" r="5" fill="{color}"/>'
            f'<text x="{legend_x + 17}" y="395" class="legend">{escape(clip(language, 13))}  {percent}%</text>'
        )
        used_width += width

    repo_nodes = []
    for index, repo in enumerate(stats["repos"][:4]):
        x = 32 + (index % 2) * 432
        y = 452 + (index // 2) * 76
        accent = language_colors[index]
        language = escape(repo.get("language") or "Mixed")
        stars = int(repo.get("stargazers_count", 0))
        forks = int(repo.get("forks_count", 0))
        star_label = "star" if stars == 1 else "stars"
        fork_label = "fork" if forks == 1 else "forks"
        repo_nodes.append(
            f'<g transform="translate({x} {y})" class="reveal" style="animation-delay:{.18 + index * .06:.2f}s">'
            f'<rect width="404" height="64" rx="14" fill="{CARD}" stroke="{BORDER}"/>'
            f'<rect x="0" y="14" width="3" height="36" rx="2" fill="{accent}"/>'
            f'<text x="20" y="28" class="repo">{escape(clip(repo.get("name"), 32))}</text>'
            f'<text x="20" y="49" class="meta">{language}  ·  {stars} {star_label}  ·  {forks} {fork_label}</text>'
            f'</g>'
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="620" viewBox="0 0 900 620" role="img" aria-label="GitHub activity overview for {escape(config['username'])}">
<defs>
  <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop stop-color="{CORAL}"/><stop offset=".55" stop-color="{ORANGE}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>
  <clipPath id="languageClip"><rect x="32" y="347" width="836" height="18" rx="9"/></clipPath>
  <style>.title{{font:700 23px 'Segoe UI',Inter,sans-serif;fill:{CREAM};letter-spacing:-.3px}}.label{{font:700 11px 'Segoe UI',Inter,sans-serif;fill:{MUTED};letter-spacing:1.35px}}.metric{{font:700 35px 'Segoe UI',Inter,sans-serif;fill:{CREAM}}}.legend{{font:600 12px 'Segoe UI',Inter,sans-serif;fill:{CREAM}}}.repo{{font:700 15px 'Segoe UI',Inter,sans-serif;fill:{CREAM}}}.meta{{font:11px 'Segoe UI',Inter,sans-serif;fill:{MUTED}}}@keyframes reveal{{from{{opacity:0}}to{{opacity:1}}}}@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}.reveal{{animation:reveal .45s ease-out both}}.bar{{transform-origin:left;animation:grow .65s cubic-bezier(.16,1,.3,1) both}}@media(prefers-reduced-motion:reduce){{.reveal,.bar{{animation:none}}}}</style>
</defs>
<rect width="900" height="620" rx="26" fill="{SHELL}"/>
<rect x="7" y="7" width="886" height="606" rx="21" fill="{CORE}" stroke="{BORDER}"/>
<path d="M28 8h844" stroke="url(#accent)" stroke-width="3" stroke-linecap="round"/>
<text x="32" y="44" class="title">A clearer look at the work</text>
<text x="868" y="43" text-anchor="end" class="label">LIVE GITHUB ACTIVITY  /  @{escape(config['username'].upper())}</text>
{''.join(metric_nodes)}
<text x="32" y="321" class="title">Most-used languages</text>
<rect x="32" y="347" width="836" height="18" rx="9" fill="{BORDER}"/>
<g clip-path="url(#languageClip)">{''.join(language_segments)}</g>
{''.join(language_legend)}
<text x="32" y="430" class="title">Selected repositories</text>
{''.join(repo_nodes)}
<text x="32" y="601" class="meta">Generated from public GitHub data · no external stats service</text>
<text x="868" y="601" text-anchor="end" class="label">AUTO-REFRESHED</text>
</svg>'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="use deterministic preview data")
    args = parser.parse_args()
    config = load_config()
    username = os.environ.get("GH_USERNAME") or os.environ.get("GITHUB_REPOSITORY_OWNER") or config["username"]
    config["username"] = username
    if args.demo:
        stats = DEMO
    else:
        try:
            stats = live_data(username, config.get("featured_repos", []))
        except (urllib.error.URLError, RuntimeError) as exc:
            raise SystemExit(f"GitHub data request failed: {exc}. Use --demo for an offline preview.")
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "hero.svg").write_text(hero_svg(config, stats), encoding="utf-8")
    (ASSETS / "signal.svg").write_text(signal_svg(config, stats), encoding="utf-8")
    print(f"Generated Ember Profile assets for @{username}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
