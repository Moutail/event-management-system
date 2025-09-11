#!/usr/bin/env bash
# Script de build pour Render

echo "🚀 Démarrage du build sur Render..."

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Appliquer les migrations
echo "🗄️ Application des migrations..."
python manage.py migrate

# Créer le super admin
echo "👑 Création du super admin..."
python manage.py create_superadmin

# Collecter les fichiers statiques
echo "📁 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "✅ Build terminé avec succès !"
