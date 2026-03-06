"""Configuration settings for ThetaBot"""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord settings
TOKEN = os.getenv('DISCORD_TOKEN')
CATEGORY_CHANNEL_IDS = {
    'Computer Science':       int(os.getenv('CS_CHANNEL_ID') or 0) or None,
    'Electrical Engineering': int(os.getenv('EE_CHANNEL_ID') or 0) or None,
    'Mechanical Engineering': int(os.getenv('ME_CHANNEL_ID') or 0) or None,
    'Civil Engineering':      int(os.getenv('CE_CHANNEL_ID') or 0) or None,
    'Data Science':           int(os.getenv('DS_CHANNEL_ID') or 0) or None,
    'Cybersecurity':          int(os.getenv('CYBER_CHANNEL_ID') or 0) or None,
}

# Database settings
DATABASE_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT') or '5432'),
    'dbname': os.getenv('DATABASE_NAME', 'thetabot'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', ''),
    'sslmode': os.getenv('DATABASE_SSLMODE', 'prefer'),
}

# Scraping settings
CHECK_INTERVAL_HOURS = 2  # How often to check for new jobs

# OpenAI classification settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CLASSIFICATION_LABELS = [
    'Computer Science',
    'Electrical Engineering',
    'Mechanical Engineering',
    'Civil Engineering',
    'Data Science',
    'Cybersecurity',
]

# Map classification labels to Discord role IDs for pinging
# Set these in .env as CS_ROLE_ID=123456789, EE_ROLE_ID=123456789, etc.
CATEGORY_ROLE_IDS = {
    'Computer Science': os.getenv('CS_ROLE_ID'),
    'Electrical Engineering': os.getenv('EE_ROLE_ID'),
    'Mechanical Engineering': os.getenv('ME_ROLE_ID'),
    'Civil Engineering': os.getenv('CE_ROLE_ID'),
    'Data Science': os.getenv('DS_ROLE_ID'),
    'Cybersecurity': os.getenv('CYBER_ROLE_ID'),
    'General Engineering': os.getenv('GENERAL_ROLE_ID'),
}
