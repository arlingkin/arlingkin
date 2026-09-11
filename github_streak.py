#!/usr/bin/env python3
"""
github_streak.py
-----------------
Raw GitHub contribution streak calculator.

No third-party render service (no streak-stats.demolab.com, no flaky
shared instance). Scrapes GitHub's own public contribution calendar
page directly and computes current streak, longest streak, and
active days — 100% first-party data.

Usage:
    python3 github_streak.py <github_username>

Output:
    - JSON stats to stdout
    - Ready-to-paste shields.io badge markdown
"""

import sys
import re
import json
import urllib.request


def fetch_contributions(username: str) -> list[tuple[str, int]]:
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode("utf-8")

    pattern = re.compile(r'data-date="([0-9-]+)"[^>]*data-level="([0-9])"')
    days = sorted(pattern.findall(html))
    return [(d, int(lvl)) for d, lvl in days]


def compute_streaks(days: list[tuple[str, int]]) -> dict:
    current = 0
    for _, lvl in reversed(days):
        if lvl > 0:
            current += 1
        else:
            break

    longest, run, run_start, best_range = 0, 0, None, None
    for d, lvl in days:
        if lvl > 0:
            if run == 0:
                run_start = d
            run += 1
            if run > longest:
                longest, best_range = run, (run_start, d)
        else:
            run = 0

    active_days = sum(1 for _, lvl in days if lvl > 0)

    return {
        "current_streak": current,
        "longest_streak": longest,
        "longest_range": best_range,
        "active_days_last_year": active_days,
        "as_of": days[-1][0] if days else None,
    }


def badge_markdown(stats: dict) -> str:
    cur, lng = stats["current_streak"], stats["longest_streak"]
    return (
        f'<img src="https://img.shields.io/badge/Current%20Streak-{cur}%20day'
        f'{"s" if cur != 1 else ""}-10b981?style=for-the-badge&logo=fire&logoColor=white" '
        f'alt="current streak" />\n'
        f'<img src="https://img.shields.io/badge/Longest%20Streak-{lng}%20days-10b981'
        f'?style=for-the-badge&logo=fire&logoColor=white" alt="longest streak" />'
    )


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 github_streak.py <github_username>")
        sys.exit(1)

    username = sys.argv[1]
    days = fetch_contributions(username)
    stats = compute_streaks(days)
    stats["user"] = username

    print(json.dumps(stats, indent=2))
    print("\n--- Markdown badges (paste into README) ---")
    print(badge_markdown(stats))


if __name__ == "__main__":
    main()
