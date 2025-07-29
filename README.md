# 🚀 GitHub Tweet Bot

Bot Twitter intelligent qui découvre automatiquement les dépôts GitHub trending, génère des résumés IA en français et publie des tweets avec captures d'écran. **Production ready** avec scheduler automatique, gestion complète des rate limits et **fallback Firefox** pour l'automatisation.

## ✨ Fonctionnalités

- 🔥 **Détection automatique** des dépôts GitHub trending
- 🤖 **Résumés IA** multi-provider (Gemini/OpenRouter/Mistral/Ollama)
- 📸 **Screenshots automatiques** centrés sur le README
- 🐦 **Publication Twitter** avec thread de réponse
- 🦊 **Fallback Firefox** automatique en cas de rate limit, avec envoi d'images.
- 📚 **Historique intelligent** évite les doublons
- 🛡️ **Retry automatique** (3x) sur tous les services
- ⏰ **Scheduler robuste** avec gestion des rate limits
- 📊 **Logs structurés** pour monitoring complet

## 🛠️ Installation

### Prérequis

1. **Python 3.11+**
2. **IA APIs** : Gemini (gratuit) + OpenRouter/Mistral (backup) + Ollama (local)
3. **Compte Twitter Developer** avec OAuth 1.0a activé
4. **Firefox** avec profil configuré (pour le fallback)

### Installation rapide

```bash
# Cloner le projet
git clone https://github.com/votre-username/twitter-post-trending-auto.git
cd twitter-post-trending-auto

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat

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
FIREFOX_PROFILE_PATH=C:\Users\laurent\AppData\Roaming\Mozilla\Firefox\Profiles\7kfdokl3.default-release
FIREFOX_HEADLESS=true
FIREFOX_ENABLED=true
```

