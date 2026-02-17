"""Seed the database with all current job listings, marked as already posted.

Run this ONCE before starting the bot on a new server so the first
check_jobs cycle only picks up genuinely new listings.

Usage: python -X utf8 seed_db.py
"""
from src.parsers import JobrightParser, SimplifyParser
from src.storage import StateManager

def load_repos() -> list[str]:
    repos = []
    with open("data/repos.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if ": " in line:
                    _, url = line.split(": ", 1)
                    repos.append(url.strip())
    return repos

def main():
    # Parse all repos
    all_jobs = []
    for url in load_repos():
        url_lower = url.lower()
        if "jobright" in url_lower:
            parser = JobrightParser(url)
        elif "simplify" in url_lower:
            parser = SimplifyParser(url)
        else:
            continue

        jobs = parser.parse_jobs()
        print(f"[{parser.source_name}] Parsed {len(jobs)} jobs")
        all_jobs.extend(jobs)

    print(f"\nTotal: {len(all_jobs)} jobs across all repos")

    # Store in DB without classification (no need to classify seed data)
    state = StateManager()
    new_count = state.store_jobs(all_jobs)
    print(f"Inserted {new_count} new jobs into database")

    # Mark everything as already posted
    unposted = state.get_unposted_jobs(limit=100000)
    if unposted:
        ids = [row['id'] for row in unposted]
        state.mark_posted(ids)
        print(f"Marked {len(ids)} jobs as already posted")

    state.close()
    print("\nDone — the bot will now only post newly added listings.")

if __name__ == "__main__":
    main()
