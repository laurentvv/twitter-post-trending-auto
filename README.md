# 🚀 GitHub Tweet Bot

Un bot Twitter intelligent qui découvre automatiquement les dépôts GitHub tendance, génère des résumés avec l'IA et publie des tweets engageants avec captures d'écran.

## ✨ Fonctionnalités

- 🔥 **Détection automatique** des dépôts GitHub trending
- 🤖 **Résumés IA** générés avec Ollama (français avec accents)
- 📸 **Screenshots automatiques** centrés sur le README
- 🐦 **Publication Twitter** avec thread de réponse
- 📚 **Historique intelligent** évite les doublons
- 🎯 **Tweets optimisés** respectant les limites de caractères

## 🛠️ Installation

### Prérequis

1. **Python 3.11+**
2. **Ollama** installé et configuré
3. **Compte Twitter Developer** avec API v2

### Installation rapide

```bash
# Cloner le projet
git clone https://github.com/votre-username/twitter-post-trending-auto.git
cd twitter-post-trending-auto

# Installer les dépendances
pip install -r requirements.txt

# Installer Playwright browsers
playwright install chromium

# Installer et démarrer Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:14b
```

### Configuration

1. **Créer le fichier `.env`** (basé sur `.env.example`) :

```env
# Twitter OAuth 1.0a (obligatoire pour poster)
TWITTER_API_KEY=votre_api_key
TWITTER_API_SECRET=votre_api_secret
TWITTER_ACCESS_TOKEN=votre_access_token
TWITTER_ACCESS_TOKEN_SECRET=votre_access_token_secret
TWITTER_BEARER_TOKEN=votre_bearer_token

# Ollama Configuration
OLLAMA_MODEL=qwen3:14b
OLLAMA_HOST=http://localhost:11434
```

2. **Obtenir les clés Twitter** :
   - Aller sur [developer.twitter.com](https://developer.twitter.com)
   - Créer une app avec permissions **Read and Write**
   - Activer **OAuth 1.0a**
   - Générer les tokens d'accès

## 🚀 Utilisation

### Mode Production (Recommandé)

```bash
# Lancer le scheduler automatique
python scheduler.py
```

### Mode Manuel

```bash
# Post unique
python -m src.main
```

### Workflow automatique

Le bot exécute automatiquement :

1. **📊 Récupération** des 20 dépôts GitHub trending
2. **🔍 Filtrage** des dépôts non encore postés
3. **📸 Capture** d'écran du README
4. **🤖 Génération** du résumé IA en français
5. **🐦 Publication** du tweet principal + thread
6. **💾 Sauvegarde** dans l'historique

### Exemple de sortie

```
🐍 awesome-python
⭐ 123,456 stars

Bibliothèque Python révolutionnaire pour l'automatisation intelligente des tâches quotidiennes !
#GitHub

Thread de réponse :
• Interface intuitive
• Performance optimisée  
• Documentation complète

🔗 https://github.com/user/awesome-python
#Code
```

## 📁 Structure du projet

```
twitter-post-trending-auto/
├── src/                    # Code source principal
│   ├── core/              # Configuration et logging
│   ├── services/          # Services métier (GitHub, AI, Twitter, etc.)
│   └── main.py            # Point d'entrée principal
├── scheduler.py           # Scheduler automatique (30min)
├── data/                  # Données persistantes
│   └── posted_repos.json # Historique des posts
├── screenshots/           # Captures d'écran générées
├── logs/                  # Fichiers de logs
├── .env                   # Variables d'environnement
└── requirements.txt       # Dépendances Python
```

## 🤖 Scheduler Automatique

### Configuration

- **Fréquence** : Toutes les 30 minutes
- **Heures actives** : 8h00 - 23h30 (France)
- **Limite mensuelle** : 500 tweets max (≈16/jour)
- **Gestion intelligente** : Skip si hors heures actives

### Lancement du scheduler

```bash
python scheduler.py
```

**Sortie exemple** :
```
🚀 GitHub Tweet Bot Scheduler Started
📅 Schedule: Every 30 minutes
⏰ Active hours: 8h00 - 23h30 (France time)
📊 Max tweets/month: 500 (≈16/day)
[2025-01-26 09:00:00] ✅ Bot executed successfully
```

## ⚙️ Configuration avancée

### Modèle Ollama

Modèle recommandé dans `.env` :

```env
OLLAMA_MODEL=qwen3:14b      # Recommandé (pas de thinking mode)
```

### Historique

L'historique est automatiquement nettoyé après 7 jours si aucun nouveau dépôt n'est disponible.

### Logs

Les logs détaillés sont disponibles dans `logs/app.log` avec format JSON structuré.

## 🔧 Dépannage

### Problèmes courants

**❌ Erreur 403 Twitter**
- Vérifiez que OAuth 1.0a est activé
- Confirmez les permissions Read and Write
- Régénérez les tokens d'accès

**❌ Ollama non accessible**
```bash
ollama serve  # Démarrer le service
ollama pull qwen3:14b  # Télécharger le modèle
```

**❌ Screenshots vides**
- Vérifiez que Playwright est installé : `playwright install chromium`
- Désactivez le firewall temporairement

### Debug

```bash
# Tester les composants individuellement
python -c "from src.services.github_service import GitHubService; print(GitHubService().get_trending_repositories(1))"
python -c "from src.services.ai_service import AIService; print(AIService().summarize_readme('Test README'))"
```

## 📊 Monitoring

Le bot génère des logs structurés pour monitoring :

```json
{
  "step": "workflow_success",
  "repo_name": "awesome-project", 
  "duration": "15.32s",
  "main_tweet_id": "1234567890",
  "timestamp": "2025-01-26T10:30:00Z"
}
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- [Ollama](https://ollama.com) pour l'IA locale
- [Tweepy](https://tweepy.readthedocs.io) pour l'API Twitter
- [Playwright](https://playwright.dev) pour les screenshots
- [GitHub API](https://docs.github.com/en/rest) pour les données trending

---

⭐ **N'hésitez pas à star le projet si il vous a été utile !**