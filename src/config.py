"""Configuration settings for ThetaBot"""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord settings
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '1466710750390255648'))

# Database settings
DATABASE_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': int(os.getenv('DATABASE_PORT', '5432')),
    'dbname': os.getenv('DATABASE_NAME', 'thetabot'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', ''),
}

# Scraping settings
CHECK_INTERVAL_HOURS = 2  # How often to check for new jobs

# Hugging Face classification settings
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
CLASSIFICATION_CONFIDENCE_THRESHOLD = 0.5
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
