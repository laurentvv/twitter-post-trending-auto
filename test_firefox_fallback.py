#!/usr/bin/env python3
"""Script de test pour le service Firefox Twitter."""

import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.firefox_config import firefox_config
from services.firefox_twitter_service import FirefoxTwitterService


def test_firefox_config():
    """Test de la configuration Firefox."""
    print("🔧 Test de la configuration Firefox...")
    
    config = firefox_config.get_config()
    print(f"Configuration: {config}")
    
    if firefox_config.is_enabled():
        print("✅ Service Firefox activé")
        print(f"📁 Profil: {config['profile_path']}")
        print(f"👻 Headless: {config['headless']}")
    else:
        print("❌ Service Firefox désactivé")
        return False
    
    return True


def test_firefox_service():
    """Test du service Firefox."""
    print("\n🚀 Test du service Firefox...")
    
    try:
        with FirefoxTwitterService() as firefox_service:
            if not firefox_service.driver:
                print("❌ Driver Firefox non initialisé")
                return False
            
            print("✅ Driver Firefox initialisé")
            
            # Test de navigation (sans poster)
            print("🌐 Test de navigation vers Twitter...")
            firefox_service.driver.get("https://twitter.com")
            
            # Attendre un peu pour voir si ça charge
            import time
            time.sleep(5)
            
            current_url = firefox_service.driver.current_url
            print(f"📍 URL actuelle: {current_url}")
            
            if "twitter.com" in current_url:
                print("✅ Navigation vers Twitter réussie")
                return True
            else:
                print("❌ Navigation vers Twitter échouée")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors du test Firefox: {e}")
        return False


def test_firefox_post():
    """Test de post via Firefox (simulation)."""
    print("\n📝 Test de post Firefox (simulation)...")
    
    try:
        with FirefoxTwitterService() as firefox_service:
            if not firefox_service.driver:
                print("❌ Driver Firefox non disponible")
                return False
            
            # Test avec un tweet de test
            test_tweet = "🧪 Test automatique du service Firefox #TestBot"
            
            print(f"📤 Tentative de post: {test_tweet}")
            
            # Note: Ceci est un test, on ne poste pas vraiment
            print("⚠️  Mode test - pas de post réel")
            print("✅ Service Firefox prêt pour utilisation")
            
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test de post: {e}")
        return False


def main():
    """Fonction principale de test."""
    print("🧪 Tests du service Firefox Twitter")
    print("=" * 50)
    
    # Test 1: Configuration
    if not test_firefox_config():
        print("\n❌ Configuration Firefox échouée")
        return False
    
    # Test 2: Service
    if not test_firefox_service():
        print("\n❌ Service Firefox échoué")
        return False
    
    # Test 3: Post (simulation)
    if not test_firefox_post():
        print("\n❌ Test de post Firefox échoué")
        return False
    
    print("\n🎉 Tous les tests Firefox sont passés!")
    print("✅ Le service Firefox est prêt à être utilisé comme fallback")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 