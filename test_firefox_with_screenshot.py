#!/usr/bin/env python3
"""
Test du service Firefox avec screenshot.
Ce script teste l'intégration des screenshots dans le service Firefox.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from src.services.firefox_twitter_service import FirefoxTwitterService
from src.core.firefox_config import firefox_config


def test_firefox_with_screenshot():
    """Test du service Firefox avec screenshot."""
    print("🧪 Test du service Firefox avec screenshot")
    print("=" * 50)
    
    # Vérifier la configuration
    config = firefox_config.get_config()
    print(f"✅ Configuration Firefox: {'Activé' if config['enabled'] else 'Désactivé'}")
    print(f"📁 Profil: {config['profile_path']}")
    print(f"👻 Mode headless: {'Oui' if config['headless'] else 'Non'}")
    
    if not config['enabled']:
        print("❌ Service Firefox désactivé")
        return
    
    # Chercher un screenshot existant
    screenshot_path = None
    screenshot_dir = Path("screenshots")
    
    if screenshot_dir.exists():
        screenshots = list(screenshot_dir.glob("*.png"))
        if screenshots:
            screenshot_path = str(screenshots[0])
            print(f"📸 Screenshot trouvé: {screenshot_path}")
        else:
            print("⚠️  Aucun screenshot trouvé dans le dossier screenshots/")
    else:
        print("⚠️  Dossier screenshots/ non trouvé")
    
    # Test du service Firefox
    print("\n🚀 Test du service Firefox...")
    
    try:
        with FirefoxTwitterService() as firefox_service:
            if not firefox_service.driver:
                print("❌ Driver Firefox non initialisé")
                return
            
            print("✅ Driver Firefox initialisé")
            
            # Test de navigation vers Twitter
            firefox_service.driver.get("https://twitter.com")
            print("✅ Navigation vers Twitter réussie")
            
            # Test avec screenshot si disponible
            if screenshot_path and Path(screenshot_path).exists():
                print(f"📸 Test avec screenshot: {screenshot_path}")
                
                # Test de post avec screenshot (simulation)
                tweet_text = "Test du service Firefox avec screenshot #Test #Firefox"
                
                print("🔄 Tentative de post avec screenshot...")
                result = firefox_service.post_tweet(tweet_text, screenshot_path=screenshot_path)
                
                if result:
                    print(f"✅ Post réussi avec screenshot! ID: {result}")
                else:
                    print("❌ Échec du post avec screenshot")
            else:
                print("⚠️  Test sans screenshot (aucun fichier disponible)")
                
                # Test de post sans screenshot
                tweet_text = "Test du service Firefox sans screenshot #Test #Firefox"
                
                print("🔄 Tentative de post sans screenshot...")
                result = firefox_service.post_tweet(tweet_text)
                
                if result:
                    print(f"✅ Post réussi sans screenshot! ID: {result}")
                else:
                    print("❌ Échec du post sans screenshot")
                    
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()


def test_screenshot_integration():
    """Test de l'intégration screenshot dans le workflow."""
    print("\n🔧 Test de l'intégration screenshot dans le workflow")
    print("=" * 50)
    
    # Simuler le workflow principal
    from src.services.twitter_service import TwitterService
    
    twitter_service = TwitterService()
    
    # Créer un tweet de test avec screenshot
    test_text = "Test d'intégration screenshot dans le workflow #Test #Integration"
    
    # Chercher un screenshot
    screenshot_path = None
    screenshot_dir = Path("screenshots")
    
    if screenshot_dir.exists():
        screenshots = list(screenshot_dir.glob("*.png"))
        if screenshots:
            screenshot_path = str(screenshots[0])
            print(f"📸 Utilisation du screenshot: {screenshot_path}")
    
    print("🔄 Test du service Twitter avec fallback Firefox...")
    
    try:
        # Forcer le fallback Firefox en simulant un rate limit
        result = twitter_service._try_firefox_fallback(test_text, screenshot_path)
        
        if result:
            print(f"✅ Fallback Firefox réussi! ID: {result}")
        else:
            print("❌ Fallback Firefox échoué")
            
    except Exception as e:
        print(f"❌ Erreur lors du test d'intégration: {e}")


if __name__ == "__main__":
    print("🧪 Tests du service Firefox avec screenshots")
    print("=" * 60)
    
    # Test 1: Service Firefox direct
    test_firefox_with_screenshot()
    
    # Test 2: Intégration dans le workflow
    test_screenshot_integration()
    
    print("\n✅ Tests terminés!") 