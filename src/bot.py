"""Discord bot for posting job listings"""
import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime

from .config import TOKEN, CHANNEL_ID, CHECK_INTERVAL_HOURS
from .storage import StateManager
from .parsers import JobrightParser, Job


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
state = StateManager("data/job_state.json")


def get_parsers() -> list:
    """Create parser instances for all repos"""
    parsers = []
    for url in load_repos():
        # Determine parser type based on URL
        if "jobright" in url:
            parsers.append(JobrightParser(url))
        # Add SimplifyParser when implemented:
        # elif "simplify" in url:
        #     parsers.append(SimplifyParser(url))
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

    # Filter out seen jobs
    new_jobs = [job for job in all_jobs if not state.is_seen(job.unique_id)]

    if new_jobs:
        print(f"Found {len(new_jobs)} new jobs. Posting...")

        for job in new_jobs[:50]:  # Limit to prevent spam
            embed = await create_job_embed(job)
            await channel.send(embed=embed)
            await asyncio.sleep(1)  # Rate limit protection

        # Mark jobs as seen
        state.mark_seen([job.unique_id for job in new_jobs])
    else:
        print("No new jobs found.")


@bot.command()
async def jobs(ctx):
    """Manually trigger a job check"""
    await check_jobs()
    await ctx.send("Checked for new jobs!")


def run():
    """Start the bot"""
    bot.run(TOKEN)
