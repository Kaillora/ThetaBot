"""Configuration settings for ThetaBot"""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord settings
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '1466710750390255648'))

# Scraping settings
CHECK_INTERVAL_HOURS = 2  # How often to check for new jobs
