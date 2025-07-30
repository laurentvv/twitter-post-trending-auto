# Active Context: SCHEDULER 30 MIN + FIREFOX FALLBACK OPTIMISÉ ✅

## Status : PRODUCTION READY + SCHEDULER 30 MINUTES + FALLBACK FIREFOX

Le bot Twitter GitHub est maintenant configuré avec un **scheduler toutes les 30 minutes** (09h00–00h00) et un fallback Firefox instancié uniquement en cas d'échec du service principal.

## Scheduler 30 Minutes
- ✅ **Fréquence** : Toutes les 30 minutes
- ✅ **Plage horaire** : 09h00 à 00h00 (France)
- ✅ **Retry automatique** : 3 tentatives par service
- ✅ **Fallback Firefox** : Instancié uniquement si nécessaire (pas de driver lancé inutilement)
- ✅ **Plus de slots** : Jusqu'à 30 tweets/jour possible (attention à vos quotas Twitter)

## Avantages du Nouveau Système
- 🛡️ **Ultra-robuste** : Fallback automatique, multi-provider IA, retry 3x
- ⏰ **Flexible** : Plage horaire large, fréquence ajustable
- 🚫 **Anti-rate limit** : Fallback Firefox si quota ou erreur API
- 🔄 **Sustainable** : Peut tourner indéfiniment sans intervention

## Système IA Multi-Provider
- ✅ **Gemini 1.5 Flash** : Provider principal (rapide, gratuit, fiable)
- ✅ **OpenRouter/Mistral** : Backup gratuit/payant
- ✅ **Ollama Local** : Dernier recours (qwen3:14b)

## Fonctionnalités Finales
- ✅ **GitHub Trending** : Récupération automatique des dépôts populaires
- ✅ **Screenshots** : Capture d'écran centrée sur README
- ✅ **IA Multi-Provider** : Fallback automatique pour résumés français
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
# Plage continue 09h00–00h00
if 9 <= current_hour < 24:
    return True  # Run bot
else:
    return False  # Skip
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