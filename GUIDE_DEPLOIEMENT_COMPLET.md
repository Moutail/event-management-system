# 🚀 Guide de Déploiement Complet - Event Management System

## 📋 Vue d'ensemble

Ce guide vous accompagne pour déployer votre système de gestion d'événements sur :
- **Backend** : Render (Django + Celery + PostgreSQL)
- **Frontend** : Vercel (React)
- **Mails automatiques** : Intégrés dans Render

## 🏗️ Architecture de Production

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Render        │    │   Services      │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   Externes      │
│                 │    │                 │    │                 │
│ • React App     │    │ • Django API    │    │ • Gmail SMTP    │
│ • Material-UI   │    │ • Celery Worker │    │ • Stripe        │
│ • PWA Ready     │    │ • Celery Beat   │    │ • Twilio SMS    │
│                 │    │ • PostgreSQL    │    │ • Google OAuth  │
└─────────────────┘    └─────────────────┘    │ • Facebook OAuth│
                                              │ • YouTube API   │
                                              │ • Zoom API      │
                                              └─────────────────┘
```

## 🚀 Étape 1 : Préparation du Projet

### 1.1 Structure des Fichiers
Votre projet doit avoir cette structure :
```
event-management-system/
├── backend/
│   ├── event_management/
│   │   ├── settings.py
│   │   ├── settings_production.py  # ✅ Nouveau
│   │   └── wsgi.py
│   ├── requirements.txt            # ✅ Mis à jour
│   ├── render.yaml                 # ✅ Nouveau
│   ├── Procfile                    # ✅ Nouveau
│   ├── runtime.txt                 # ✅ Nouveau
│   ├── start_production_services.py # ✅ Nouveau
│   └── migrate_database.py         # ✅ Nouveau
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vercel.json                 # ✅ Nouveau
│   └── env.production              # ✅ Nouveau
└── ENVIRONMENT_VARIABLES.md        # ✅ Nouveau
```

### 1.2 Configuration des Services Externes

#### Gmail SMTP
1. Allez sur https://myaccount.google.com/apppasswords
2. Créez un mot de passe d'application
3. Notez ce mot de passe (ex: `abcd efgh ijkl mnop`)

#### Stripe
1. Créez un compte sur https://stripe.com
2. Récupérez vos clés API de production
3. Notez `pk_live_...` et `sk_live_...`

#### Twilio (SMS)
1. Créez un compte sur https://twilio.com
2. Achetez un numéro de téléphone
3. Notez Account SID, Auth Token et numéro

#### Google OAuth2
1. Allez sur https://console.developers.google.com
2. Créez un projet et activez Google+ API
3. Créez des identifiants OAuth2
4. Ajoutez les domaines autorisés

#### Facebook OAuth2
1. Allez sur https://developers.facebook.com
2. Créez une application
3. Ajoutez le produit "Facebook Login"
4. Configurez les domaines autorisés

## 🚀 Étape 2 : Déploiement Backend sur Render

### 2.1 Création du Projet Render

1. **Connectez-vous à Render** : https://render.com
2. **Cliquez sur "New +"** → **"Web Service"**
3. **Connectez votre repository GitHub**
4. **Sélectionnez le dossier `backend`**

### 2.2 Configuration du Service Web

```yaml
Name: event-management-backend
Environment: Python 3
Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
Start Command: gunicorn event_management.wsgi:application
Django Settings Module: event_management.settings_render
```

### 2.3 Configuration des Variables d'Environnement

Dans l'onglet "Environment" de Render, ajoutez :

```bash
# Configuration de base
DEBUG=False
ALLOWED_HOSTS=event-management-backend.onrender.com,localhost,127.0.0.1
SECRET_KEY=your-secret-key-here

# Configuration MySQL (en ligne)
DATABASE_URL=mysql://user:password@host:port/database

# Configuration Cron (pour les mails automatiques)
CRON_SECRET_KEY=your-secret-key-here

# Configuration Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@eventmanagement.com

# Configuration Stripe
STRIPE_PUBLIC_KEY=pk_live_your_stripe_public_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key

# Configuration Twilio
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=your_twilio_phone_number

