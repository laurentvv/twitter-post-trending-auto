@echo off
echo 🚀 GitHub Tweet Bot - Démarrage rapide
echo ======================================

REM Vérifier si l'environnement virtuel existe
if not exist ".venv\Scripts\activate.bat" (
    echo ❌ Environnement virtuel non trouvé
    echo.
    echo 🔧 Créer l'environnement virtuel:
    echo   setup_venv.bat
    echo.
    pause
    exit /b 1
)

REM Activer l'environnement virtuel
echo 🔧 Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat

REM Vérifier si les dépendances sont installées
python -c "import tweepy" 2>nul
if errorlevel 1 (
    echo 📦 Installation des dépendances...
    pip install -r requirements.txt
    echo ✅ Dépendances installées
)

echo.
echo 🎯 Choisir une option:
echo.
echo 1. Lancer le bot (post unique)
echo 2. Lancer le scheduler (mode production)
echo 3. Tester Firefox fallback
echo 4. Quitter
echo.
set /p choice="Votre choix (1-4): "

if "%choice%"=="1" (
    echo 🚀 Lancement du bot...
    python -m src.main
) else if "%choice%"=="2" (
    echo ⏰ Lancement du scheduler...
    python scheduler.py
) else if "%choice%"=="3" (
    echo 🧪 Test Firefox fallback...
    python test_firefox_fallback.py
) else if "%choice%"=="4" (
    echo 👋 Au revoir!
) else (
    echo ❌ Choix invalide
)

pause 