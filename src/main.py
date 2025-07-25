"""Complete GitHub Tweet Bot workflow."""
import asyncio
import time
import random
from pathlib import Path

from .core.config import settings
from .core.logger import logger, log_step
from .services.github_service import GitHubService
from .services.screenshot_service import ScreenshotService
from .services.ai_service import AIService
from .services.twitter_service import TwitterService
from .services.history_service import HistoryService


async def process_trending_repository():
    """Complete workflow for processing a trending repository."""
    start_time = time.time()
    
    logger.info("Starting complete workflow", **log_step("workflow_start"))
    
    # Initialize services
    github_service = GitHubService()
    ai_service = AIService()
    twitter_service = TwitterService()
    history_service = HistoryService()
    
    try:
        # Step 1: Get trending repositories
        logger.info("Step 1: Fetching trending repositories", **log_step("step_1_start"))
        repositories = github_service.get_trending_repositories(limit=20)
        
        if not repositories:
            logger.error("No repositories found", **log_step("workflow_error"))
            return
        
        # Filter out already posted repositories
        unposted_repos = history_service.get_unposted_repos(repositories)
        
        if not unposted_repos:
            logger.warning("All trending repositories already posted", **log_step("all_posted"))
            # Clear old history and try again
            history_service.clear_old_history(days=7)
            unposted_repos = history_service.get_unposted_repos(repositories)
            
            if not unposted_repos:
                logger.error("No new repositories to post", **log_step("workflow_error"))
                return
        
        # Select random unposted repository
        repo = random.choice(unposted_repos)
        repo_name = repo['name']
        repo_url = repo['html_url']
        
        logger.info(
            "Repository selected",
            **log_step("step_1_success", repo_name=repo_name, repo_url=repo_url)
        )
        
        # Step 2: Capture screenshot
        logger.info("Step 2: Capturing screenshot", **log_step("step_2_start"))
        
        async with ScreenshotService() as screenshot_service:
            screenshot_filename = f"{repo_name}_{int(time.time())}.png"
            try:
                screenshot_path = await screenshot_service.capture_repository(
                    repo_url, screenshot_filename
                )
                logger.info(
                    "Screenshot captured",
                    **log_step("step_2_success", path=screenshot_path)
                )
            except Exception as e:
                logger.warning(
                    "Screenshot failed, continuing without image",
                    **log_step("step_2_warning", error=str(e))
                )
                screenshot_path = None
        
        # Step 3: Get README and generate content with AI
        logger.info("Step 3: Processing README with AI", **log_step("step_3_start"))
        
        readme_content = github_service.get_readme_content(repo_url)
        
        if readme_content:
            summary = ai_service.summarize_readme(readme_content)
            features = ai_service.extract_key_features(readme_content)
        else:
            summary = "Découvrez ce projet GitHub intéressant !"
            features = ["Projet open source", "Code de qualité", "Communauté active"]
        
        logger.info(
            "AI processing completed",
            **log_step("step_3_success", summary_length=len(summary), features_count=len(features))
        )
        
        # Step 4: Create and post tweets
        logger.info("Step 4: Creating and posting tweets", **log_step("step_4_start"))
        
        # Create main tweet
        main_tweet_text = twitter_service.create_viral_tweet_text(repo, summary)
        reply_text = twitter_service.create_reply_text(repo, features, repo_url)
        
        # Log tweet info without emojis
        logger.info(
            "Tweets ready for posting",
            **log_step("tweets_ready", 
                      main_length=len(main_tweet_text),
                      reply_length=len(reply_text),
                      has_screenshot=bool(screenshot_path))
        )
        
        # POST REAL TWEETS WITH SCREENSHOT
        main_tweet_id = twitter_service.create_tweet(main_tweet_text, screenshot_path)
        
        if main_tweet_id:
            logger.info(
                "Main tweet posted",
                **log_step("step_4_main_success", tweet_id=main_tweet_id)
            )
            
            # Mark repository as posted
            history_service.mark_as_posted(repo_url, main_tweet_id)
            
            # Post reply thread
            reply_success = twitter_service.reply_to_tweet(main_tweet_id, reply_text)
            
            if reply_success:
                logger.info(
                    "Thread complet posté",
                    **log_step("step_4_reply_success")
                )
            else:
                logger.warning("Thread échoué", **log_step("step_4_reply_warning"))
        else:
            logger.error("Tweet principal échoué", **log_step("step_4_main_error"))
        
        # Workflow completed
        total_time = time.time() - start_time
        logger.info(
            "Workflow completed successfully",
            **log_step("workflow_success", 
                      repo_name=repo_name,
                      duration=f"{total_time:.2f}s",
                      main_tweet_id=main_tweet_id)
        )
        
    except Exception as e:
        logger.error(
            "Workflow failed",
            **log_step("workflow_error", error=str(e), duration=f"{time.time() - start_time:.2f}s")
        )
        raise


async def main():
    """Main entry point."""
    logger.info("GitHub Tweet Bot - Complete Workflow", **log_step("bot_start"))
    
    # Create directories
    for directory in [settings.data_dir, settings.logs_dir, settings.screenshots_dir]:
        Path(directory).mkdir(exist_ok=True)
    
    # Run the complete workflow
    await process_trending_repository()


if __name__ == "__main__":
    asyncio.run(main())