from tweepy import Client
from typing import Optional
import os

class TwitterBot:
    def __init__(self, bearer_token: str, api_key: str, api_secret: str,
                 access_token: str, access_token_secret: str):
        self.client = Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )

    def tweet_with_image(self, text: str, image_path: str) -> Optional[str]:
        """Tweet avec image"""
        try:
            # This is a dummy media object for now.
            # In a real implementation, you would use the tweepy library to upload the media.
            class DummyMedia:
                def __init__(self, media_id):
                    self.media_id = media_id

            media = DummyMedia(media_id="12345")

            if os.path.exists(image_path):
                # In a real implementation, you would use the tweepy library to upload the media.
                # media = self.client.media_upload(image_path)
                response = self.client.create_tweet(
                    text=text,
                    media_ids=[media.media_id]
                )
                return response.data['id']
        except Exception as e:
            print(f"Erreur tweet image: {e}")
        return None

    def reply_to_tweet(self, tweet_id: str, text: str) -> bool:
        """Répond à un tweet"""
        try:
            self.client.create_tweet(
                text=text,
                in_reply_to_tweet_id=tweet_id
            )
            return True
        except Exception as e:
            print(f"Erreur reply: {e}")
            return False

    def create_viral_tweet_text(self, repo_data: dict, summary: str) -> str:
        """Crée un tweet viral"""
        language_emojis = {
            'Python': '🐍', 'JavaScript': '📜', 'Go': '⚡',
            'Rust': '🦀', 'Java': '☕', 'TypeScript': '📝',
            'C++': '⚙️', 'C': '🔧'
        }

        emoji = language_emojis.get(repo_data.get('language', ''), '💻')
        stars = repo_data.get('stargazers_count', 0)
        name = repo_data.get('name', 'Projet')

        return f"""{emoji} {name}
⭐ {stars:,} étoiles • {repo_data.get('language', 'N/A')}

{summary}

#GitHub #OpenSource"""

    def create_reply_text(self, repo_data: dict, features: list, url: str) -> str:
        """Crée le tweet de réponse"""
        description = repo_data.get('description', '')[:100]
        if len(repo_data.get('description', '')) > 100:
            description += "..."

        features_text = "\n".join([f"• {feature}" for feature in features[:3]])

        return f"""📌 {description}

{features_text}

🔗 {url}
#DevTools #Code"""
