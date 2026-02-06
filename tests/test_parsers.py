"""Test script for job parsers"""
from src.parsers import JobrightParser, SimplifyParser


def test_jobright_parser():
    """Test the Jobright parser with a real repo"""
    url = "https://raw.githubusercontent.com/jobright-ai/2026-Software-Engineer-New-Grad/refs/heads/master/README.md"
    parser = JobrightParser(url)

    print("Testing JobrightParser...")
    jobs = parser.parse_jobs()

    print(f"Found {len(jobs)} jobs")

    if jobs:
        print("\nFirst 3 jobs:")
        for job in jobs[:3]:
            print(f"  - {job.title} @ {job.company}")
            print(f"    Location: {job.location}")
            print(f"    Link: {job.apply_link[:50]}...")
            print()

    return len(jobs) > 0


def test_simplify_parser():
    """Test the Simplify parser with a real repo"""
    url = "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/refs/heads/dev/README.md"
    parser = SimplifyParser(url)

    print("Testing SimplifyParser...")
    jobs = parser.parse_jobs()

    print(f"Found {len(jobs)} jobs")

    if jobs:
        print("\nFirst 3 jobs:")
        for job in jobs[:3]:
            print(f"  - {job.title} @ {job.company}")

    return len(jobs) > 0


if __name__ == "__main__":
    print("=" * 50)
    test_jobright_parser()
    print("=" * 50)
    test_simplify_parser()
    print("=" * 50)
