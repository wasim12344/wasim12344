#!/usr/bin/env python3
"""
Scrape real daily contribution counts from GitHub's public, unauthenticated
contributions endpoint (the same fragment the profile page itself uses) and
write data/contributions.json with raw days plus derived stats.
"""
import datetime
import json
import os
import re
import sys
import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "wasim12344")
URL = f"https://github.com/users/{USERNAME}/contributions"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "data", "contributions.json")


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot/1.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        print("no calendar cells found -- github markup may have changed", file=sys.stderr)
        sys.exit(1)

    days = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        td_id = td.get("id")
        tooltip_el = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None
        text = tooltip_el.get_text(strip=True) if tooltip_el else ""
        if not text:
            # Fallback to td text or aria-label
            text = td.get_text(strip=True) or td.get("aria-label", "")

        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            m = re.search(r"(\d+)\s+contribution", text, re.I)
            if not m:
                m = re.match(r"(\d+)", text)
            count = int(m.group(1)) if m else 0
        days.append({"date": date, "count": count})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)
    
    # Calculate streaks
    # Sort descending by date to compute current streak from latest day
    today_str = datetime.date.today().isoformat()
    rev_days = sorted(days, key=lambda d: d["date"], reverse=True)
    
    current_streak = 0
    counting_current = False
    
    # Check if today or yesterday had contributions
    for d in rev_days:
        if d["date"] > today_str:
            continue
        if d["count"] > 0:
            current_streak += 1
            counting_current = True
        else:
            # If streak started, zero breaks it
            if counting_current:
                break
            # If today has 0, check if yesterday had >0 before giving up
            days_ago = (datetime.date.fromisoformat(today_str) - datetime.date.fromisoformat(d["date"])).days
            if days_ago > 1:
                break

    # Longest streak
    longest_streak = 0
    cur = 0
    for d in days:
        if d["count"] > 0:
            cur += 1
            if cur > longest_streak:
                longest_streak = cur
        else:
            cur = 0

    # Best day
    best_day = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}

    return {
        "username": USERNAME,
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "days": days
    }


def main():
    print(f"Fetching contribution data for {USERNAME}...")
    days = fetch_days()
    stats = compute_stats(days)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"Successfully saved {len(days)} days ({stats['total']} total contributions) to {OUT_PATH}")


if __name__ == "__main__":
    main()
