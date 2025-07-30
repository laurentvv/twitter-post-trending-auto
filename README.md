# Twitter Post Trending Auto

Ce bot automatise la publication sur Twitter en récupérant les dépôts tendance de GitHub, en générant un résumé et des fonctionnalités clés à l'aide d'une IA, et en les publiant avec une capture d'écran.

## Fonctionnalités

- Récupère les dépôts GitHub tendance.
- Utilise une IA (via Ollama) pour résumer les READMEs et extraire les fonctionnalités clés.
- Prend une capture d'écran de la page du dépôt.
- Poste un tweet principal avec le résumé et la capture d'écran.
- Poste une réponse avec les fonctionnalités clés.
- Utilise **Selenium avec Firefox** pour une automatisation robuste du navigateur, en s'appuyant sur un profil utilisateur réel pour l'authentification.
- Inclut un **planificateur (`scheduler`)** pour exécuter le bot automatiquement aux heures configurées.

## Structure du Projet


=======
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
.
├── img/                  # Captures d'écran et images pour les tweets
├── src/
│   ├── core/             # Composants principaux (config, logger)
│   ├── services/         # Services (GitHub, AI, Firefox)
│   └── main.py           # Logique principale du workflow
├── .amazonq/             # Fichier de mémoire pour l'assistant IA
├── config.json           # Fichier de configuration principal
├── scheduler.py          # Script pour exécuter le bot sur un planning
└── test_firefox_real_post.py # Script de test manuel pour le service Firefox
```

## Configuration (`config.json`)

Tous les paramètres du bot sont gérés dans `config.json`. La partie la plus importante est la configuration de `firefox_service`.

```json
{
  "firefox_service": {
    "enabled": true,
    "profile_path": "C:\\Users\\VotreUtilisateur\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\votre-profil.default-release",
    "headless": true,
    "timeout": 30,
    "retry_attempts": 3,
    "wait_between_actions": 2
  }
}
```

- **`enabled`**: Mettre à `true` pour utiliser l'automatisation Firefox.
- **`profile_path`**: **Crucial**. Vous devez fournir le chemin complet vers votre répertoire de profil Firefox. Le bot utilise ce profil pour être déjà connecté à Twitter.
- **`headless`**: Mettre à `true` pour exécuter Firefox en arrière-plan sans fenêtre visible. Mettre à `false` pour le débogage.

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

- **Logique**: Il exécute la logique principale du bot (`src/main.py`) à des heures précises (9h00, 13h00, 17h00, 21h00). Il vérifie au début de chaque heure s'il doit lancer le bot.
- **Utilisation**: Pour démarrer le bot et le faire fonctionner selon le planning, exécutez simplement :
  `python scheduler.py`