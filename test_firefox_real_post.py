#!/usr/bin/env python3
"""
Test d'envoi d'un vrai tweet et sa réponse via le service Firefox.
"""

import os
import sys
import time
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Imports avec gestion des erreurs d'import
try:
    from services.firefox_twitter_service import FirefoxTwitterService
    from core.firefox_config import firefox_config
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("🔧 Tentative de correction...")
    
    # Ajouter le répertoire parent au path
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from src.services.firefox_twitter_service import FirefoxTwitterService
        from src.core.firefox_config import firefox_config
    except ImportError as e2:
        print(f"❌ Erreur d'import persistante: {e2}")
        sys.exit(1)


def test_firefox_real_post():
    """Test d'envoi d'un vrai tweet et sa réponse via Firefox."""
    
    print("🧪 Test d'envoi réel via Firefox")
    print("=" * 50)
    
    # Vérifier la configuration
    print("📋 Configuration Firefox:")
    config = firefox_config.get_config()
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    if not firefox_config.is_enabled():
        print("❌ Service Firefox désactivé")
        return False
    
    # Messages de test
    main_tweet = "La gestion des logs est cruciale pour la sécurité et la maintenance des systèmes. Quels outils utilisez-vous pour centraliser et analyser vos logs ? #SysAdmin #DevOps"
    reply_tweet = "Personnellement, j'utilise une combinaison de ELK Stack (Elasticsearch, Logstash, Kibana) pour la centralisation et l'analyse des logs. Et vous, quelles sont vos solutions préférées ?"
    
    print(f"\n📝 Tweet principal:")
    print(f"  {main_tweet}")
    print(f"\n💬 Réponse:")
    print(f"  {reply_tweet}")
    
    # Demander confirmation
    print("\n⚠️  ATTENTION: Ce test va poster de VRAIS tweets!")
    response = input("Continuer? (oui/non): ").lower().strip()
    
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Test annulé")
        return False
    
    try:
        # Initialiser le service Firefox
        print("\n🔧 Initialisation du service Firefox...")
        firefox_service = FirefoxTwitterService()
        
        # Poster le tweet principal
        print("\n🐦 Envoi du tweet principal...")
        main_tweet_id = firefox_service.post_tweet(main_tweet)
        
        if main_tweet_id:
            print(f"✅ Tweet principal envoyé! ID: {main_tweet_id}")
            
            # Attendre un peu avant la réponse
            print("⏳ Attente de 5 secondes avant la réponse...")
            time.sleep(5)
            
            # Poster la réponse
            print("\n💬 Envoi de la réponse...")
            reply_tweet_id = firefox_service.post_reply(main_tweet_id, reply_tweet)
            
            if reply_tweet_id:
                print(f"✅ Réponse envoyée! ID: {reply_tweet_id}")
                print("\n🎉 Test réussi! Vérifiez vos tweets sur Twitter.")
                return True
            else:
                print("❌ Échec de l'envoi de la réponse")
                return False
        else:
            print("❌ Échec de l'envoi du tweet principal")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False


def test_firefox_config_only():
    """Test de la configuration Firefox sans poster."""
    
    print("🔧 Test de configuration Firefox")
    print("=" * 40)
    
    # Vérifier la configuration
    print("📋 Configuration:")
    config = firefox_config.get_config()
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    if not firefox_config.is_enabled():
        print("❌ Service Firefox désactivé")
        return False
    
    try:
        # Tester l'initialisation du service
        print("\n🔧 Test d'initialisation du service...")
        firefox_service = FirefoxTwitterService()
        
        # Tester la navigation vers Twitter
        print("🌐 Test de navigation vers Twitter...")
        with firefox_service._get_driver() as driver:
            driver.get("https://twitter.com")
            time.sleep(3)
            
            # Vérifier que la page Twitter est chargée
            if "twitter" in driver.title.lower():
                print("✅ Navigation vers Twitter réussie")
                return True
            else:
                print("❌ Échec de la navigation vers Twitter")
                return False
                
    except Exception as e:
        print(f"❌ Erreur lors du test de configuration: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Test du service Firefox Twitter")
    print("=" * 50)
    
    # Menu de choix
    print("\nChoisir un test:")
    print("1. Test de configuration uniquement")
    print("2. Test d'envoi réel (ATTENTION: va poster!)")
    print("3. Quitter")
    
    choice = input("\nVotre choix (1-3): ").strip()
    
    if choice == "1":
        test_firefox_config_only()
    elif choice == "2":
        test_firefox_real_post()
    elif choice == "3":
        print("👋 Au revoir!")
    else:
        print("❌ Choix invalide") 