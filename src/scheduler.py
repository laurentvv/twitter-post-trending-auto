import schedule
import time
import random
from datetime import datetime
from src.github_analyzer import GitHubAnalyzer
from src.screenshot import ScreenshotCapturer
from src.ai_summarizer import AISummarizer
from src.twitter_bot import TwitterBot
from config.settings import TWEET_INTERVAL_HOURS
import logging
import requests

class TweetScheduler:
    def __init__(self):
        self.github_analyzer = GitHubAnalyzer()
        self.screenshot_capturer = ScreenshotCapturer()
        self.ai_summarizer = AISummarizer()

        # Setup logging
        logging.basicConfig(
            filename='logs/app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setup_twitter_bot(self, twitter_config):
        """Initialise le bot Twitter"""
        self.twitter_bot = TwitterBot(
            bearer_token=twitter_config['bearer_token'],
            api_key=twitter_config['api_key'],
            api_secret=twitter_config['api_secret'],
            access_token=twitter_config['access_token'],
            access_token_secret=twitter_config['access_token_secret']
        )

    def tweet_trending_repo(self):
        """Tweet un dépôt tendance aléatoire"""
        try:
            # Récupérer les dépôts tendance
            trending_repos = self.github_analyzer.get_trending_repositories()

            if not trending_repos:
                logging.warning("Aucun dépôt tendance trouvé")
                return

            # Choisir un dépôt aléatoire
            repo = random.choice(trending_repos)

            # Capture d'écran
            screenshot_path = self.screenshot_capturer.capture_repository(
                repo['html_url'],
                f"{repo['name']}_{int(time.time())}.png"
            )

            # Télécharger et résumer le README
            readme_content = self._download_readme(repo['html_url'])
            if readme_content:
                summary = self.ai_summarizer.summarize_readme(readme_content)
                features = self.ai_summarizer.extract_key_features(readme_content)
            else:
                summary = "Découvrez ce projet GitHub intéressant !"
                features = ["Fonctionnalité principale"]

            # Créer et envoyer les tweets
            viral_text = self.twitter_bot.create_viral_tweet_text(repo, summary)
            reply_text = self.twitter_bot.create_reply_text(repo, features, repo['html_url'])

            tweet_id = self.twitter_bot.tweet_with_image(viral_text, screenshot_path)

            if tweet_id:
                self.twitter_bot.reply_to_tweet(tweet_id, reply_text)
                logging.info(f"Tweet envoyé pour {repo['name']}")
            else:
                logging.error(f"Échec tweet pour {repo['name']}")

        except Exception as e:
            logging.error(f"Erreur tweet_trending_repo: {e}")

    def _download_readme(self, repo_url: str) -> str:
        """Télécharge le README"""
        for branch in ["main", "master"]:
            try:
                raw_url = repo_url.replace("github.com", "raw.githubusercontent.com") + f"/{branch}/README.md"
                response = requests.get(raw_url)
                if response.status_code == 200:
                    return response.text
            except:
                continue
        return ""

    def start_scheduler(self):
        """Démarre la planification"""
        # Tweet immédiat
        self.tweet_trending_repo()

        # Planifier les tweets suivants
        schedule.every(TWEET_INTERVAL_HOURS).hours.do(self.tweet_trending_repo)

        print(f"📅 Planification activée - Tweet toutes les {TWEET_INTERVAL_HOURS} heures")
        print("🚀 Premier tweet envoyé !")

        while True:
            schedule.run_pending()
            time.sleep(60)  # Vérifier chaque minute
