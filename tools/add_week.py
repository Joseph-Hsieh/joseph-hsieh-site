#!/usr/bin/env python3
"""Add one week of news to data/site.json.

Usage:  python3 tools/add_week.py path/to/week.json

week.json format:
{
  "week": "2026-10-05",            # Monday of the week, YYYY-MM-DD
  "label": "2026 年 10 月第 1 週",   # Chinese label shown on the site
  "items": {
    "impact": [ {item}, ... ],      # 全球影響力投資
    "gvc":    [ ... ],              # 全球創業投資
    "twvc":   [ ... ],              # 台灣創投
    "fo":     [ ... ]               # 家族辦公室
  }
}
item = {"title_zh","title_en","title_ja","sum_zh","sum_en","sum_ja","source","date","url"}

Each of the four categories carries 7 to 9 items per week (28 to 36 in total).

The script validates every field, drops links that already appeared in an
earlier week, replaces an existing entry for the same week and keeps weeks
newest first. Past weeks are never deleted: the archive keeps growing and
stays searchable on the site.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "site.json")
CATS = ["impact", "gvc", "twvc", "fo"]
FIELDS = ["title_zh", "title_en", "title_ja", "sum_zh", "sum_en", "sum_ja", "source", "date", "url"]
MIN_ITEMS, MAX_ITEMS = 7, 9


def fail(msg):
    sys.exit("ERROR: " + msg)


def main(path):
    week = json.load(open(path, encoding="utf-8"))
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", week.get("week", "")):
        fail("week must be YYYY-MM-DD")
    week.setdefault("label", week["week"])
    items = week.get("items") or {}
    site = json.load(open(DATA, encoding="utf-8"))
    weeks = site.setdefault("news", {}).setdefault("weeks", [])
    seen = {n.get("url") for w in weeks if w.get("week") != week["week"]
            for c in CATS for n in w.get("items", {}).get(c, [])}
    total = 0
    for c in CATS:
        clean = []
        for n in items.get(c, []):
            missing = [f for f in FIELDS if not str(n.get(f, "")).strip()]
            if missing:
                fail("%s item '%s' missing %s" % (c, n.get("title_zh", "?"), ", ".join(missing)))
            if not n["url"].startswith("http"):
                fail("bad url: %s" % n["url"])
            if n["url"] in seen:
                print("skip (already published): %s" % n["url"])
                continue
            seen.add(n["url"])
            clean.append({f: n[f].strip() for f in FIELDS})
        items[c] = clean
        total += len(clean)
    if total == 0:
        fail("no items to publish")
    for c in CATS:
        k = len(items.get(c, []))
        if k > MAX_ITEMS:
            fail("%s has %d items; keep each category to %d-%d" % (c, k, MIN_ITEMS, MAX_ITEMS))
        if k < MIN_ITEMS:
            print("WARNING: %s has only %d items (target %d-%d per category)" % (c, k, MIN_ITEMS, MAX_ITEMS))
    week["items"] = {c: items.get(c, []) for c in CATS}
    weeks = [w for w in weeks if w.get("week") != week["week"]] + [week]
    weeks.sort(key=lambda w: w["week"], reverse=True)
    site["news"]["weeks"] = weeks
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(site, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("Added week %s with %d items (%s)" % (week["week"], total,
          ", ".join("%s=%d" % (c, len(week["items"][c])) for c in CATS)))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        fail(__doc__)
    main(sys.argv[1])
