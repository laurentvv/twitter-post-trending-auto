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