jobs = []
seen_jobs = set()

for job in jobs:
    cleaned_company = job['company'].strip()
    cleaned_title = job['title'].strip()
    cleaned_location = job['location'].strip()