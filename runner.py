import time
import subprocess
import json
import os

JSON_PATH = os.path.join(os.path.dirname(__file__), "structured_matches.json")


def print_latest_snapshot():
    try:
        with open(JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print("JSON read error:", e)
        return

    if not data:
        print("No matches found.")
        return

    print("~" * 70)
    print("LATEST MATCH ")
    print("~" * 70)

    for m in data:
        fmt = m.get("format", "")
        title = m.get("match_title", "")
        t1 = m.get("team1", "")
        s1 = m.get("team1_score", "")
        t2 = m.get("team2", "")
        s2 = m.get("team2_score", "")
        status = m.get("status", "")

        print(f"{fmt} | {title}")
        print(f"  {t1:>4} {s1:<20} vs {t2:>4} {s2 or '-'}")
        print(f"  {status}")
        print("-" * 70)


def main():
    while True:
        print("\nRunning spider: cricbuzz_home ...")
        subprocess.run(
            ["scrapy", "crawl", "cricbuzz_home", "-O", "structured_matches.json"],
            check=False,
        )
        print_latest_snapshot()
        time.sleep(30)


if __name__ == "__main__":
    main()
