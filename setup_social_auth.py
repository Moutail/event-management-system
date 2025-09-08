#!/usr/bin/env python
"""
🚀 SCRIPT DE CONFIGURATION AUTOMATIQUE - AUTHENTIFICATION SOCIALE
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """Affiche l'en-tête du script"""
    print("=" * 60)
    print("🔐 CONFIGURATION AUTOMATIQUE - AUTHENTIFICATION SOCIALE")
    print("=" * 60)
    print()

def check_environment():
    """Vérifie l'environnement de développement"""
    print("🔍 Vérification de l'environnement...")
    
    # Vérifier Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8+ requis")
        return False
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Vérifier Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js non trouvé")
            return False
    except FileNotFoundError:
        print("❌ Node.js non installé")
        return False
    
    # Vérifier npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()}")
        else:
            print("❌ npm non trouvé")
            return False
    except FileNotFoundError:
        print("❌ npm non installé")
        return False
    
    print()
    return True

def create_env_files():
    """Crée les fichiers .env avec des valeurs par défaut"""
    print("📝 Création des fichiers .env...")
    
    # Backend .env
    backend_env = """# 🔐 Configuration de l'authentification sociale côté backend

# Google OAuth2
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Facebook OAuth2
FACEBOOK_APP_ID=your-facebook-app-id-here
FACEBOOK_APP_SECRET=your-facebook-app-secret-here
FACEBOOK_REDIRECT_URI=http://localhost:3000/auth/facebook/callback

# Configuration générale
SOCIAL_AUTH_ENABLED=True
SOCIAL_AUTH_SUCCESS_URL=/dashboard
SOCIAL_AUTH_FAILURE_URL=/login?error=social_auth_failed

# Mode développement
DEBUG=True
SOCIAL_AUTH_DEBUG=True
"""
    
    # Frontend .env
    frontend_env = """# 🔐 Configuration de l'authentification sociale côté frontend

# Google OAuth2
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id-here
REACT_APP_GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Facebook OAuth2
REACT_APP_FACEBOOK_APP_ID=your-facebook-app-id-here
REACT_APP_FACEBOOK_REDIRECT_URI=http://localhost:3000/auth/facebook/callback

# Configuration générale
REACT_APP_SOCIAL_AUTH_ENABLED=true
REACT_APP_SOCIAL_AUTH_SUCCESS_URL=/dashboard
REACT_APP_SOCIAL_AUTH_FAILURE_URL=/login?error=social_auth_failed

# Mode développement
REACT_APP_DEBUG_MODE=true
"""
    
    # Créer le fichier backend/.env
    backend_path = Path("backend/.env")
    if not backend_path.exists():
        backend_path.parent.mkdir(exist_ok=True)
        with open(backend_path, 'w', encoding='utf-8') as f:
            f.write(backend_env)
        print("✅ backend/.env créé")
    else:
        print("ℹ️ backend/.env existe déjà")
    
    # Créer le fichier frontend/.env
    frontend_path = Path("frontend/.env")
    if not frontend_path.exists():
        frontend_path.parent.mkdir(exist_ok=True)
        with open(frontend_path, 'w', encoding='utf-8') as f:
            f.write(frontend_env)
        print("✅ frontend/.env créé")
    else:
        print("ℹ️ frontend/.env existe déjà")
    
    print()

def install_dependencies():
    """Installe les dépendances nécessaires"""
    print("📦 Installation des dépendances...")
    
    # Backend
    print("🔧 Installation des dépendances backend...")
    try:
        os.chdir("backend")
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dépendances backend installées")
        os.chdir("..")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation backend: {e}")
        return False
    
    # Frontend
    print("🔧 Installation des dépendances frontend...")
    try:
        os.chdir("frontend")
        subprocess.run(['npm', 'install'], check=True)
        print("✅ Dépendances frontend installées")
        os.chdir("..")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur installation frontend: {e}")
        return False
    
    print()
    return True

def run_migrations():
    """Exécute les migrations Django"""
    print("🗄️ Exécution des migrations...")
    
    try:
        os.chdir("backend")
        subprocess.run(['python', 'manage.py', 'makemigrations'], check=True)
        subprocess.run(['python', 'manage.py', 'migrate'], check=True)
        print("✅ Migrations exécutées")
        os.chdir("..")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur migrations: {e}")
        return False
    
    print()
    return True

def print_next_steps():
    """Affiche les prochaines étapes"""
    print("🎯 PROCHAINES ÉTAPES OBLIGATOIRES:")
    print("=" * 50)
    print()
    print("1️⃣ **CONFIGURER GOOGLE OAUTH2:**")
    print("   - Suivez le guide: GOOGLE_OAUTH2_SETUP.md")
    print("   - Créez un projet Google Cloud")
    print("   - Activez l'API Google+ API")
    print("   - Créez des identifiants OAuth2")
    print()
    print("2️⃣ **CONFIGURER FACEBOOK OAUTH2:**")
    print("   - Suivez le guide: FACEBOOK_OAUTH2_SETUP.md")
    print("   - Créez une application Facebook")
    print("   - Ajoutez le produit Facebook Login")
    print()
    print("3️⃣ **METTRE À JOUR LES FICHIERS .env:**")
    print("   - Remplacez les valeurs par défaut par vos vraies clés")
    print("   - Backend: backend/.env")
    print("   - Frontend: frontend/.env")
    print()
    print("4️⃣ **TESTER L'AUTHENTIFICATION:**")
    print("   - Démarrez le backend: cd backend && python manage.py runserver 8001")
    print("   - Démarrez le frontend: cd frontend && npm start")
    print("   - Testez la connexion via Google/Facebook")
    print()
    print("📚 **GUIDES DISPONIBLES:**")
    print("   - GOOGLE_OAUTH2_SETUP.md")
    print("   - FACEBOOK_OAUTH2_SETUP.md")
    print("   - SOCIAL_AUTH_SETUP.md")
    print("   - SOCIAL_AUTH_README.md")
    print()

def main():
    """Fonction principale"""
    print_header()
    
    if not check_environment():
        print("❌ Environnement non compatible. Arrêt du script.")
        return
    
    create_env_files()
    
    if not install_dependencies():
        print("❌ Erreur lors de l'installation des dépendances.")
        return
    
    if not run_migrations():
        print("❌ Erreur lors des migrations.")
        return
    
    print("🎉 CONFIGURATION AUTOMATIQUE TERMINÉE !")
    print()
    print_next_steps()

if __name__ == "__main__":
    main()









