# ThetaBot

Discord bot that scrapes GitHub-hosted job listing repos and posts newly listed engineering internship and new grad roles to a configured channel with @role pings.

**Stack:** Python 3.8+, discord.py, PostgreSQL, HuggingFace Inference API

---

## Features

- Scrapes 6 GitHub-hosted job listing repos (Jobright and SimplifyJobs)
- Deduplicates jobs via PostgreSQL so each listing is posted at most once
- Classifies jobs by engineering discipline (CS, EE, ME, CE, DS, Cybersecurity) using zero-shot NLP
- Posts job embeds to a Discord channel with @role pings per category
- Silently skips jobs that fall under General Engineering (no relevant role ping)
- Tracks cycle metrics (scraped, new, classified, posted counts)

---

## Architecture

```
main.py
  └── bot.py
        ├── parsers/
        │     ├── JobrightParser   (markdown pipe tables)
        │     └── SimplifyParser  (HTML <tr>/<td> tables)
        ├── classifier/
        │     └── MajorClassifier (HuggingFace NLI, keyword fast-path)
        ├── storage/
        │     └── StateManager    (PostgreSQL via psycopg2)
        └── Discord channel
```

Parsers use a **Template Method** pattern: `BaseParser.parse_jobs()` drives the loop, `extract_rows()` handles table formatting differences, and `parse_row()` is implemented per source. The classifier uses a keyword-map fast path before falling back to a HuggingFace API call. 

---

## Prerequisites

- Python 3.10+
- PostgreSQL 18
- Discord bot token with **Send Messages**, **Embed Links**, and **Mention Roles** permissions
- HuggingFace Inference API token (only posts job listings, no classification without it)

---

## Setup & Installation

**1. Clone the repo**
```bash
git clone <repo-url>
cd ThetaBot
```

**2. Create a virtual environment and install dependencies**
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Create a `.env` file** in the root of the project, and create all the necessary [Environment Variables](#environment-variables). See the table below for all options available.

**4. Create the PostgreSQL database**
```sql
CREATE DATABASE thetabot;
```

**5. Seed the database** (marks all currently listed jobs as already seen so the bot does not spam on first run)
```bash
python -X utf8 seed_db.py
```

**6. Run the bot**
```bash
python -X utf8 main.py
```

> **Note:** `python -X utf8` is required on Windows to handle the `↳` continuation character used in Jobright tables. This is to prevent potentioal job listings from being skipped.

The bot checks for new jobs every 2 hours automatically through GitHub Actions workflow.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DISCORD_TOKEN` | Yes | — | Discord bot authentication token |
| `CHANNEL_ID` | Yes | — | ID of the Discord channel where jobs are posted |
| `DATABASE_PASSWORD` | Yes | — | PostgreSQL user password |
| `DATABASE_HOST` | No | `localhost` | PostgreSQL host |
| `DATABASE_PORT` | No | `5432` | PostgreSQL port |
| `DATABASE_NAME` | No | — | PostgreSQL database name |
| `DATABASE_USER` | No | — | PostgreSQL username |
| `HUGGINGFACE_TOKEN` | No | — | HuggingFace Inference API token |
| `CS_ROLE_ID` | No | — | Discord role ID to ping for Computer Science jobs |
| `EE_ROLE_ID` | No | — | Discord role ID to ping for Electrical Engineering jobs |
| `ME_ROLE_ID` | No | — | Discord role ID to ping for Mechanical Engineering jobs |
| `CE_ROLE_ID` | No | — | Discord role ID to ping for Civil Engineering jobs |
| `DS_ROLE_ID` | No | — | Discord role ID to ping for Data Science jobs |
| `CYBER_ROLE_ID` | No | — | Discord role ID to ping for Cybersecurity jobs |

> **Note:** I used `Neon` as my external PostgreSQL database to host since the free tier is more than sufficient for the job postings. `DATABASE_USER` and `DATABASE_USER` varies on setting the database up locally vs. externally.

---

## Discord Bot Setup

1. Create an application at [discord.com/developers](https://discord.com/developers/applications) and add a Bot.
2. Under **OAuth2 → URL Generator**, select the `bot` scope and the following permissions:
   - Send Messages
   - Embed Links
   - Mention Everyone (required for @role pings)
3. Enable the following **Privileged Gateway Intents**: Message Content Intent.
4. Copy the bot token into `.env` as `DISCORD_TOKEN`.
5. Right-click the target channel in Discord → Copy ID → set as `CHANNEL_ID` in `.env`.
6. Right-click each role in Discord → Copy ID → set the corresponding `*_ROLE_ID` values in `.env`.

---

## Data Sources

| Name | Repo |
|---|---|
| SimplifyJobs Summer 2026 Internships | [SimplifyJobs/Summer2026-Internships](https://github.com/SimplifyJobs/Summer2026-Internships) |
| SimplifyJobs New Grad Positions | [SimplifyJobs/New-Grad-Positions](https://github.com/SimplifyJobs/New-Grad-Positions) |
| Jobright 2026 SWE Internship | [jobright-ai/2026-Software-Engineer-Internship](https://github.com/jobright-ai/2026-Software-Engineer-Internship) |
| Jobright 2026 SWE New Grad | [jobright-ai/2026-Software-Engineer-New-Grad](https://github.com/jobright-ai/2026-Software-Engineer-New-Grad) |
| Jobright 2026 Engineering Internship | [jobright-ai/2026-Engineer-Internship](https://github.com/jobright-ai/2026-Engineer-Internship) |
| Jobright 2026 Engineering New Grad | [jobright-ai/2026-Engineering-New-Grad](https://github.com/jobright-ai/2026-Engineering-New-Grad) |

Repo URLs are configured in `data/repos.txt` and can be updated without code changes. The Parses are created to handle the formatting of the Simplify and Jobright repositories.

---

## Project Structure

```
ThetaBot/
├── main.py                      # Entry point
├── seed_db.py                   # Filters out the DB to prevent spam on first run
├── data/
│   └── repos.txt                # Job listing repository URLs
└── src/
    ├── bot.py                   # Discord bot and tasks
    ├── config.py                # Loading environment variables
    ├── parsers/
    │   ├── base.py              # BaseParser (Template)
    │   ├── jobright.py          # Jobright Markdown table parser
    │   └── simplify.py          # Simplify HTML table parser
    ├── classifier/
    │   └── major_classifier.py  # HuggingFace NLI + keyword fast-path
    └── storage/
        └── database.py          # PostgreSQL state manager
```
