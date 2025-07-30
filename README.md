# Twitter Post Trending Auto

Ce bot automatise la publication sur Twitter en récupérant les dépôts tendance de GitHub, en générant un résumé et des fonctionnalités clés à l'aide d'une IA, et en les publiant avec une capture d'écran.

## Fonctionnalités

- Récupère les dépôts GitHub tendance.
- Utilise une IA multi-provider (Gemini, OpenRouter, Mistral, Ollama) pour résumer les READMEs et extraire les fonctionnalités clés.
- Prend une capture d'écran de la page du dépôt (Playwright).
- Poste un tweet principal avec le résumé et la capture d'écran.
- Poste une réponse avec les fonctionnalités clés.
- Utilise **Selenium avec Firefox** comme fallback automatique en cas de rate limit ou d'échec API Twitter.
- Planificateur (`scheduler.py`) pour exécuter le bot automatiquement toutes les 30 minutes de 09h00 à 00h00.

## Prérequis

1. **Python 3.11+**
2. **API IA** : Gemini (gratuit) + OpenRouter/Mistral (backup) + Ollama (local)
3. **Compte Twitter Developer** avec OAuth 1.0a activé
4. **Firefox** avec profil configuré (pour le fallback)

## Installation rapide

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

## Configuration

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

### Workflow automatique

Le bot exécute automatiquement :

1. **📊 Récupération** des 20 dépôts GitHub trending
2. **🔍 Filtrage** des dépôts non encore postés
3. **���� Capture** d'écran du README
4. **🤖 Génération** du résumé IA en français (multi-provider, fallback automatique)
5. **🐦 Publication** du tweet principal + thread
6. **🦊 Fallback Firefox** si rate limit ou échec API Twitter (après 3 tentatives)
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
- **Échec API Twitter après 3 tentatives**

Le service Firefox n'est instancié **que si nécessaire** (pas de lancement inutile du driver).

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

- **Fréquence** : Toutes les 30 minutes
- **Heures actives** : 09h00 à 00h00 (France)
- **Limite quotidienne** : Dépend du nombre de slots (jusqu'à 30 tweets/jour max)
- **Retry automatique** : 3 tentatives par service
- **Fallback Firefox** : Automatique en cas de rate limit ou d'échec API

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
📅 Schedule: Every 30 minutes
⏰ Active hours: 09h00 to 00h00 (France time)
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
```

## Automatisation Firefox

Le bot utilise `src/services/firefox_twitter_service.py` pour interagir avec Twitter.

- **Authentification**: Il repose sur les cookies et la session stockés dans le profil Firefox fourni. **Vous devez être connecté à Twitter dans ce profil Firefox.**
- **Robustesse**: Le service utilise une combinaison de pauses fixes (`time.sleep`) et de fonctions d'attente personnalisées pour trouver les éléments, offrant un équilibre entre vitesse et fiabilité. Il inclut des mécanismes de secours comme un clic JavaScript si un clic standard est intercepté.
- **Dépendances**: Il utilise `selenium` et `webdriver-manager`. Ce dernier téléchargera automatiquement le `geckodriver` correct pour votre version de Firefox.

### Tester le service Firefox

Vous pouvez tester manuellement si l'automatisation Firefox fonctionne correctement en exécutant :
`python test_firefox_real_post.py`

## Planificateur (`scheduler.py`)

Le script `scheduler.py` est le point d'entrée pour exécuter le bot automatiquement.

- **Logique**: Il exécute la logique principale du bot (`src/main.py`) toutes les 30 minutes, uniquement entre 09h00 et 00h00.
- **Utilisation**: Pour démarrer le bot et le faire fonctionner selon le planning, exécutez simplement :
  `python scheduler.py`
