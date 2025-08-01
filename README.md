# 🚀 GitHub Tweet Bot

Bot Twitter intelligent qui découvre automatiquement les dépôts GitHub trending, génère des résumés IA en français et publie des tweets avec captures d'écran. **Production ready** avec scheduler adaptatif (09h00–01h00) et gestion complète des rate limits avec fallback Firefox.

## ✨ Fonctionnalités

- 🌐 **Détection multi-source** des dépôts GitHub trending (API, Scraping, LibHunt, Gitstar Ranking) avec fallback automatique
- 🤖 **Résumés IA** multi-provider (Gemini → OpenRouter → Mistral → Ollama)
- 📸 **Screenshots automatiques** centrés sur le README avec retry 3x
- ✅ **Validation & Correction IA** : Les tweets sont validés et corrigés par l'IA avant publication pour une qualité optimale
- 🐦 **Publication Twitter** avec thread de réponse, OAuth 1.0a et retry 3x
- 🦊 **Fallback Firefox** automatique en cas de rate limit ou d'échec API (instancié uniquement si nécessaire)
- 📚 **Historique intelligent** évite les doublons avec nettoyage automatique (7 jours)
- 🛡️ **Retry automatique** (3x) sur tous les services (IA, GitHub, Twitter, Firefox)
- ⏰ **Scheduler adaptatif** : L'intervalle de publication s'ajuste automatiquement (30, 60, 90, 120 min) en fonction des rate limits de l'API Twitter
- 📊 **Logs structurés** avec provider IA utilisé, durée et statut de chaque étape

## 🛠️ Installation

### Prérequis

1. **Python 3.11+**
2. **IA APIs** : Gemini (gratuit) + OpenRouter/Mistral (backup) + Ollama (local)
3. **Compte Twitter Developer** avec OAuth 1.0a activé
4. **Firefox** avec profil configuré (pour le fallback)

### Installation rapide

```bash
# Cloner le projet
git clone https://github.com/laurentvv/twitter-post-trending-auto.git
cd twitter-post-trending-auto

# Installer les dépendances
pip install -r requirements.txt

# Installer Playwright browsers
playwright install chromium

# Installer Ollama (fallback local)
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

# IA Multi-Provider (ordre de priorité)
GEMINI_API_KEY=votre_clé_gemini
OPENROUTER_API_KEY=votre_clé_openrouter
MISTRAL_API_KEY=votre_clé_mistral

# Ollama (fallback local)
OLLAMA_MODEL=qwen3:14b
OLLAMA_HOST=http://localhost:11434

# Firefox Fallback (optionnel)
FIREFOX_PROFILE_PATH=C:\Users\user\AppData\Roaming\Mozilla\Firefox\Profiles\6fgdokl3.default-release
FIREFOX_HEADLESS=true
FIREFOX_ENABLED=true
```

