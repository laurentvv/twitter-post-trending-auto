# GitHub Tweet Bot

Ce bot Twitter recherche les dépôts GitHub tendance, génère un résumé à l'aide de l'IA et publie un tweet avec une capture d'écran du dépôt.

## 🚀 Utilisation

### Installation

1.  **Installer Ollama**
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```

2.  **Télécharger Qwen3:14b**
    ```bash
    ollama pull qwen3:14b
    ```

3.  **Installer les dépendances Python**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Remplir `.env` avec vos clés Twitter**
    Créez un fichier `.env` à la racine du projet et ajoutez vos clés API Twitter en vous basant sur le fichier `.env.example`.

5.  **Lancer le bot**
    ```bash
    python src/main.py
    ```

## 🚀 Guide pas à pas pour créer ton app Twitter

### Étape 1 : Créer un compte développeur

1. Rends-toi sur [https://developer.twitter.com](https://developer.twitter.com)
2. Clique sur **"Apply for a developer account"**
3. Choisis le type de compte : **"Hobbyist"** → **"Student or enthusiast"** (si c'est pour apprendre/personnel)
4. Réponds aux questions :
   - Nom de ton projet : *"Tweet GitHub Projects"*
   - Description : *"Automatiser des tweets à partir de dépôts GitHub"*
   - Utilisation de l'API : *"Post tweets with images and replies"*

⚠️ Twitter peut mettre quelques heures à valider ton compte.

---

### Étape 2 : Créer une application

1. Une fois approuvé, va dans **"Dashboard"** → **"Create App"**
2. Nom de l'app : par exemple `GitHubTweetBot`
3. Tu obtiens alors :
   - **API Key** (Consumer Key)
   - **API Secret Key** (Consumer Secret)

---

### Étape 3 : Configurer les permissions

1. Dans l'onglet **"App settings"** → **"User authentication settings"**
2. Active **"OAuth 1.0a"**
3. Coche :
   - **Read**
   - **Write**
4. Définis le **"Callback URI"** comme : `http://localhost`

---

### Étape 4 : Générer les tokens

1. Toujours dans **"Keys and tokens"**
2. Clique sur **"Generate"** pour :
   - **Access Token and Secret**
3. Note bien ces 4 éléments :

```env
TWITTER_API_KEY = "xxx"
TWITTER_API_SECRET = "yyy"
TWITTER_ACCESS_TOKEN = "zzz"
TWITTER_ACCESS_TOKEN_SECRET = "aaa"
```

> ⚠️ Garde ces clés **secrètes** ! Ne les publie jamais.

---

### Étape 5 : Obtenir le Bearer Token

1. Dans le même onglet, clique sur **"Generate"** pour le **Bearer Token**
2. Tu auras ainsi les 5 variables nécessaires :

```env
TWITTER_BEARER_TOKEN = "bbb"
```

## 📁 Structure du Projet

```
github-tweet-bot/
├── .env                    # Variables d'environnement
├── .gitignore             # Fichiers à ignorer
├── requirements.txt       # Dépendances
├── config/
│   └── settings.py        # Configuration globale
├── src/
│   ├── __init__.py
│   ├── main.py           # Point d'entrée principal
│   ├── github_analyzer.py # Analyse des dépôts GitHub
│   ├── screenshot.py     # Capture d'écran
│   ├── ai_summarizer.py  # Résumé avec IA locale
│   ├── twitter_bot.py    # Gestion des tweets
│   ├── scheduler.py      # Planification
│   └── utils.py          # Fonctions utilitaires
├── data/
│   └── trending_repos.json # Dépôts tendance
├── logs/
│   └── app.log           # Logs de l'application
└── README.md             # Documentation
```
