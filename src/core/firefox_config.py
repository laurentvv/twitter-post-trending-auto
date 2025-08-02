"""Configuration pour le service Firefox Twitter."""
import os
from pathlib import Path
from typing import Optional

from .config import settings


class FirefoxConfig:
    """Configuration pour l'automatisation Firefox."""
    
    def __init__(self):
        self.profile_path = self._get_profile_path()
        self.headless = self._get_headless_setting()
        self.timeout = 30
        self.retry_attempts = 3
        self.wait_between_actions = 2
    
    def _get_profile_path(self) -> Optional[str]:
        """Récupère le chemin du profil Firefox."""
        # Priorité 1: Variable d'environnement
        env_path = os.getenv('FIREFOX_PROFILE_PATH')
        if env_path and Path(env_path).exists():
            return env_path
        
        # Priorité 2: Configuration par défaut de l'utilisateur
        default_path = r'C:\Users\laurent\AppData\Roaming\Mozilla\Firefox\Profiles\7kfdokl3.default-release'
        if Path(default_path).exists():
            return default_path
        
        # Priorité 3: Chercher automatiquement
        return self._find_firefox_profile()
    
    def _find_firefox_profile(self) -> Optional[str]:
        """Trouve automatiquement un profil Firefox."""
        # Windows
        windows_path = Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
        if windows_path.exists():
            for profile_dir in windows_path.iterdir():
                if profile_dir.is_dir() and profile_dir.name.endswith('.default-release'):
                    return str(profile_dir)
        
        # Linux/Mac
        linux_path = Path.home() / ".mozilla" / "firefox"
        if linux_path.exists():
            for profile_dir in linux_path.iterdir():
                if profile_dir.is_dir() and profile_dir.name.endswith('.default-release'):
                    return str(profile_dir)
        
        return None
    
    def _get_headless_setting(self) -> bool:
        """Détermine si Firefox doit tourner en mode headless."""
        env_setting = os.getenv('FIREFOX_HEADLESS', 'true').lower()
        return env_setting in ('true', '1', 'yes')
    
    def is_enabled(self) -> bool:
        """Vérifie si le service Firefox est activé."""
        enabled = os.getenv('FIREFOX_ENABLED', 'true').lower()
        return enabled in ('true', '1', 'yes') and self.profile_path is not None
    
    def get_config(self) -> dict:
        """Retourne la configuration complète."""
        return {
            "profile_path": self.profile_path,
            "headless": self.headless,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "wait_between_actions": self.wait_between_actions,
            "enabled": self.is_enabled()
        }


# Instance globale
firefox_config = FirefoxConfig() 