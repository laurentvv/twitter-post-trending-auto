"""GitHub service for fetching trending repositories."""
import requests
from typing import List, Dict, Any, Optional

from ..core.config import settings
from ..core.logger import logger, log_step


class GitHubService:
    """Service for GitHub API interactions."""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if settings.github_token:
            self.headers["Authorization"] = f"token {settings.github_token}"
    
    def get_trending_repositories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending repositories from GitHub.
        
        Args:
            limit: Maximum number of repositories to return
            
        Returns:
            List of repository data
        """
        logger.info("Fetching trending repositories", **log_step("github_fetch", limit=limit))
        
        try:
            # Search for repositories created in the last week, sorted by stars
            url = f"{self.base_url}/search/repositories"
            params = {
                "q": "created:>2024-01-01",
                "sort": "stars",
                "order": "desc",
                "per_page": limit
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            repositories = data.get("items", [])
            
            logger.info(
                "Trending repositories fetched",
                **log_step("github_success", count=len(repositories))
            )
            
            return repositories
            
        except Exception as e:
            logger.error(
                "Failed to fetch trending repositories",
                **log_step("github_error", error=str(e))
            )
            return []
    
    def get_readme_content(self, repo_url: str) -> Optional[str]:
        """
        Get README content from repository.
        
        Args:
            repo_url: Repository URL (e.g., https://github.com/owner/repo)
            
        Returns:
            README content or None
        """
        try:
            # Extract owner and repo from URL
            parts = repo_url.replace("https://github.com/", "").split("/")
            if len(parts) < 2:
                return None
            
            owner, repo = parts[0], parts[1]
            
            logger.info(
                "Fetching README",
                **log_step("readme_fetch", owner=owner, repo=repo)
            )
            
            # Try different README file names
            for readme_name in ["README.md", "README.rst", "README.txt", "README"]:
                url = f"{self.base_url}/repos/{owner}/{repo}/contents/{readme_name}"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("encoding") == "base64":
                        import base64
                        content = base64.b64decode(data["content"]).decode("utf-8")
                        
                        logger.info(
                            "README fetched successfully",
                            **log_step("readme_success", filename=readme_name, length=len(content))
                        )
                        
                        return content
            
            logger.warning("README not found", **log_step("readme_not_found"))
            return None
            
        except Exception as e:
            logger.error(
                "Failed to fetch README",
                **log_step("readme_error", error=str(e))
            )
            return None