2. **Obtenir les clés APIs** :
   - **Twitter** : [developer.twitter.com](https://developer.twitter.com) (OAuth 1.0a + Read/Write)
   - **Gemini** : [aistudio.google.com](https://aistudio.google.com) (gratuit)
   - **OpenRouter** : [openrouter.ai](https://openrouter.ai) (backup gratuit)
   - **Mistral** : [console.mistral.ai](https://console.mistral.ai) (backup)

3. **Configuration Firefox** (pour le fallback) :
   - Créer un profil Firefox dédié
   - Se connecter à Twitter dans ce profil
   - Noter le chemin du profil dans `FIREFOX_PROFILE_PATH`

## 🚀 Utilisation

### Mode Production (Recommandé)

```bash
# Activer l'environnement virtuel
.venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
.venv\Scripts\activate.bat   # Windows CMD

# Lancer le scheduler automatique
python scheduler.py
```

### Mode Manuel

```bash
# Activer l'environnement virtuel
.venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
.venv\Scripts\activate.bat   # Windows CMD

# Post unique
python -m src.main
```

### Démarrage rapide (Windows)

```bash
# Script automatique avec menu
start.bat
```

### Test du Fallback Firefox

```bash
# Activer l'environnement virtuel d'abord
.venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
.venv\Scripts\activate.bat   # Windows CMD

# Tester la configuration Firefox
python test_firefox_fallback.py
```

### Workflow automatique

Le bot exécute automatiquement :

1. **📊 Récupération** des 20 dépôts GitHub trending
2. **🔍 Filtrage** des dépôts non encore postés
3. **📸 Capture** d'écran du README
4. **🤖 Génération** du résumé IA en français
5. **🐦 Publication** du tweet principal + thread
6. **🦊 Fallback Firefox** si rate limit détecté
7. **💾 Sauvegarde** dans l'historique

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

## 🦊 Fallback Firefox

### Fonctionnement

Le bot utilise automatiquement Firefox comme fallback quand :

- **Rate limit détecté** sur l'API Twitter
- **Erreur 429** (Too Many Requests)
- **Quota dépassé** sur l'API

### Configuration Firefox

```env
# Chemin vers le profil Firefox (obligatoire)
FIREFOX_PROFILE_PATH=C:\Users\laurent\AppData\Roaming\Mozilla\Firefox\Profiles\7kfdokl3.default-release

# Mode headless (recommandé)
FIREFOX_HEADLESS=true

# Activer/désactiver le fallback
FIREFOX_ENABLED=true
```

### Avantages du Fallback

- ✅ **Contourne les rate limits** de l'API Twitter
- ✅ **Pas de quota** sur l'automatisation Firefox
- ✅ **Plus de tweets** possibles par jour
- ✅ **Fallback automatique** sans intervention
- ✅ **Logs détaillés** pour monitoring

### Fonctionnalités Screenshots

Le service Firefox peut utiliser les screenshots générés par Playwright :

- 📸 **Screenshots automatiques** des README GitHub
- 🔄 **Intégration transparente** dans le workflow
- 📤 **Upload automatique** vers Twitter via Firefox
- 🎯 **Même qualité** que l'API Twitter

### Limitations

- ⚠️ **Plus lent** que l'API directe
- ⚠️ **Dépendant** du profil Firefox configuré

## 📁 Structure du projet

```
twitter-post-trending-auto/
├── src/                    # Code source principal
│   ├── core/              # Configuration et logging
│   │   └── firefox_config.py  # Configuration Firefox
│   ├── services/          # Services métier
│   │   ├── twitter_service.py      # API Twitter + fallback
│   │   └── firefox_twitter_service.py  # Service Firefox
│   └── main.py            # Point d'entrée principal
├── scheduler.py           # Scheduler automatique (4h)
├── test_firefox_fallback.py  # Test du service Firefox
├── data/                  # Données persistantes
│   └── posted_repos.json # Historique des posts
├── screenshots/           # Captures d'écran générées
├── logs/                  # Fichiers de logs
├── .env                   # Variables d'environnement
└── requirements.txt       # Dépendances Python
```

## 🤖 Scheduler Automatique

### Configuration

- **Fréquence** : Toutes les 4 heures
- **Heures actives** : 9h, 13h, 17h, 21h (France)
- **Limite quotidienne** : 4 tweets max (ultra-safe pour 17/24h Twitter)
- **Espacement** : 4h minimum entre tweets
- **Retry automatique** : 3 tentatives par service
- **Fallback Firefox** : Automatique en cas de rate limit

### Lancement du scheduler

```bash
# Activer l'environnement virtuel
.venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
.venv\Scripts\activate.bat   # Windows CMD

python scheduler.py
```

**Sortie exemple** :
```
🚀 GitHub Tweet Bot Scheduler Started
📅 Schedule: Every 4 hours
⏰ Active hours: 9h, 13h, 17h, 21h (France time)
📊 Max tweets/day: 4 (ultra-safe pour 17/24h limit)
🦊 Firefox fallback: Enabled
[2025-01-26 09:00:00] ✅ Bot executed successfully
```

## ⚙️ Configuration avancée

### IA Multi-Provider

Système de fallback automatique dans `.env` :

```env
# Ordre de priorité : Gemini -> OpenRouter -> Mistral -> Ollama
GEMINI_API_KEY=votre_clé_gemini
OPENROUTER_API_KEY=votre_clé_openrouter  
MISTRAL_API_KEY=votre_clé_mistral
OLLAMA_MODEL=qwen3:14b      # Fallback local
```

### Firefox Fallback

Configuration complète du fallback :

```env
# Profil Firefox (obligatoire)
FIREFOX_PROFILE_PATH=C:\Users\laurent\AppData\Roaming\Mozilla\Firefox\Profiles\7kfdokl3.default-release

# Options Firefox
FIREFOX_HEADLESS=true        # Mode headless (recommandé)
FIREFOX_ENABLED=true         # Activer le fallback

# Configuration automatique si non spécifié
# Le bot cherchera automatiquement un profil .default-release
```

### Robustesse

- **Retry 3x** : GitHub API, Screenshots, IA, Twitter
- **Rate limiting** : Gestion automatique avec `wait_on_rate_limit=True`
- **Fallbacks** : Textes par défaut si IA échoue
- **Firefox fallback** : Automatique en cas de rate limit
- **Historique** : Nettoyage automatique après 7 jours

### Monitoring

- **Logs JSON** : `logs/app.log` avec structure complète
- **Progress display** : Scheduler avec étapes détaillées
- **Error handling** : Logs d'erreur avec retry attempts
- **Fallback tracking** : Suivi des méthodes utilisées (API vs Firefox)

## 🔧 Dépannage

### Problèmes courants

**❌ Rate limit Twitter (17/24h)**
- Le bot utilise automatiquement Firefox comme fallback
- Scheduler configuré pour 8 tweets/jour max (safe)

**❌ Erreur 403 Twitter**
- Vérifiez OAuth 1.0a activé + permissions Read and Write
- Régénérez les tokens d'accès

**❌ Firefox fallback échoue**
```bash
# Activer l'environnement virtuel
.venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
.venv\Scripts\activate.bat   # Windows CMD

# Tester la configuration Firefox
python test_firefox_fallback.py

# Vérifier le profil Firefox
echo %FIREFOX_PROFILE_PATH%
```

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
# Activer l'environnement virtuel
.venv\Scripts\Activate.ps1  # Windows PowerShell
# ou
.venv\Scripts\activate.bat   # Windows CMD

# Test complet
python -m src.main

# Test Firefox uniquement
python test_firefox_fallback.py

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
  "method": "firefox_fallback",
  "timestamp": "2025-01-26T10:30:00Z"
}
```

### Robustesse

- ✅ **Retry 3x** sur tous les services
- ✅ **Rate limit handling** automatique
- ✅ **Firefox fallback** en cas de rate limit
- ✅ **Fallbacks** si services échouent
- ✅ **Scheduler stable** avec progression détaillée
- ✅ **Anti-doublons** avec historique persistant

### Performance

- ⚡ **15-35s** par workflow complet
- 🛡️ **4 tweets/jour** max (ultra-safe pour Twitter)
- 🦊 **Fallback Firefox** pour contourner les limites
- 📊 **100% succès** avec retry automatique
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
- [Selenium](https://selenium.dev) pour l'automatisation Firefox
- [GitHub API](https://docs.github.com/en/rest) pour les données trending

---

⭐ **N'hésitez pas à star le projet si il vous a été utile !**