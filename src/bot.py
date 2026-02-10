"""Discord bot for posting job listings"""
import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime

from .config import TOKEN, CHANNEL_ID, CHECK_INTERVAL_HOURS
from .storage import StateManager
from .parsers import JobrightParser, SimplifyParser, Job


# Load repo URLs from data file
def load_repos() -> list[str]:
    """Load repository URLs from data/repos.txt"""
    repos = []
    with open("data/repos.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                # Format: name: url
                if ":" in line:
                    _, url = line.split(":", 1)
                    repos.append(url.strip())
    return repos


# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# State manager for tracking seen jobs
state = StateManager()


def get_parsers() -> list:
    """Create parser instances for all repos"""
    parsers = []
    for url in load_repos():
        if "jobright" in url:
            parsers.append(JobrightParser(url))
        elif "simplify" in url:
            parsers.append(SimplifyParser(url))
    return parsers


async def create_job_embed(job: Job) -> discord.Embed:
    """Create a Discord embed for a job listing"""
    embed = discord.Embed(
        title=f"{job.title} @ {job.company}",
        url=job.apply_link,
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Location", value=job.location, inline=True)
    embed.add_field(name="Posted", value=job.date_posted, inline=True)
    embed.description = f"**[Click here to Apply]({job.apply_link})**"
    embed.set_footer(text=f"Theta Bot | Source: {job.source}")
    return embed


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
    embed.description = f"**[Click here to Apply]({row['apply_link']})**"
    embed.set_footer(text=f"Theta Bot | Source: {row['source']}")
    return embed


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    check_jobs.start()


@tasks.loop(hours=CHECK_INTERVAL_HOURS)
async def check_jobs():
    """Scheduled task to check for new jobs"""
    print("Checking for new jobs...")
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Channel not found!")
        return

    # Fetch jobs from all parsers
    all_jobs: list[Job] = []
    for parser in get_parsers():
        jobs = parser.parse_jobs()
        all_jobs.extend(jobs)
        print(f"[{parser.source_name}] Found {len(jobs)} jobs")

    # Store all jobs in database (duplicates are skipped)
    new_count = state.store_jobs(all_jobs)
    print(f"Stored {new_count} new jobs in database")

    # Get unposted jobs and send to Discord
    unposted = state.get_unposted_jobs(50)

    if unposted:
        print(f"Posting {len(unposted)} jobs to Discord...")
        posted_ids = []

        for row in unposted:
            embed = create_job_embed_from_row(row)
            await channel.send(embed=embed)
            posted_ids.append(row['id'])
            await asyncio.sleep(1)  # Rate limit protection

        state.mark_posted(posted_ids)
        print(f"Posted and marked {len(posted_ids)} jobs")
    else:
        print("No new jobs to post.")


@bot.command()
async def jobs(ctx):
    """Manually trigger a job check"""
    await check_jobs()
    await ctx.send("Checked for new jobs!")


def run():
    """Start the bot"""
    try:
        bot.run(TOKEN)
    finally:
        state.close()
