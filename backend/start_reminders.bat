@echo off
echo 🚀 DÉMARRAGE DU SYSTÈME DE RAPPELS AUTOMATIQUES
echo ================================================
echo.
echo 💡 Ce script lance le monitoring des rappels programmés
echo 💡 Pour arrêter: Ctrl+C
echo.

cd /d "%~dp0"

echo 🔄 Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat

echo.
echo 🚀 Lancement du monitoring des rappels...
python run_reminders_manual.py

pause
