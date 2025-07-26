"""AI service with multi-provider fallback system."""
import ollama
import requests
from typing import List, Optional

from ..core.config import settings
from ..core.logger import logger, log_step


class AIService:
    """AI service with multi-provider fallback system."""
    
    def __init__(self):
        self.ollama_client = ollama.Client(host=settings.ollama_host)
        self.ollama_model = settings.ollama_model
        
        # Provider order: Gemini -> OpenRouter -> Mistral -> Ollama
        self.providers = [
            ("Gemini", self._gemini_request),
            ("OpenRouter", self._openrouter_request), 
            ("Mistral", self._mistral_request),
            ("Ollama", self._ollama_request)
        ]
    
    def summarize_readme(self, readme_content: str) -> str:
        """
        Generate a catchy French summary using multi-provider fallback.
        
        Args:
            readme_content: README content to summarize
            
        Returns:
            French summary or fallback text
        """
        logger.info(
            "Generating README summary",
            **log_step("ai_summarize", content_length=len(readme_content))
        )
        
        prompt = f"""Crée une phrase accrocheuse de 8-12 mots en français pour décrire ce projet GitHub.
Utilise les accents français. Sois enthousiaste et précis.

Exemples: "Convertisseur intelligent qui transforme tous vos documents en Markdown", "Modèle d'IA révolutionnaire pour le raisonnement avancé"

Projet: {readme_content[:800]}

Phrase accrocheuse:"""
        
        # Try each provider in order
        for provider_name, provider_func in self.providers:
            summary = self._try_provider(provider_func, prompt, provider_name, "summary")
            if summary:
                logger.info(
                    "Summary generated",
                    **log_step("ai_summary_success", provider=provider_name, summary_length=len(summary))
                )
                return self._fix_accents(summary)
        
        # All providers failed
        logger.error("All AI providers failed for summary", **log_step("ai_summary_all_failed"))
        return "Découvrez ce projet GitHub intéressant !"
    
    def extract_key_features(self, readme_content: str) -> List[str]:
        """
        Extract key features using multi-provider fallback.
        
        Args:
            readme_content: README content to analyze
            
        Returns:
            List of key features in French
        """
        logger.info(
            "Extracting key features",
            **log_step("ai_features", content_length=len(readme_content))
        )
        
        prompt = f"""Liste 3 fonctionnalités principales de ce projet en français.
Chaque fonctionnalité en 2-3 mots avec accents.
Format: une fonctionnalité par ligne.

Exemples:
Conversion automatique
Interface intuitive
Support multi-formats

Projet: {readme_content[:600]}

Fonctionnalités:"""
        
        # Try each provider in order
        for provider_name, provider_func in self.providers:
            features_text = self._try_provider(provider_func, prompt, provider_name, "features")
            if features_text:
                features = [f.strip() for f in features_text.split('\n') if f.strip() and not f.startswith('Voici')][:3]
                if features:
                    logger.info(
                        "Features extracted",
                        **log_step("ai_features_success", provider=provider_name, count=len(features))
                    )
                    return features
        
        # All providers failed
        logger.error("All AI providers failed for features", **log_step("ai_features_all_failed"))
        return ["Fonctionnalité principale", "Interface moderne", "Open source"]
    
    def _try_provider(self, provider_func, prompt: str, provider_name: str, task: str) -> Optional[str]:
        """Try a provider with 3 retry attempts."""
        for attempt in range(3):
            try:
                result = provider_func(prompt)
                if result and len(result.strip()) > 0:
                    return result.strip()
            except Exception as e:
                logger.warning(
                    f"{provider_name} {task} attempt {attempt+1} failed",
                    **log_step(f"ai_{task}_retry", provider=provider_name, error=str(e), attempt=attempt+1)
                )
        
        logger.warning(
            f"{provider_name} failed after 3 attempts",
            **log_step(f"ai_{task}_provider_failed", provider=provider_name)
        )
        return None
    
    def _gemini_request(self, prompt: str) -> str:
        """Make request to Gemini API."""
        if not settings.gemini_api_key:
            raise Exception("Gemini API key not configured")
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.gemini_api_key}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.5, "maxOutputTokens": 100}
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"Gemini API error: {response.status_code}")
    
    def _openrouter_request(self, prompt: str) -> str:
        """Make request to OpenRouter API."""
        if not settings.openrouter_api_key:
            raise Exception("OpenRouter API key not configured")
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistralai/mistral-small-3.2-24b-instruct:free",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.5
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"OpenRouter API error: {response.status_code}")
    
    def _mistral_request(self, prompt: str) -> str:
        """Make request to Mistral API."""
        if not settings.mistral_api_key:
            raise Exception("Mistral API key not configured")
        
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.mistral_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-small-latest",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 100,
                "temperature": 0.5
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            raise Exception(f"Mistral API error: {response.status_code}")
    
    def _ollama_request(self, prompt: str) -> str:
        """Make request to Ollama (local fallback)."""
        response = self.ollama_client.generate(
            model=self.ollama_model,
            prompt=prompt,
            think=False,
            options={"temperature": 0.5, "num_predict": 80}
        )
        return response['response']
    
    def _fix_accents(self, text: str) -> str:
        """Fix common missing French accents."""
        accent_fixes = {
            'crez': 'créez', 'prsence': 'présence', 'ds': 'dès',
            'revolutionnaire': 'révolutionnaire', 'avance': 'avancé',
            'editeur': 'éditeur', 'fonctionnalites': 'fonctionnalités',
            'donnees': 'données', 'cree': 'crée', 'integre': 'intègre',
            'genere': 'génère', 'ameliore': 'améliore'
        }
        
        for wrong, correct in accent_fixes.items():
            text = text.replace(wrong, correct)
        
        return text