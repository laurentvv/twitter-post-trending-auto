"""Modern Twitter service using Tweepy v4 and Twitter API v2 with Firefox fallback."""
import tweepy
from typing import Optional, Dict, Any
from pathlib import Path
import time

from ..core.config import settings
from ..core.logger import logger, log_step


class TwitterService:
    """Modern Twitter service with API v2 and Firefox fallback."""
    
    def __init__(self):
        self.client: Optional[tweepy.Client] = None
        self.firefox_service = None
        self._setup_client()
    
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
                wait_on_rate_limit=False  # Disable auto-wait to handle rate limits manually
            )
            logger.info("Twitter client ready with OAuth 1.0a", **log_step("twitter_ready"))
            return
        
        # Fallback to Bearer Token
        if settings.twitter_bearer_token:
            self.client = tweepy.Client(
                bearer_token=settings.twitter_bearer_token,
                wait_on_rate_limit=False
            )
            logger.info("Twitter client ready with Bearer Token", **log_step("twitter_ready"))
        else:
            raise ValueError("Twitter credentials required")
    
    def _is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is related to rate limiting."""
        error_str = str(error).lower()
        rate_limit_indicators = [
            'rate limit exceeded',
            '429',
            'too many requests',
            'rate limited',
            'quota exceeded'
        ]
        return any(indicator in error_str for indicator in rate_limit_indicators)
    
    def _init_firefox_fallback(self):
        """Initialize Firefox service as fallback."""
        if self.firefox_service is None:
            try:
                from ..services.firefox_twitter_service import FirefoxTwitterService
                self.firefox_service = FirefoxTwitterService()
                logger.info("Firefox fallback service initialized", **log_step("firefox_fallback_init"))
            except Exception as e:
                logger.error(f"Failed to initialize Firefox fallback: {e}", **log_step("firefox_fallback_error"))
                self.firefox_service = None
    
    def create_tweet(self, text: str, media_path: Optional[str] = None, use_firefox_fallback: bool = True) -> Optional[str]:
        """
        Create a tweet with optional media and Firefox fallback for rate limits.
        
        Args:
            text: Tweet text content
            media_path: Optional path to media file
            use_firefox_fallback: Whether to use Firefox if API fails
            
        Returns:
            Tweet ID if successful, None otherwise
        """
        # First try Twitter API
        for attempt in range(2):  # Reduced to 2 attempts for API
            try:
                logger.info(
                    "Creating tweet via API",
                    **log_step("tweet_create_api", text_length=len(text), has_media=bool(media_path), attempt=attempt+1)
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
                        if self._is_rate_limit_error(e):
                            logger.warning(
                                "Rate limit hit during media upload",
                                **log_step("media_rate_limit", error=str(e))
                            )
                            break  # Exit API attempts, go to Firefox
                        logger.warning(
                            "Media upload failed, posting without image",
                            **log_step("media_upload_error", error=str(e))
                        )
                
                response = self.client.create_tweet(text=text, media_ids=media_ids)
                
                if response.data:
                    tweet_id = response.data['id']
                    logger.info(
                        "Tweet created successfully via API",
                        **log_step("tweet_api_success", tweet_id=tweet_id, attempt=attempt+1)
                    )
                    return tweet_id
                
            except Exception as e:
                if self._is_rate_limit_error(e):
                    logger.warning(
                        "Rate limit exceeded on API, switching to Firefox fallback",
                        **log_step("api_rate_limit", error=str(e))
                    )
                    break  # Exit API attempts, go to Firefox
                
                logger.warning(
                    f"Tweet creation attempt {attempt+1} failed",
                    **log_step("tweet_api_retry", error=str(e), attempt=attempt+1)
                )
                
                if attempt == 1:  # Last API attempt
                    logger.error(
                        "Tweet creation failed after API attempts",
                        **log_step("tweet_api_failed", error=str(e))
                    )
        
        # Fallback to Firefox if API failed or rate limited
        if use_firefox_fallback:
            logger.info("Attempting Firefox fallback for tweet", **log_step("firefox_fallback_start"))
            try:
                self._init_firefox_fallback()
                if self.firefox_service:
                    tweet_id = self.firefox_service.post_tweet(text, image_path=media_path)
                    if tweet_id:
                        logger.info(
                            "Tweet created successfully via Firefox",
                            **log_step("tweet_firefox_success", tweet_id=tweet_id)
                        )
                        return tweet_id
                    else:
                        logger.error("Firefox tweet creation failed", **log_step("tweet_firefox_failed"))
                else:
                    logger.error("Firefox service not available", **log_step("firefox_not_available"))
            except Exception as e:
                logger.error(f"Firefox fallback failed: {e}", **log_step("firefox_fallback_error", error=str(e)))
        
        return None
    
    def reply_to_tweet(self, tweet_id: str, text: str, use_firefox_fallback: bool = True) -> Optional[str]:
        """
        Reply to a tweet with Firefox fallback for rate limits.
        
        Args:
            tweet_id: ID of tweet to reply to
            text: Reply text
            use_firefox_fallback: Whether to use Firefox if API fails
            
        Returns:
            Reply tweet ID if successful, None otherwise
        """
        # First try Twitter API
        for attempt in range(2):  # Reduced to 2 attempts for API
            try:
                logger.info(
                    "Creating reply via API",
                    **log_step("reply_create_api", tweet_id=tweet_id, text_length=len(text), attempt=attempt+1)
                )
                
                response = self.client.create_tweet(
                    text=text,
                    in_reply_to_tweet_id=tweet_id
                )
                
                if response.data:
                    reply_id = response.data['id']
                    logger.info(
                        "Reply created successfully via API",
                        **log_step("reply_api_success", reply_id=reply_id, attempt=attempt+1)
                    )
                    return reply_id
                    
            except Exception as e:
                if self._is_rate_limit_error(e):
                    logger.warning(
                        "Rate limit exceeded on API for reply, switching to Firefox fallback",
                        **log_step("api_reply_rate_limit", error=str(e))
                    )
                    break  # Exit API attempts, go to Firefox
                
                logger.warning(
                    f"Reply creation attempt {attempt+1} failed",
                    **log_step("reply_api_retry", error=str(e), attempt=attempt+1)
                )
                
                if attempt == 1:  # Last API attempt
                    logger.error(
                        "Reply creation failed after API attempts",
                        **log_step("reply_api_failed", error=str(e))
                    )
        
        # Fallback to Firefox if API failed or rate limited
        if use_firefox_fallback:
            logger.info("Attempting Firefox fallback for reply", **log_step("firefox_reply_fallback_start"))
            try:
                self._init_firefox_fallback()
                if self.firefox_service:
                    reply_id = self.firefox_service.post_reply(tweet_id, text)
                    if reply_id:
                        logger.info(
                            "Reply created successfully via Firefox",
                            **log_step("reply_firefox_success", reply_id=reply_id)
                        )
                        return reply_id
                    else:
                        logger.error("Firefox reply creation failed", **log_step("reply_firefox_failed"))
                else:
                    logger.error("Firefox service not available for reply", **log_step("firefox_not_available"))
            except Exception as e:
                logger.error(f"Firefox reply fallback failed: {e}", **log_step("firefox_reply_fallback_error", error=str(e)))
        
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
    
    def close_firefox(self):
        """Close Firefox service if initialized."""
        if self.firefox_service:
            try:
                self.firefox_service.close()
                logger.info("Firefox service closed", **log_step("firefox_closed"))
            except Exception as e:
                logger.warning(f"Error closing Firefox service: {e}")
            finally:
                self.firefox_service = None