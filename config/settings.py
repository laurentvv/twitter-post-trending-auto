import os
from dotenv import load_dotenv

load_dotenv()

# Twitter API
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Ollama IA
OLLAMA_MODEL = "qwen3:14b"
OLLAMA_HOST = "http://localhost:11434"

# Chemins
SCREENSHOT_DIR = "screenshots/"
DATA_DIR = "data/"
LOGS_DIR = "logs/"

# Configuration
TWEET_INTERVAL_HOURS = 4  # Tweet toutes les 4 heures
MAX_TRENDING_REPOS = 10   # Nombre max de dépôts tendance
