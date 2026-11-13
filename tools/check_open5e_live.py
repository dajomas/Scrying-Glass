#!/usr/bin/env python3
"""Manual live Open5e v2 contract check (SG-TODO-017). Not part of CI.

Runs the real provider against https://api.open5e.com/v2 and verifies the
fields the fixtures assume. Network results change with Open5e releases, so a
failure here is evidence to review, not an automatic regression.
Usage: python3 tools/check_open5e_live.py [species ...]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from python import scrying_glass_open5e as open5e  # noqa: E402


def main(names):
    failures = 0
    catalog = open5e.documents(open5e.DEFAULT_BASE_URL)
    print(f"documents: {len(catalog)}")
    for species in names:
        found = open5e.candidates(species, {})
        print(f"{species}: {len(found)} candidate(s)")
        for item in found:
            print(f"  - {item['name']} | {item['source']} | {item['game_system']} | AC {item['ac']} "
                  f"| HP {item['hp']} ({item['hp_source']}) | init {item['initiative_bonus']} "
                  f"| image {'yes' if item['image_url'] else 'no'} | {item['attribution']}")
            if item["ac"] is None or item["hp"] is None or not item["source_url"].startswith(
                    open5e.CANONICAL_BASE_URL + "/creatures/"):
                failures += 1
        if not found:
            failures += 1
    print("result:", "PASS" if failures == 0 else f"FAIL ({failures})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["Goblin", "Aboleth", "Adult Red Dragon"]))