# Configuration OAuth2
GOOGLE_OAUTH2_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH2_CLIENT_SECRET=your_google_client_secret
FACEBOOK_OAUTH2_CLIENT_ID=your_facebook_app_id
FACEBOOK_OAUTH2_CLIENT_SECRET=your_facebook_app_secret

# Configuration Streaming
YOUTUBE_API_KEY=your_youtube_api_key
ZOOM_ACCOUNT_ID=your_zoom_account_id
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
```

### 2.4 Configuration de la Base de Données MySQL

**✅ Vous utilisez MySQL en local** - Pour le déploiement en ligne, vous avez plusieurs options :

#### Option 1 : MySQL sur Render (RECOMMANDÉ)
1. **Cliquez sur "New +"** → **"MySQL"**
2. **Nom** : `event-management-mysql`
3. **Plan** : Free
4. **Attendez** que la base soit créée (2-3 minutes)
5. **Copiez l'URL de connexion** et mettez-la dans `DATABASE_URL`

#### Option 2 : MySQL sur PlanetScale (GRATUIT)
1. **Allez sur** https://planetscale.com
2. **Créez un compte gratuit**
3. **Créez une base de données** : `event_management`
4. **Récupérez l'URL de connexion**

#### Option 3 : MySQL sur Railway (GRATUIT)
1. **Allez sur** https://railway.app
2. **Créez un compte gratuit**
3. **Déployez MySQL**
4. **Récupérez l'URL de connexion**

**📚 Guide détaillé** : Voir `GUIDE_MYSQL_HEBERGE.md`

### 2.5 Configuration des Services Externes

**✅ Plus besoin de Redis** : Le système utilise des services cron externes gratuits au lieu de Celery.

### 2.6 Configuration du Système de Mails Automatiques

**⚠️ IMPORTANT** : Les services Celery Worker et Celery Beat ne sont pas gratuits sur Render. 

**✅ SOLUTION GRATUITE** : Utilisez des services cron externes gratuits !

#### Services Cron Externes Gratuits
- **Cron-job.org** (recommandé) - 100% gratuit
- **Uptime Robot** - 100% gratuit  
- **GitHub Actions** - 100% gratuit
- **Heroku Scheduler** - 100% gratuit

#### Configuration
1. **Utilisez** `settings_render.py` au lieu de `settings_production.py`
2. **Ajoutez** `CRON_SECRET_KEY` dans les variables d'environnement
3. **Configurez** un service cron externe pour appeler `/cron/notifications/`

**📚 Guide détaillé** : Voir `GUIDE_MAILS_AUTOMATIQUES_GRATUITS.md`

### 2.7 Configuration des Services Cron Externes

#### Option 1 : Cron-job.org (RECOMMANDÉ)
1. **Allez sur** https://cron-job.org
2. **Créez un compte gratuit**
3. **Configurez le cron job** :
   - **URL** : `https://event-management-backend.onrender.com/cron/notifications/`
   - **Méthode** : POST
   - **Headers** : `Authorization: Bearer YOUR_SECRET_KEY`
   - **Fréquence** : Toutes les 15 minutes

#### Option 2 : Uptime Robot
1. **Allez sur** https://uptimerobot.com
2. **Créez un compte gratuit**
3. **Configurez le monitor** avec la même URL

### 2.8 Déploiement

1. **Cliquez sur "Deploy"**
2. **Attendez la fin du déploiement**
3. **Notez l'URL** : `https://event-management-backend.onrender.com`

## 🚀 Étape 3 : Déploiement Frontend sur Vercel

### 3.1 Création du Projet Vercel

1. **Connectez-vous à Vercel** : https://vercel.com
2. **Cliquez sur "New Project"**
3. **Importez votre repository GitHub**
4. **Sélectionnez le dossier `frontend`**

### 3.2 Configuration du Projet

```yaml
Framework Preset: Create React App
Root Directory: frontend
Build Command: npm run build
Output Directory: build
Install Command: npm install
```

### 3.3 Configuration des Variables d'Environnement

Dans l'onglet "Environment Variables" de Vercel, ajoutez :

```bash
REACT_APP_API_URL=https://event-management-backend.onrender.com/api
REACT_APP_BASE_URL=https://event-management-backend.onrender.com
REACT_APP_STRIPE_PK=pk_live_your_stripe_public_key
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
REACT_APP_FACEBOOK_APP_ID=your_facebook_app_id
```

