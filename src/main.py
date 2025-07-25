from src.scheduler import TweetScheduler
from config.settings import *
import os

def main():
    # Créer les dossiers nécessaires
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Initialiser le scheduler
    scheduler = TweetScheduler()

    # Configuration Twitter
    twitter_config = {
        'bearer_token': TWITTER_BEARER_TOKEN,
        'api_key': TWITTER_API_KEY,
        'api_secret': TWITTER_API_SECRET,
        'access_token': TWITTER_ACCESS_TOKEN,
        'access_token_secret': TWITTER_ACCESS_TOKEN_SECRET
    }

    scheduler.setup_twitter_bot(twitter_config)

    # Démarrer la planification
    print("🤖 GitHub Tweet Bot démarré !")
    print("🔍 Recherche des dépôts tendance...")
    scheduler.start_scheduler()

if __name__ == "__main__":
    main()
