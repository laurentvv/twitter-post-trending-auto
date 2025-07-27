"""Modern Twitter service using Tweepy v4 and Twitter API v2 with Firefox fallback."""
import tweepy
from typing import Optional, Dict, Any
from pathlib import Path

from ..core.config import settings
from ..core.logger import logger, log_step
from ..core.firefox_config import firefox_config


class TwitterService:
    """Modern Twitter service with API v2 and Firefox fallback."""
    
    def __init__(self):
        self.client: Optional[tweepy.Client] = None
        self._setup_client()
        self.firefox_fallback_enabled = firefox_config.is_enabled()
    
    def _has_oauth1_credentials(self) -> bool:
        """Check if OAuth 1.0a credentials are available."""
        return bool(
            settings.twitter_api_key and settings.twitter_api_key != 'your_api_key_here' and
            settings.twitter_api_secret and settings.twitter_api_secret != 'your_api_secret_here' and
            settings.twitter_access_token and settings.twitter_access_token != 'your_access_token_here' and
            settings.twitter_access_token_secret and settings.twitter_access_token_secret != 'your_access_token_secret_here'
        )
    
    def _setup_client(self) -> None:
        """Setup Twitter API v2 client."""
        logger.info("Setting up Twitter client", **log_step("twitter_setup"))
        
        # Try OAuth 1.0a first (for posting)
        if self._has_oauth1_credentials():
            self.client = tweepy.Client(
                consumer_key=settings.twitter_api_key,
                consumer_secret=settings.twitter_api_secret,
                access_token=settings.twitter_access_token,
                access_token_secret=settings.twitter_access_token_secret,
                bearer_token=settings.twitter_bearer_token,
                wait_on_rate_limit=True
            )
            logger.info("Twitter client ready with OAuth 1.0a", **log_step("twitter_ready"))
            return
        
        # Fallback to Bearer Token
        if settings.twitter_bearer_token:
            self.client = tweepy.Client(
                bearer_token=settings.twitter_bearer_token,
                wait_on_rate_limit=True
            )
            logger.info("Twitter client ready with Bearer Token", **log_step("twitter_ready"))
        else:
            raise ValueError("Twitter credentials required")
    
    def _is_rate_limit_error(self, error) -> bool:
        """Détecte si l'erreur est un rate limit."""
        rate_limit_indicators = [
            "Rate limit exceeded",
            "Too Many Requests", 
            "429",
            "wait_on_rate_limit",
            "rate_limit",
            "quota"
        ]
        error_str = str(error).lower()
        return any(indicator.lower() in error_str for indicator in rate_limit_indicators)
    
    def create_tweet(self, text: str, media_path: Optional[str] = None) -> Optional[str]:
        """
        Create a tweet with optional media (with 3 retry attempts and Firefox fallback).
        
        Args:
            text: Tweet text content
            media_path: Optional path to media file
            
        Returns:
            Tweet ID if successful, None otherwise
        """
        for attempt in range(3):
            try:
                logger.info(
                    "Creating tweet",
                    **log_step("tweet_create", text_length=len(text), has_media=bool(media_path), attempt=attempt+1)
                )
                
                media_ids = None
                if media_path and Path(media_path).exists() and self._has_oauth1_credentials():
                    try:
                        # Use OAuth 1.0a API for media upload
                        auth = tweepy.OAuth1UserHandler(
                            consumer_key=settings.twitter_api_key,
                            consumer_secret=settings.twitter_api_secret,
                            access_token=settings.twitter_access_token,
                            access_token_secret=settings.twitter_access_token_secret
                        )
                        api = tweepy.API(auth)
                        
                        media = api.media_upload(media_path)
                        media_ids = [media.media_id]
                        
                        logger.info(
                            "Media uploaded successfully",
                            **log_step("media_upload_success", media_id=media.media_id)
                        )
                    except Exception as e:
                        logger.warning(
                            "Media upload failed, posting without image",
                            **log_step("media_upload_error", error=str(e))
                        )
                
                response = self.client.create_tweet(text=text, media_ids=media_ids)
                
                if response.data:
                    tweet_id = response.data['id']
                    logger.info(
                        "Tweet created successfully",
                        **log_step("tweet_success", tweet_id=tweet_id, attempt=attempt+1)
                    )
                    return tweet_id
                
            except Exception as e:
                # Vérifier si c'est un rate limit et si Firefox est disponible
                if self._is_rate_limit_error(e) and self.firefox_fallback_enabled and attempt == 2:
                    logger.warning(
                        "Rate limit détecté, tentative avec Firefox fallback",
                        **log_step("rate_limit_detected", error=str(e))
                    )
                    return self._try_firefox_fallback(text, media_path)
                
                logger.warning(
                    f"Tweet creation attempt {attempt+1} failed",
                    **log_step("tweet_retry", error=str(e), attempt=attempt+1)
                )
                if attempt == 2:  # Last attempt
                    logger.error(
                        "Tweet creation failed after 3 attempts",
                        **log_step("tweet_error", error=str(e))
                    )
        
        return None
    
    def _try_firefox_fallback(self, text: str, media_path: Optional[str] = None) -> Optional[str]:
        """Tente de poster via Firefox en cas de rate limit."""
        try:
            logger.info("Tentative de post via Firefox fallback", 
                       **log_step("firefox_fallback_start"))
            
            from .firefox_twitter_service import FirefoxTwitterService
            
            with FirefoxTwitterService() as firefox_service:
                # Firefox peut maintenant gérer les screenshots
                if media_path and Path(media_path).exists():
                    logger.info(f"Utilisation du screenshot avec Firefox: {media_path}",
                               **log_step("firefox_with_screenshot"))
                
                result = firefox_service.post_tweet(text, screenshot_path=media_path)
                
                if result:
                    logger.info("Post Firefox réussi", 
                               **log_step("firefox_fallback_success", method="firefox", has_screenshot=bool(media_path)))
                    return result
                else:
                    logger.error("Post Firefox échoué", 
                               **log_step("firefox_fallback_error"))
                    return None
                    
        except Exception as e:
            logger.error(f"Erreur lors du fallback Firefox: {e}", 
                        **log_step("firefox_fallback_error", error=str(e)))
            return None
    
    def reply_to_tweet(self, tweet_id: str, text: str) -> Optional[str]:
        """
        Reply to a tweet (with 3 retry attempts and Firefox fallback).
        
        Args:
            tweet_id: ID of tweet to reply to
            text: Reply text
            
        Returns:
            Reply tweet ID if successful, None otherwise
        """
        for attempt in range(3):
            try:
                logger.info(
                    "Creating reply",
                    **log_step("reply_create", tweet_id=tweet_id, text_length=len(text), attempt=attempt+1)
                )
                
                response = self.client.create_tweet(
                    text=text,
                    in_reply_to_tweet_id=tweet_id
                )
                
                if response.data:
                    reply_id = response.data['id']
                    logger.info(
                        "Reply created successfully",
                        **log_step("reply_success", reply_id=reply_id, attempt=attempt+1)
                    )
                    return reply_id
                    
            except Exception as e:
                # Vérifier si c'est un rate limit et si Firefox est disponible
                if self._is_rate_limit_error(e) and self.firefox_fallback_enabled and attempt == 2:
                    logger.warning(
                        "Rate limit détecté pour la réponse, tentative avec Firefox fallback",
                        **log_step("rate_limit_detected_reply", error=str(e))
                    )
                    return self._try_firefox_reply_fallback(text)
                
                logger.warning(
                    f"Reply creation attempt {attempt+1} failed",
                    **log_step("reply_retry", error=str(e), attempt=attempt+1)
                )
                if attempt == 2:  # Last attempt
                    logger.error(
                        "Reply creation failed after 3 attempts",
                        **log_step("reply_error", error=str(e))
                    )
        
        return None
    
    def _try_firefox_reply_fallback(self, text: str) -> Optional[str]:
        """Tente de poster une réponse via Firefox en cas de rate limit."""
        try:
            logger.info("Tentative de réponse via Firefox fallback", 
                       **log_step("firefox_reply_fallback_start"))
            
            from .firefox_twitter_service import FirefoxTwitterService
            
            with FirefoxTwitterService() as firefox_service:
                # Pour les réponses, on poste directement le texte
                result = firefox_service.post_tweet(text)
                
                if result:
                    logger.info("Réponse Firefox réussie", 
                               **log_step("firefox_reply_fallback_success", method="firefox"))
                    return result
                else:
                    logger.error("Réponse Firefox échouée", 
                               **log_step("firefox_reply_fallback_error"))
                    return None
                    
        except Exception as e:
            logger.error(f"Erreur lors du fallback Firefox pour la réponse: {e}", 
                        **log_step("firefox_reply_fallback_error", error=str(e)))
            return None
    
    def create_viral_tweet_text(self, repo_data: Dict[str, Any], summary: str) -> str:
        """
        Create engaging tweet text for a repository.
        
        Args:
            repo_data: Repository information
            summary: AI-generated summary
            
        Returns:
            Formatted tweet text
        """
        language_emojis = {
            'Python': '🐍', 'JavaScript': '📜', 'Go': '⚡',
            'Rust': '🦀', 'Java': '☕', 'TypeScript': '📝',
            'C++': '⚙️', 'C': '🔧', 'Swift': '🍎', 'Kotlin': '🎯'
        }
        
        emoji = language_emojis.get(repo_data.get('language', ''), '💻')
        stars = repo_data.get('stargazers_count', 0)
        name = repo_data.get('name', 'Project')
        
        # Keep it very short
        base_text = f"{emoji} {name}\n⭐ {stars:,} stars"
        hashtags = "\n#GitHub"
        
        # Smart truncation to avoid cutting words
        max_summary = 100
        if len(summary) > max_summary:
            truncated = summary[:max_summary-3]
            last_space = truncated.rfind(' ')
            if last_space > 50:  # Keep reasonable length
                summary = truncated[:last_space] + "..."
            else:
                summary = truncated + "..."
        
        tweet_text = f"{base_text}\n\n{summary}{hashtags}"
        
        # Final safety check - max 200 chars total with smart truncation
        if len(tweet_text) > 200:
            available_space = 200 - len(base_text) - len(hashtags) - 4  # 4 for \n\n
            if available_space > 20:
                truncated = summary[:available_space-3]
                last_space = truncated.rfind(' ')
                if last_space > 15:
                    summary = truncated[:last_space] + "..."
                else:
                    summary = truncated + "..."
            else:
                summary = "Projet intéressant..."
            
            tweet_text = f"{base_text}\n\n{summary}{hashtags}"
        
        return tweet_text
    
    def create_reply_text(self, repo_data: Dict[str, Any], features: list[str], url: str) -> str:
        """
        Create reply tweet with additional details.
        
        Args:
            repo_data: Repository information
            features: Key features list
            url: Repository URL
            
        Returns:
            Formatted reply text
        """
        description = repo_data.get('description') or ''
        if len(description) > 80:
            description = description[:80] + "..."
        
        features_text = "\n".join([f"• {feature}" for feature in features[:3]])
        
        base_text = f"{features_text}\n\nLien: {url}\n#Code"
        
        # Ensure reply stays under 280 characters
        if len(base_text) > 280:
            # Truncate features if needed
            features_text = "\n".join([f"• {feature}" for feature in features[:2]])
            base_text = f"📌 {description}\n\n{features_text}\n\n🔗 {url}\n#Code"
        
        return base_text