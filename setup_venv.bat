@echo off
echo 🐍 Création de l'environnement virtuel...

REM Créer l'environnement virtuel
python -m venv .venv

echo ✅ Environnement virtuel créé dans .venv/
echo.
echo 🔧 Pour activer l'environnement virtuel:
echo.
echo Windows (PowerShell):
echo   .venv\Scripts\Activate.ps1
echo.
echo Windows (CMD):
echo   .venv\Scripts\activate.bat
echo.
echo 🚀 Pour installer les dépendances:
echo   pip install -r requirements.txt
echo.
echo 🎯 Pour lancer le bot:
echo   python -m src.main
echo.
echo 🧪 Pour tester Firefox:
echo   python test_firefox_fallback.py
echo.
pause 