### 3.4 Déploiement

1. **Cliquez sur "Deploy"**
2. **Attendez la fin du déploiement**
3. **Notez l'URL** : `https://event-management-frontend.vercel.app`

## 🚀 Étape 4 : Configuration des Domaines

### 4.1 Mise à jour des URLs

1. **Dans Render** : Mettez à jour `ALLOWED_HOSTS` avec votre domaine Vercel
2. **Dans Vercel** : Mettez à jour `REACT_APP_API_URL` avec votre domaine Render
3. **Redéployez** les deux services

### 4.2 Configuration CORS

Le fichier `settings_production.py` est déjà configuré pour accepter les requêtes depuis Vercel.

## 🚀 Étape 5 : Test du Système

### 5.1 Test de l'API

```bash
# Test de l'API
curl https://event-management-backend.onrender.com/api/events/

# Test de l'authentification
curl -X POST https://event-management-backend.onrender.com/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 5.2 Test du Frontend

1. **Ouvrez** `https://event-management-frontend.vercel.app`
2. **Testez** l'inscription/connexion
3. **Testez** la création d'événements
4. **Testez** les paiements Stripe

### 5.3 Test des Mails Automatiques

1. **Créez un événement** avec une date future
2. **Inscrivez-vous** à cet événement
3. **Vérifiez** que vous recevez les emails de confirmation
4. **Attendez** les rappels automatiques

## 🔧 Gestion des Services

### Services Render

1. **Web Service** : API Django principal
2. **MySQL** : Base de données hébergée (Render/PlanetScale/Railway)
3. **Services Cron Externes** : Gèrent les mails automatiques (gratuits)

### Monitoring

1. **Render Dashboard** : Surveillez les logs et les performances
2. **Vercel Dashboard** : Surveillez les déploiements
3. **Logs** : Consultez les logs en temps réel

## 🚨 Dépannage

### Problèmes Courants

#### 1. Erreur CORS
```bash
# Vérifiez que CORS_ALLOWED_ORIGINS contient votre domaine Vercel
CORS_ALLOWED_ORIGINS = [
    "https://event-management-frontend.vercel.app",
]
```

#### 2. Erreur de Base de Données
```bash
# Vérifiez que DATABASE_URL est correct
# Redéployez le service web
```

#### 3. Mails non envoyés
```bash
# Vérifiez que le service cron externe fonctionne
# Vérifiez les logs Render
# Vérifiez la configuration SMTP
# Testez l'endpoint /cron/notifications/
```

#### 4. Images non affichées
```bash
# Vérifiez que MEDIA_URL est correct
# Vérifiez que les fichiers sont uploadés
```

### Logs et Debugging

1. **Render Logs** : Onglet "Logs" de chaque service
2. **Vercel Logs** : Onglet "Functions" → "View Function Logs"
3. **Django Debug** : Activez `DEBUG=True` temporairement

## 📊 Monitoring et Maintenance

### Surveillance Continue

1. **Uptime** : Surveillez la disponibilité des services
2. **Performance** : Surveillez les temps de réponse
3. **Erreurs** : Surveillez les erreurs 500
4. **Logs** : Consultez régulièrement les logs

### Maintenance

1. **Mises à jour** : Mettez à jour les dépendances régulièrement
2. **Sauvegardes** : Sauvegardez la base de données
3. **Monitoring** : Surveillez l'utilisation des ressources
4. **Logs** : Nettoyez les anciens logs

## 🎉 Félicitations !

Votre système de gestion d'événements est maintenant déployé en production !

### URLs de Production
- **Frontend** : `https://event-management-frontend.vercel.app`
- **Backend API** : `https://event-management-backend.onrender.com/api`
- **Admin Django** : `https://event-management-backend.onrender.com/admin`

### Prochaines Étapes
1. **Testez** toutes les fonctionnalités
2. **Configurez** un domaine personnalisé
3. **Mettez en place** un monitoring avancé
4. **Planifiez** les sauvegardes

---

**Support** : En cas de problème, consultez les logs et la documentation des services utilisés.
