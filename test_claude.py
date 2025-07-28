#!/usr/bin/env python3
"""
Test spécifique pour répondre au tweet ID: 1949789057959010691
"""

import os
import sys
import time
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from services.firefox_twitter_service import FirefoxTwitterService
    from core.firefox_config import firefox_config
except ImportError as e:
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from src.services.firefox_twitter_service import FirefoxTwitterService
        from src.core.firefox_config import firefox_config
    except ImportError as e2:
        print(f"❌ Erreur d'import: {e2}")
        sys.exit(1)


def test_reply_to_specific_tweet():
    """Test de réponse au tweet spécifique."""
    
    print("🧪 Test de réponse au tweet 1949789057959010691")
    print("=" * 50)
    
    # ID du tweet et texte de réponse
    tweet_id = "1949789057959010691"
    reply_text = "Personnellement, j'utilise une combinaison de ELK Stack (Elasticsearch, Logstash, Kibana) pour la centralisation et l'analyse des logs. Et vous, quelles sont vos solutions préférées ?"
    
    print(f"📌 Tweet ID: {tweet_id}")
    print(f"💬 Réponse: {reply_text}")
    
    # Vérifier la configuration
    config = firefox_config.get_config()
    print(f"\n📋 Mode headless: {config['headless']}")
    
    if not firefox_config.is_enabled():
        print("❌ Service Firefox désactivé")
        return False
    
    # Demander confirmation
    print("\n⚠️  ATTENTION: Ce test va poster une VRAIE réponse!")
    response = input("Continuer? (oui/non): ").lower().strip()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Test annulé")
        return False
    
    try:
        # Initialiser le service Firefox
        print("\n🔧 Initialisation du service Firefox...")
        firefox_service = FirefoxTwitterService()
        
        # Poster la réponse
        print("\n💬 Envoi de la réponse...")
        reply_result = firefox_service.post_reply(tweet_id, reply_text)
        
        if reply_result:
            print(f"✅ Réponse envoyée! Résultat: {reply_result}")
            print("\n🎉 Test réussi! Vérifiez la réponse sur Twitter/X.")
            return True
        else:
            print("❌ Échec de l'envoi de la réponse")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            firefox_service.close()
        except:
            pass


def test_reply_with_debug():
    """Test avec mode debug (non-headless)."""
    
    print("🔍 Test de réponse avec visualisation")
    print("=" * 40)
    
    # Modifier temporairement la config pour voir ce qui se passe
    config = firefox_config.get_config()
    original_headless = config["headless"]
    
    # Forcer le mode non-headless pour ce test
    config["headless"] = False
    
    try:
        result = test_reply_to_specific_tweet()
        return result
    finally:
        # Restaurer la config originale
        config["headless"] = original_headless


if __name__ == "__main__":
    print("🚀 Test de réponse Twitter/X")
    print("=" * 30)
    
    print("\nChoisir un test:")
    print("1. Test de réponse normal")
    print("2. Test de réponse avec visualisation (non-headless)")
    print("3. Quitter")
    
    choice = input("\nVotre choix (1-3): ").strip()
    
    if choice == "1":
        test_reply_to_specific_tweet()
    elif choice == "2":
        test_reply_with_debug()
    elif choice == "3":
        print("👋 Au revoir!")
    else:
        print("❌ Choix invalide")