"""History service to track posted repositories."""
import json
from pathlib import Path
from datetime import datetime
from typing import Set, Dict, Any

from ..core.config import settings
from ..core.logger import logger, log_step


class HistoryService:
    """Service to track posted repositories and avoid duplicates."""
    
    def __init__(self):
        self.history_file = Path(settings.data_dir) / "posted_repos.json"
        self.history_file.parent.mkdir(exist_ok=True)
        self._load_history()
    
    def _load_history(self) -> None:
        """Load posting history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.posted_repos: Set[str] = set(data.get('repos', []))
                    self.last_posts: Dict[str, str] = data.get('last_posts', {})
            else:
                self.posted_repos = set()
                self.last_posts = {}
                
            logger.info(
                "History loaded",
                **log_step("history_loaded", count=len(self.posted_repos))
            )
        except Exception as e:
            logger.warning(
                "Failed to load history, starting fresh",
                **log_step("history_load_error", error=str(e))
            )
            self.posted_repos = set()
            self.last_posts = {}
    
    def _save_history(self) -> None:
        """Save posting history to file."""
        try:
            data = {
                'repos': list(self.posted_repos),
                'last_posts': self.last_posts,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            logger.info("History saved", **log_step("history_saved"))
        except Exception as e:
            logger.error(
                "Failed to save history",
                **log_step("history_save_error", error=str(e))
            )
    
    def is_already_posted(self, repo_url: str) -> bool:
        """Check if repository was already posted."""
        return repo_url in self.posted_repos
    
    def mark_as_posted(self, repo_url: str, tweet_id: str) -> None:
        """Mark repository as posted."""
        self.posted_repos.add(repo_url)
        self.last_posts[repo_url] = {
            'tweet_id': tweet_id,
            'posted_at': datetime.now().isoformat()
        }
        self._save_history()
        
        logger.info(
            "Repository marked as posted",
            **log_step("repo_marked", repo_url=repo_url, tweet_id=tweet_id)
        )
    
    def get_unposted_repos(self, repos: list) -> list:
        """Filter out already posted repositories."""
        unposted = [repo for repo in repos if not self.is_already_posted(repo['html_url'])]
        
        logger.info(
            "Filtered repositories",
            **log_step("repos_filtered", 
                      total=len(repos), 
                      unposted=len(unposted),
                      already_posted=len(repos) - len(unposted))
        )
        
        return unposted
    
    def clear_old_history(self, days: int = 30) -> None:
        """Clear history older than specified days."""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        old_repos = []
        
        for repo_url, post_info in list(self.last_posts.items()):
            try:
                posted_at = datetime.fromisoformat(post_info['posted_at'])
                if posted_at < cutoff_date:
                    old_repos.append(repo_url)
                    self.posted_repos.discard(repo_url)
                    del self.last_posts[repo_url]
            except (KeyError, ValueError):
                # Remove invalid entries
                old_repos.append(repo_url)
                self.posted_repos.discard(repo_url)
                self.last_posts.pop(repo_url, None)
        
        if old_repos:
            self._save_history()
            logger.info(
                "Old history cleared",
                **log_step("history_cleared", removed=len(old_repos), days=days)
            )