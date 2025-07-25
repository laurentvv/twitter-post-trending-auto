import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict
from config.settings import DATA_DIR

class GitHubAnalyzer:
    def __init__(self):
        self.github_api = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}

    def get_trending_repositories(self, language: str = None, days: int = 7) -> List[Dict]:
        """
        Récupère les dépôts tendance sur GitHub
        Utilise l'API GitHub Search
        """
        since_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        query = f"created:>{since_date}"
        if language:
            query += f" language:{language}"

        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': 20
        }

        try:
            response = requests.get(
                f"{self.github_api}/search/repositories",
                params=params,
                headers=self.headers
            )

            if response.status_code == 200:
                repos = response.json()['items']
                return self._filter_quality_repos(repos)
        except Exception as e:
            print(f"Erreur GitHub API: {e}")

        return []

    def _filter_quality_repos(self, repos: List[Dict]) -> List[Dict]:
        """Filtre les dépôts de qualité (min 50 stars, description)"""
        filtered = []
        for repo in repos:
            if (repo.get('stargazers_count', 0) >= 50 and
                repo.get('description') and
                not repo.get('private', False)):
                filtered.append(repo)
        return filtered[:10]  # Limite à 10

    def get_repository_details(self, owner: str, repo: str) -> Dict:
        """Récupère les détails complets d'un dépôt"""
        try:
            response = requests.get(
                f"{self.github_api}/repos/{owner}/{repo}",
                headers=self.headers
            )

            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Erreur détails dépôt: {e}")

        return {}

    def save_trending_repos(self, repos: List[Dict], filename: str = "trending_repos.json"):
        """Sauvegarde les dépôts tendance"""
        filepath = f"{DATA_DIR}{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(repos, f, indent=2, ensure_ascii=False)

    def load_trending_repos(self, filename: str = "trending_repos.json") -> List[Dict]:
        """Charge les dépôts tendance sauvegardés"""
        filepath = f"{DATA_DIR}{filename}"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
