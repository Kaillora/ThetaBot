import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import requests
import re
import json
from datetime import datetime
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')          
CHANNEL_ID = 1466710750390255648      

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Simple persistent storage (for seen jobs)
STATE_FILE = 'job_state.json'

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"last_checked": None, "seen": []}  # seen = list of "Company|Title|Date" strings

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    check_jobs.start()  # Start the scheduled task

@tasks.loop(hours=4)  # Check every 4 hours
async def check_jobs():
    print("Checking for new jobs...")
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("Channel not found!")
        return

    state = load_state()

    # Fetch raw README
    url = "https://raw.githubusercontent.com/jobright-ai/2026-Software-Engineer-New-Grad/master/README.md"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text
    except Exception as e:
        print(f"Failed to fetch README: {e}")
        return

    # Very basic parsing: find the Daily Job List table
    lines = content.splitlines()
    table_start = False
    jobs = []
    current_job = {}
    
    link_pattern = re.compile(r'\((https?://.*?)\)')

    for line in lines:
        line = line.strip()
        
        # Skip headers and separators
        if not line.startswith("|") or "---" in line or "Company" in line:
            continue
            
        # Split by pipe, but handle the empty start/end of the line
        parts = [p.strip() for p in line.split("|")]
        # Remove empty strings caused by leading/trailing pipes
        parts = [p for p in parts if p]

        # Ensure we have enough columns (Company, Title, Location, Link, Date)
        if len(parts) < 5:
            continue

        company = parts[0]
        title = parts[1]
        location = parts[2]
        link_md = parts[3] # This looks like "[Apply](https://...)"
        date_posted = parts[4]

        # Extract the actual URL
        url_match = link_pattern.search(link_md)
        apply_link = url_match.group(1) if url_match else "https://github.com/jobright-ai/2026-Software-Engineer-New-Grad"

        # Create a unique ID (Prevent duplicates)
        job_id = f"{company}|{title}|{location}" # Better than date, which changes

        if job_id not in state["seen"]:
            jobs.append({
                "company": company,
                "title": title,
                "location": location,
                "link": apply_link,
                "date": date_posted,
                "id": job_id
            })

    # 2. Improved Posting Logic (With Clickable Links)
    if jobs:
        print(f"Found {len(jobs)} new jobs. Posting the first 10...")
        
        for job in jobs[:50]: # Keep the limit for safety during testing
            embed = discord.Embed(
                title=f"{job['title']} @ {job['company']}", # Combine for cleaner title
                url=job['link'], # THIS makes the title clickable!
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="📍 Location", value=job["location"], inline=True)
            embed.add_field(name="📅 Posted", value=job["date"], inline=True)
            
            # Add a clear "Apply Now" button in the text
            embed.description = f"**[👉 Click here to Apply]({job['link']})**"
            
            embed.set_footer(text="Theta Bot • 2026 Internships")
            
            await channel.send(embed=embed)
            await asyncio.sleep(1) # Sleep 1s between posts to avoid Discord Rate Limits

        # Update state
        new_ids = [j["id"] for j in jobs]
        state["seen"].extend(new_ids)
        state["last_checked"] = datetime.utcnow().isoformat()
        save_state(state)
    else:
        print("No new jobs found.")

@bot.command()
async def jobs(ctx):
    """Manually trigger a check"""
    await check_jobs()
    await ctx.send("Checked for new jobs!")

bot.run(TOKEN)