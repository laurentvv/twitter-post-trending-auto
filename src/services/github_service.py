"""GitHub service for fetching trending repositories with fallbacks."""
import requests
import random
import base64
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from ..core.config import settings
from ..core.logger import logger, log_step

class GitHubService:
    """Service for GitHub API interactions with multiple fallbacks."""
    
    # List of User-Agents for rotation to avoid blocking
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if settings.github_token:
            self.headers["Authorization"] = f"token {settings.github_token}"
    
    def _parse_number(self, num_str: str) -> int:
        """Parse numbers with commas (e.g., '1,234' -> 1234)."""
        return int(re.sub(r'[^\d]', '', num_str)) if num_str else 0
    
    def get_trending_repositories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending repositories from GitHub API (with 3 retry attempts).
        
        Args:
            limit: Maximum number of repositories to return
            
        Returns:
            List of repository data
        """
        for attempt in range(3):
            try:
                logger.info(
                    "Fetching trending repositories from GitHub API", 
                    **log_step("github_api_fetch", limit=limit, attempt=attempt+1)
                )
                
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
                    "GitHub API trending repositories fetched",
                    **log_step("github_api_success", count=len(repositories), attempt=attempt+1)
                )
                
                return repositories
                
            except Exception as e:
                logger.warning(
                    f"GitHub API fetch attempt {attempt+1} failed",
                    **log_step("github_api_retry", error=str(e), attempt=attempt+1)
                )
                if attempt == 2:  # Last attempt
                    logger.error(
                        "Failed to fetch trending repositories from GitHub API after 3 attempts",
                        **log_step("github_api_error", error=str(e))
                    )
        
        return []
    
    def scrape_github_trending_fallback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape GitHub Trending page as fallback.
        
        Args:
            limit: Maximum number of repositories to return
            
        Returns:
            List of repository data
        """
        try:
            logger.info("Attempting GitHub Trending scraping fallback", **log_step("github_scrape_start", limit=limit))
            
            url = "https://github.com/trending"
            headers = {"User-Agent": random.choice(self.USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            repos = []
            
            for repo in soup.select("article.Box-row")[:limit]:
                try:
                    # Extract repository name - CORRECTION COMPLÈTE ICI
                    name_elem = repo.select_one("h2 a")
                    if not name_elem:
                        continue
                    
                    # Extraire le href qui contient le chemin complet du dépôt
                    href = name_elem.get('href', '')
                    if not href:
                        continue
                    
                    # Nettoyer le href pour obtenir le nom complet du dépôt
                    full_name = href.strip('/')
                    repo_url = "https://github.com" + href
                    
                    # Extraire le nom du dépôt (sans le propriétaire) pour la clé 'name'
                    name = full_name.split('/')[-1] if '/' in full_name else full_name
                    
                    # Extract description
                    desc_elem = repo.select_one("p")
                    description = desc_elem.text.strip() if desc_elem else ""
                    
                    # Extract language
                    lang_elem = repo.select_one("span[itemprop='programmingLanguage']")
                    language = lang_elem.text.strip() if lang_elem else ""
                    
                    # Extract star count
                    stars_elem = repo.select_one("a[href$='/stargazers']")
                    stars = self._parse_number(stars_elem.text.strip()) if stars_elem else 0
                    
                    repos.append({
                        "name": name,  # Ajout de la clé 'name'
                        "full_name": full_name,
                        "description": description,
                        "language": language,
                        "stargazers_count": stars,
                        "html_url": repo_url
                    })
                except Exception as e:
                    logger.warning(f"Error parsing repository: {str(e)}", **log_step("scrape_parse_error"))
                    continue
            
            logger.info(
                "GitHub Trending scraping fallback successful",
                **log_step("github_scrape_success", count=len(repos))
            )
            return repos
            
        except Exception as e:
            logger.error(
                f"GitHub Trending scraping fallback failed: {str(e)}",
                **log_step("github_scrape_error", error=str(e))
            )
            return []
    
    def fetch_libhunt_trending(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch trending repositories from LibHunt API.
        
        Args:
            limit: Maximum number of repositories to return
            
        Returns:
            List of repository data
        """
        try:
            logger.info("Attempting LibHunt API fallback", **log_step("libhunt_start", limit=limit))
            
            url = "https://libhunt.com/api/v1/trending/github"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            repositories = []
            
            for repo in data.get("repositories", [])[:limit]:
                full_name = repo["full_name"]
                repositories.append({
                    "name": full_name.split('/')[-1],  # Ajout de la clé 'name'
                    "full_name": full_name,
                    "description": repo.get("description", ""),
                    "language": repo.get("language", ""),
                    "stargazers_count": repo.get("stars", 0),
                    "html_url": f"https://github.com/{repo['full_name']}"
                })
            
            logger.info(
                "LibHunt API fallback successful",
                **log_step("libhunt_success", count=len(repositories))
            )
            return repositories
            
        except Exception as e:
            logger.error(
                f"LibHunt API fallback failed: {str(e)}",
                **log_step("libhunt_error", error=str(e))
            )
            return []
    
    def fetch_gitstar_ranking(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch trending repositories from Gitstar Ranking.
        
        Args:
            limit: Maximum number of repositories to return
            
        Returns:
            List of repository data
        """
        try:
            logger.info("Attempting Gitstar Ranking fallback", **log_step("gitstar_start", limit=limit))
            
            url = "https://gitstar-ranking.com/repositories"
            headers = {"User-Agent": random.choice(self.USER_AGENTS)}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            repos = []
            
            for row in soup.select("table tbody tr")[:limit]:
                try:
                    name_elem = row.select_one("td:nth-child(2) a")
                    if not name_elem:
                        continue
                    
                    full_name = name_elem.text.strip()
                    repo_url = "https://github.com" + name_elem["href"]
                    
                    stars_elem = row.select_one("td:nth-child(3)")
                    stars = self._parse_number(stars_elem.text.strip()) if stars_elem else 0
                    
                    repos.append({
                        "name": full_name.split('/')[-1],  # Ajout de la clé 'name'
                        "full_name": full_name,
                        "description": "",  # Gitstar doesn't provide descriptions
                        "language": "",     # Gitstar doesn't provide language
                        "stargazers_count": stars,
                        "html_url": repo_url
                    })
                except Exception as e:
                    logger.warning(f"Error parsing Gitstar repository: {str(e)}", **log_step("gitstar_parse_error"))
                    continue
            
            logger.info(
                "Gitstar Ranking fallback successful",
                **log_step("gitstar_success", count=len(repos))
            )
            return repos
            
        except Exception as e:
            logger.error(
                f"Gitstar Ranking fallback failed: {str(e)}",
                **log_step("gitstar_error", error=str(e))
            )
            return []
    
    def get_trending_repositories_with_fallbacks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending repositories with multiple fallback sources.
        
        Args:
            limit: Maximum number of repositories to return
            
        Returns:
            List of repository data
        """
        # 1. Try GitHub API first
        repos = self.get_trending_repositories(limit)
        if repos:
            logger.info("Successfully fetched from GitHub API", **log_step("primary_success", count=len(repos)))
            return repos
        
        logger.warning("GitHub API failed, trying fallbacks")
        
        # 2. Fallback 1: Scrape GitHub Trending
        repos = self.scrape_github_trending_fallback(limit)
        if repos:
            logger.info("Successfully fetched from GitHub scraping fallback", **log_step("fallback1_success", count=len(repos)))
            return repos
        
        # 3. Fallback 2: LibHunt API
        repos = self.fetch_libhunt_trending(limit)
        if repos:
            logger.info("Successfully fetched from LibHunt fallback", **log_step("fallback2_success", count=len(repos)))
            return repos
        
        # 4. Fallback 3: Gitstar Ranking
        repos = self.fetch_gitstar_ranking(limit)
        if repos:
            logger.info("Successfully fetched from Gitstar fallback", **log_step("fallback3_success", count=len(repos)))
            return repos
        
        logger.error("All fallbacks failed")
        return []
    
    def get_readme_content(self, repo_url: str) -> Optional[str]:
        """
        Get README content from repository (with 3 retry attempts).
        
        Args:
            repo_url: Repository URL (e.g., https://github.com/owner/repo)
            
        Returns:
            README content or None
        """
        for attempt in range(3):
            try:
                # Extract owner and repo from URL
                parts = repo_url.replace("https://github.com/", "").split("/")
                if len(parts) < 2:
                    return None
                
                owner, repo = parts[0], parts[1]
                
                logger.info(
                    "Fetching README",
                    **log_step("readme_fetch", owner=owner, repo=repo, attempt=attempt+1)
                )
                
                # Try different README file names
                for readme_name in ["README.md", "README.rst", "README.txt", "README"]:
                    url = f"{self.base_url}/repos/{owner}/{repo}/contents/{readme_name}"
                    response = requests.get(url, headers=self.headers, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("encoding") == "base64":
                            content = base64.b64decode(data["content"]).decode("utf-8")
                            
                            logger.info(
                                "README fetched successfully",
                                **log_step("readme_success", filename=readme_name, length=len(content), attempt=attempt+1)
                            )
                            
                            return content
                
                logger.warning(
                    "README not found", 
                    **log_step("readme_not_found", attempt=attempt+1)
                )
                return None
                
            except Exception as e:
                logger.warning(
                    f"README fetch attempt {attempt+1} failed",
                    **log_step("readme_retry", error=str(e), attempt=attempt+1)
                )
                if attempt == 2:  # Last attempt
                    logger.error(
                        "Failed to fetch README after 3 attempts",
                        **log_step("readme_error", error=str(e))
                    )
        
        return None