2. **Obtenir les clés APIs** :
   - **Twitter** : [developer.twitter.com](https://developer.twitter.com) (OAuth 1.0a + Read/Write)
   - **Gemini** : [aistudio.google.com](https://aistudio.google.com) (gratuit)
   - **OpenRouter** : [openrouter.ai](https://openrouter.ai) (backup gratuit)
   - **Mistral** : [console.mistral.ai](https://console.mistral.ai) (backup)

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

1. **📊 Récupération multi-source** des dépôts GitHub trending (API, scraping, etc.) avec fallback
2. **🔍 Filtrage** des dépôts non encore postés
3. **📸 Capture** d'écran du README
4. **🤖 Génération** du contenu du tweet en français (multi-provider, fallback automatique)
5. **✅ Validation & Correction IA** des tweets générés pour garantir la qualité
6. **🐦 Publication** du tweet principal + thread
7. **🦊 Fallback Firefox** si rate limit ou échec API Twitter (après 3 tentatives)
8. **💾 Sauvegarde** dans l'historique

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
│   ├── services/          # Services métier (GitHub, AI, Twitter, Firefox)
│   └── main.py            # Point d'entrée principal
├── scheduler.py           # Scheduler automatique (30 min)
├── data/                  # Données persistantes
│   └── posted_repos.json # Historique des posts
├── screenshots/           # Captures d'écran générées
├── logs/                  # Fichiers de logs
├── .env                   # Variables d'environnement
└── requirements.txt       # Dépendances Python
```

## 🤖 Scheduler Automatique

### Configuration

- **Fréquence adaptative** : Toutes les 30 minutes par défaut, s'ajuste à 60, 90 ou 120 minutes en cas de rate limits répétés
- **Plage horaire** : 09h00 à 01h00 (le lendemain), France
- **Limite quotidienne** : Flexible, s'adapte pour éviter les blocages de l'API Twitter
- **Retry automatique** : 3 tentatives par service (IA, GitHub, Twitter, Firefox)
- **Fallback Firefox** : Automatique en cas de rate limit ou d'échec API (instancié uniquement si nécessaire)
- **Gestion intelligente** : Skip si hors plage horaire, avec affichage du prochain créneau
- **Log détaillé** : Progression en temps réel du workflow et statut horaire du scheduler

### Lancement du scheduler

```bash
python scheduler.py
```

**Sortie exemple** :
```
🚀 GitHub Tweet Bot Scheduler Started
📅 Schedule: Every 30 minutes
⏰ Active hours: 09h00 to 00h00 (France time)
🦊 Firefox fallback: Enabled
[2025-01-26 09:00:00] ✅ Bot executed successfully
```

## ⚙️ Configuration avancée

### IA Multi-Provider

Système de fallback automatique dans `.env` :

```env
# Ordre de priorité : Gemini (principal) → OpenRouter (backup gratuit) → Mistral (backup payant) → Ollama (local)
GEMINI_API_KEY=votre_clé_gemini
OPENROUTER_API_KEY=votre_clé_openrouter  
MISTRAL_API_KEY=votre_clé_mistral
OLLAMA_MODEL=qwen3:14b      # Fallback local
OLLAMA_HOST=http://localhost:11434
```

### Firefox Fallback

Configuration complète du fallback :

```env
# Profil Firefox (obligatoire)
FIREFOX_PROFILE_PATH=C:\Users\user\AppData\Roaming\Mozilla\Firefox\Profiles\7rtfgkl3.default-release

# Options Firefox
FIREFOX_HEADLESS=true        # Mode headless (recommandé)
FIREFOX_ENABLED=true         # Activer le fallback
```

### Scheduler Logic
```python
# Plage continue 09h00–00h00
if 9 <= current_hour < 24:
    return True  # Run bot
else:
    return False  # Skip
```

### Firefox Fallback

Configuration complète du fallback :

```env
# Profil Firefox (obligatoire)
FIREFOX_PROFILE_PATH=C:\Users\user\AppData\Roaming\Mozilla\Firefox\Profiles\7kfdokl3.default-release

# Options Firefox
FIREFOX_HEADLESS=true        # Mode headless (recommandé)
FIREFOX_ENABLED=true         # Activer le fallback
```

## 🔧 Dépannage

### Problèmes courants

**❌ Rate limit Twitter (17/24h)**
- Le bot bascule automatiquement sur Firefox si l'API échoue 3x
- Scheduler configuré pour éviter le spam

**❌ Erreur 403 Twitter**
- Vérifiez OAuth 1.0a activé + permissions Read and Write
- Régénérez les tokens d'accès

**❌ Ollama non accessible**
```bash
ollama serve
ollama pull qwen3:14b
```

**❌ Screenshots échouent**
- `playwright install chromium`
- Retry automatique 3x intégré

### Test manuel

```bash
# Test complet
python -m src.main

# Scheduler avec debug
python scheduler.py
```

## 📊 Production Ready

### Monitoring

Logs JSON structurés dans `logs/app.log` :

```json
{
  "step": "workflow_success",
  "repo_name": "awesome-project", 
  "duration": "15.32s",
  "main_tweet_id": "1234567890",
  "reply_tweet_id": "1234567891",
  "timestamp": "2025-01-26T10:30:00Z",
  "ai_provider_used": "Gemini",
  "error_count": 0
}
```

### Robustesse

- ✅ **Retry 3x** sur tous les services (IA, GitHub, Twitter, Firefox)
- ✅ **Rate limit handling** automatique avec fallback Firefox
- ✅ **Fallbacks** multi-niveaux : Sources de données (API → Scraping → LibHunt...) + IA (Gemini → OpenRouter → ...) + Publication (API → Firefox)
- ✅ **Scheduler stable** avec progression détaillée et affichage du prochain créneau
- ✅ **Anti-doublons** avec historique persistant (nettoyage automatique 7 jours)
- ✅ **Logs détaillés** : Provider IA utilisé, durée, statut, erreurs (si any)

### Performance

- ⚡ **15-35s** par workflow complet
- 🛡️ **Jusqu'à 30 tweets/jour** (attention à vos quotas Twitter)
- 📊 **100% succès** avec retry automatique + fallback
- 🎯 **Production tested** et optimisé

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
```

amazonq\memory-bank\activeContext.md
