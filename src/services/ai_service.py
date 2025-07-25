"""AI service using Ollama for content generation."""
import ollama
import re
from typing import List

from ..core.config import settings
from ..core.logger import logger, log_step


class AIService:
    """Service for AI-powered content generation."""
    
    def __init__(self):
        self.client = ollama.Client(host=settings.ollama_host)
        self.model = settings.ollama_model
    
    def summarize_readme(self, readme_content: str) -> str:
        """
        Generate a concise summary of README content.
        
        Args:
            readme_content: Raw README text
            
        Returns:
            Concise summary for tweet
        """
        logger.info(
            "Generating README summary",
            **log_step("ai_summarize", content_length=len(readme_content))
        )
        
        try:
            prompt = f"""Crée une phrase accrocheuse de 8-12 mots en français pour décrire ce projet GitHub.
Utilise les accents français. Sois enthousiaste et précis.

Exemples: "Convertisseur intelligent qui transforme tous vos documents en Markdown", "Modèle d'IA révolutionnaire pour le raisonnement avancé", "Éditeur de code moderne avec fonctionnalités collaboratives"

Projet: {readme_content[:800]}

Phrase accrocheuse:"""

            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.5,
                    "num_predict": 80
                }
            )
            
            summary = response['response'].strip()
            # Remove think tags
            summary = re.sub(r"<think>.*?</think>\n?", "", summary, flags=re.DOTALL).strip()
            
            summary = response['response'].strip()
            
            # Fix common missing accents
            accent_fixes = {
                'crez': 'créez',
                'prsence': 'présence', 
                'ds': 'dès',
                'revolutionnaire': 'révolutionnaire',
                'avance': 'avancé',
                'moderne': 'moderne',
                'editeur': 'éditeur',
                'fonctionnalites': 'fonctionnalités',
                'donnees': 'données',
                'cree': 'crée',
                'integre': 'intègre',
                'genere': 'génère',
                'ameliore': 'améliore'
            }
            
            for wrong, correct in accent_fixes.items():
                summary = summary.replace(wrong, correct)
            
            logger.info(
                "Summary generated",
                **log_step("ai_summary_success", summary_length=len(summary))
            )
            
            return summary
            
        except Exception as e:
            logger.error(
                "Failed to generate summary",
                **log_step("ai_summary_error", error=str(e))
            )
            return "Découvrez ce projet GitHub intéressant !"
    
    def extract_key_features(self, readme_content: str) -> List[str]:
        """
        Extract key features from README.
        
        Args:
            readme_content: Raw README text
            
        Returns:
            List of key features
        """
        logger.info(
            "Extracting key features",
            **log_step("ai_features", content_length=len(readme_content))
        )
        
        try:
            prompt = f"""Liste 3 fonctionnalités principales de ce projet en français.
Chaque fonctionnalité en 2-3 mots avec accents.
Format: une fonctionnalité par ligne.

Exemples:
Conversion automatique
Interface intuitive
Support multi-formats

Projet: {readme_content[:600]}

Fonctionnalités:"""

            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.4,
                    "num_predict": 50
                }
            )
            
            features_text = response['response'].strip()
            # Remove think tags
            features_text = re.sub(r"<think>.*?</think>\n?", "", features_text, flags=re.DOTALL).strip()
            
            features_text = response['response'].strip()
            features = [f.strip() for f in features_text.split('\n') if f.strip()][:3]
            
            logger.info(
                "Features extracted",
                **log_step("ai_features_success", count=len(features))
            )
            
            return features if features else ["Fonctionnalité principale"]
            
        except Exception as e:
            logger.error(
                "Failed to extract features",
                **log_step("ai_features_error", error=str(e))
            )
            return ["Fonctionnalité principale", "Interface moderne", "Open source"]