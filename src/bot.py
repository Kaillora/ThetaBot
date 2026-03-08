"""Discord bot for posting job listings"""
import discord
from discord.ext import commands
import asyncio
from datetime import datetime

from .config import TOKEN, CATEGORY_CHANNEL_IDS, CATEGORY_ROLE_IDS, CHECK_INTERVAL_HOURS
from .storage import StateManager
from .parsers import JobrightParser, SimplifyParser, Job
from .classifier import MajorClassifier


# Load repo URLs from data file
def load_repos() -> list[str]:
    """Load repository URLs from data/repos.txt"""
    repos = []
    with open("data/repos.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Format: name: https://...
                # Split on first ": " to avoid breaking on "https:"
                if ": " in line:
                    _, url = line.split(": ", 1)
                    repos.append(url.strip())
    return repos


# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# State manager for tracking seen jobs
state = StateManager()

# Job classifier (graceful degradation — bot works without it)
try:
    classifier = MajorClassifier()
    print("Classifier initialized successfully")
except Exception as e:
    classifier = None
    print(f"Classifier unavailable, jobs will post without categories: {e}")


def get_parsers() -> list:
    """Create parser instances for all repos"""
    parsers = []
    for url in load_repos():
        url_lower = url.lower()
        if "jobright" in url_lower:
            parsers.append(JobrightParser(url))
        elif "simplify" in url_lower:
            parsers.append(SimplifyParser(url))
    return parsers



def create_job_embed_from_row(row: dict) -> discord.Embed:
    """Create a Discord embed from a database row dict"""
    embed = discord.Embed(
        title=f"{row['title']} @ {row['company']}",
        url=row['apply_link'],
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Location", value=row['location'], inline=True)
    embed.add_field(name="Posted", value=row['date_posted'], inline=True)
    if row.get('category'):
        embed.add_field(name="Category", value=row['category'], inline=True)
    embed.description = f"**[Click here to Apply]({row['apply_link']})**"
    embed.set_footer(text=f"Theta Bot | Source: {row['source']}")
    return embed


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    await check_jobs()
    await bot.close()


async def check_jobs():
    """Scheduled task to check for new jobs"""
    print("Checking for new jobs...")
    category_channels = {
        cat: bot.get_channel(cid)
        for cat, cid in CATEGORY_CHANNEL_IDS.items()
        if cid
    }

    # 1. Fetch jobs from all parsers
    all_jobs: list[Job] = []
    for parser in get_parsers():
        jobs = parser.parse_jobs()
        all_jobs.extend(jobs)
        print(f"[{parser.source_name}] Found {len(jobs)} jobs")

    # 2. Store all jobs in database first (duplicates are skipped)
    new_count = state.store_jobs(all_jobs)
    print(f"Stored {new_count} new jobs in database")

    # 3. Get unposted jobs from DB and classify only those
    unposted = state.get_unposted_jobs(100, max_age_hours=CHECK_INTERVAL_HOURS + 1)
    classified_count = 0

    if classifier and unposted:
        uncategorized = [r for r in unposted if not r.get('category')]
        if uncategorized:
            try:
                # Build lightweight Job objects just for classification
                jobs_to_classify = [
                    Job(company=r['company'], title=r['title'], location=r['location'],
                        apply_link=r['apply_link'], date_posted=r['date_posted'], source=r['source'])
                    for r in uncategorized
                ]
                await asyncio.to_thread(classifier.classify_jobs, jobs_to_classify)

                # Write categories back to DB
                for row, job in zip(uncategorized, jobs_to_classify):
                    if job.category:
                        state.update_category(row['id'], job.category)
                        row['category'] = job.category
                        classified_count += 1

                print(f"Classified {classified_count} / {len(uncategorized)} unposted jobs")
            except Exception as e:
                print(f"[Classifier] Classification failed: {e}")

    # 4. Post unposted jobs to Discord (skip General Engineering)
    posted_count = 0

    if unposted:
        posted_ids = []
        skipped = 0

        for row in unposted:
            category = row.get('category') or 'General Engineering'
            posted_ids.append(row['id'])

            if category == 'General Engineering':
                skipped += 1
                continue

            embed = create_job_embed_from_row(row)

            ch = category_channels.get(category)
            if ch:
                role_id = CATEGORY_ROLE_IDS.get(category)
                msg = f"<@&{role_id}> New **{category}** opportunity!" if role_id else f"New **{category}** opportunity!"
                await ch.send(content=msg, embed=embed)

            posted_count += 1
            await asyncio.sleep(0.25)  # Rate limit protection

        state.mark_posted(posted_ids)
        print(f"Posted {posted_count} jobs, silently skipped {skipped} General Engineering")
    else:
        print("No new jobs to post.")

    # 5. Log cycle metrics
    state.log_cycle(
        jobs_scraped=len(all_jobs),
        jobs_new=new_count,
        jobs_classified=classified_count,
        jobs_posted=posted_count,
    )


@bot.command()
async def jobs(ctx):
    """Manually trigger a job check"""
    await check_jobs()
    await ctx.send("Checked for new jobs!")


@bot.command()
async def metrics(ctx):
    """Show bot performance metrics"""
    m = state.get_metrics_summary()
    if not m or not m['total_cycles']:
        await ctx.send("No metrics recorded yet.")
        return

    embed = discord.Embed(title="ThetaBot Metrics", color=0x00ff00)
    embed.add_field(name="Total Cycles", value=str(m['total_cycles']), inline=True)
    embed.add_field(name="Jobs Scraped", value=str(m['total_scraped']), inline=True)
    embed.add_field(name="New Jobs Found", value=str(m['total_new']), inline=True)
    embed.add_field(name="Jobs Classified", value=str(m['total_classified']), inline=True)
    embed.add_field(name="Jobs Posted", value=str(m['total_posted']), inline=True)
    embed.add_field(name="Running Since", value=str(m['first_cycle'].strftime('%Y-%m-%d')), inline=True)
    await ctx.send(embed=embed)


def run():
    """Start the bot"""
    try:
        bot.run(TOKEN)
    finally:
        state.close()