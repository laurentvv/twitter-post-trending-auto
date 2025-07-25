import ollama
import requests
from config.settings import OLLAMA_MODEL, OLLAMA_HOST

class AISummarizer:
    def __init__(self):
        self.model = OLLAMA_MODEL
        self.host = OLLAMA_HOST

    def summarize_readme(self, readme_content: str) -> str:
        """
        Résume le README avec IA locale (Qwen3:14b)
        """
        prompt = f"""
        Résume ce README GitHub en points clés français.
        Extrais les fonctionnalités principales, les avantages, et ce qui rend ce projet spécial.
        Sois concis et engageant. Maximum 5 points.

        README:
        {readme_content[:2000]}  # Limite de tokens

        Résumé en français:
        """

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
            )
            return response['response'].strip()
        except Exception as e:
            print(f"Erreur IA: {e}")
            return self._fallback_summary(readme_content)

    def _fallback_summary(self, content: str) -> str:
        """Résumé basique si IA échoue"""
        lines = content.split('\n')
        titles = [line for line in lines if line.startswith('#')][:3]
        bullets = [line[2:] for line in lines if line.startswith('- ')][:5]

        summary_points = titles[:2] + bullets[:3]
        return "\n".join([f"• {point}" for point in summary_points[:5]])

    def extract_key_features(self, readme_content: str) -> list:
        """Extrait les fonctionnalités clés"""
        prompt = f"""
        Liste les 5 fonctionnalités principales de ce projet GitHub.
        Réponds uniquement par une liste numérotée en français.

        {readme_content[:1500]}

        Fonctionnalités:
        """

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt
            )
            features = response['response'].strip().split('\n')
            return [f.strip() for f in features if f.strip()][:5]
        except:
            return ["Fonctionnalité 1", "Fonctionnalité 2", "Fonctionnalité 3"]
