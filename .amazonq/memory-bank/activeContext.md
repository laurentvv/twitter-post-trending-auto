# Active Context: ADAPTIVE SCHEDULER + AI QUALITY CONTROL ✅

## Status : PRODUCTION READY + ADAPTIVE SCHEDULER + AI VALIDATION

Le bot est maintenant doté d'un **scheduler adaptatif** (30-120 min) qui ajuste sa fréquence en fonction des rate limits de Twitter, et d'une **boucle de validation et correction par IA** pour garantir la qualité des tweets.

## Adaptive Scheduler
- ✅ **Fréquence adaptative** : 30, 60, 90, ou 120 min en fonction des erreurs de rate limit.
- ✅ **Plage horaire** : 09h00 à 01h00 (France, jour suivant inclus).
- ✅ **Priorisation Fallback** : Le scheduler peut décider de prioriser Firefox si des rate limits récents ont été détectés.
- ✅ **Monitoring Live** : Suivi en temps réel de l'exécution du bot.
- ✅ **Stabilité maximale** : Conçu pour tourner 24/7 sans intervention.

## Avantages du Nouveau Système
- 🛡️ **Ultra-robuste** : Fallbacks à tous les niveaux (sources de données, providers IA, publication).
- ✍️ **Qualité garantie** : Validation et correction des tweets par l'IA avant publication.
- 🌐 **Sources de données multiples** : Détection des tendances via API GitHub, scraping, API OSS Insight, et Gitstar Ranking.
- 🚫 **Anti-rate limit intelligent** : Le scheduler et le fallback Firefox gèrent les limites de l'API Twitter de manière proactive.
- 🔄 **Autonome** : Peut tourner indéfiniment sans intervention.

## Système IA Multi-Provider
- ✅ **Gemini 1.5 Flash** : Provider principal (rapide, gratuit, fiable)
- ✅ **OpenRouter/Mistral** : Backup gratuit/payant
- ✅ **Ollama Local** : Dernier recours (qwen3:14b)

## Fonctionnalités Finales
- ✅ **GitHub Trending Multi-Source** : Récupération automatique des dépôts via API, scraping et autres sources avec fallback.
- ✅ **Screenshots** : Capture d'écran centrée sur README
- ✅ **IA Multi-Provider** : Fallback automatique pour résumés français
- ✅ **Validation & Correction IA** : Qualité des tweets assurée par une passe de validation et correction par l'IA.
- ✅ **Twitter Posting** : Publication avec OAuth 1.0a, upload d'images, thread de réponse
- ✅ **Historique** : Système anti-doublons avec nettoyage automatique (7 jours)
- ✅ **Logs structurés** : Monitoring complet avec provider utilisé
- ✅ **Retry 3x** : Robustesse maximale sur tous les services

## Configuration
```env
# IA Multi-Provider (ordre de priorité)
GEMINI_API_KEY=...
OPENROUTER_API_KEY=...
MISTRAL_API_KEY=...
OLLAMA_MODEL=qwen3:14b
OLLAMA_HOST=http://localhost:11434

# Firefox fallback
FIREFOX_PROFILE_PATH=...
FIREFOX_HEADLESS=true
FIREFOX_ENABLED=true
```

## Scheduler Logic
```python
# Plage horaire de 09h00 à 01h00 (le lendemain)
def should_run_now():
    now = datetime.now()
    current_hour = now.hour
    # Autorisé de 9h à 1h du matin inclus
    return (current_hour >= 9) or (current_hour <= 1)
```

## Monitoring Amélioré
- **Status toutes les 30min** : Affichage du prochain créneau
- **Logs détaillés** : Provider IA utilisé + durée
- **Rate limit** : Fallback Firefox automatique

## Commandes de Production
```bash
python scheduler.py   # Mode production (recommandé)
python -m src.main    # Mode manuel
```

**Le bot est maintenant flexible, robuste, et prêt à tourner en production avec fallback automatique !** 🚀