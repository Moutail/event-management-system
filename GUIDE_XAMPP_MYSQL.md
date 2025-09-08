# 🗄️ Guide Configuration XAMPP + MySQL

## 🎯 Configuration avec XAMPP

Vous utilisez XAMPP avec MySQL - c'est parfait ! Voici comment configurer votre projet.

## 🚀 Étape 1 : Configuration XAMPP

### 1.1 Démarrage de XAMPP

1. **Lancez XAMPP Control Panel**
2. **Démarrez Apache** (pour phpMyAdmin)
3. **Démarrez MySQL** (pour la base de données)

### 1.2 Création de la Base de Données

1. **Ouvrez phpMyAdmin** : http://localhost/phpmyadmin
2. **Cliquez sur "Nouvelle base de données"**
3. **Nom** : `event_management`
4. **Interclassement** : `utf8mb4_unicode_ci`
5. **Cliquez sur "Créer"**

### 1.3 Configuration des Variables d'Environnement

Créez un fichier `.env` dans le dossier `backend` :

```env
# Configuration MySQL (XAMPP)
DB_NAME=event_management
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

# Configuration de base
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuration Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@eventmanagement.com

# Configuration Stripe
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key

# Configuration Twilio
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=your_twilio_phone_number

# Configuration OAuth2
GOOGLE_OAUTH2_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH2_CLIENT_SECRET=your_google_client_secret
FACEBOOK_OAUTH2_CLIENT_ID=your_facebook_app_id
FACEBOOK_OAUTH2_CLIENT_SECRET=your_facebook_app_secret

# Configuration Cron
CRON_SECRET_KEY=your-secret-key-here
```

## 🚀 Étape 2 : Configuration Django

### 2.1 Mise à jour des Settings

Le fichier `settings_render.py` est déjà configuré pour MySQL. Pour le développement local, créez `settings_local.py` :

```python
# backend/event_management/settings_local.py
from .settings import *
import os

# Configuration MySQL pour XAMPP
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'event_management'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}

# Configuration de développement
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Configuration des médias
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuration CORS pour le développement
CORS_ALLOW_ALL_ORIGINS = True
```

### 2.2 Installation des Dépendances

```bash
# Dans le dossier backend
pip install -r requirements.txt
```

### 2.3 Migration de la Base de Données

```bash
# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser
```

## 🚀 Étape 3 : Test Local

### 3.1 Démarrage du Serveur

```bash
# Démarrer le serveur Django
python manage.py runserver

# Dans un autre terminal, démarrer le frontend
cd frontend
npm start
```

### 3.2 Test de la Base de Données

1. **Ouvrez** http://localhost:8000/admin
2. **Connectez-vous** avec votre superutilisateur
3. **Vérifiez** que les tables sont créées dans phpMyAdmin

## 🚀 Étape 4 : Déploiement sur Render

### 4.1 Configuration Render

Pour le déploiement sur Render, utilisez `settings_render.py` qui est déjà configuré pour MySQL.

### 4.2 Variables d'Environnement Render

```bash
# Configuration de base
DEBUG=False
ALLOWED_HOSTS=event-management-backend.onrender.com,localhost,127.0.0.1
SECRET_KEY=your-secret-key-here

# Configuration MySQL (XAMPP)
DB_NAME=event_management
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

# Configuration Cron
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
```

## 🚀 Étape 5 : Configuration des Mails Automatiques

### 5.1 Service Cron Externe

Utilisez un service cron externe gratuit pour déclencher les mails :

1. **Cron-job.org** (recommandé)
2. **Uptime Robot**
3. **GitHub Actions**

### 5.2 Configuration du Cron Job

```yaml
URL: https://event-management-backend.onrender.com/cron/notifications/
Méthode: POST
Headers: 
  Authorization: Bearer YOUR_SECRET_KEY
  Content-Type: application/json
Fréquence: Toutes les 15 minutes
```

## 🔧 Dépannage

### Problèmes Courants

#### 1. Erreur de Connexion MySQL
```bash
# Vérifiez que XAMPP est démarré
# Vérifiez que MySQL est actif
# Vérifiez les paramètres de connexion
```

#### 2. Erreur de Migration
```bash
# Vérifiez que la base de données existe
# Vérifiez les permissions MySQL
# Exécutez les migrations une par une
```

#### 3. Erreur de Charset
```bash
# Vérifiez que la base utilise utf8mb4
# Vérifiez la configuration MySQL
```

## 📊 Avantages de XAMPP + MySQL

- ✅ **Gratuit** : Aucun coût
- ✅ **Local** : Développement en local
- ✅ **Familiers** : Interface phpMyAdmin
- ✅ **Léger** : Moins de ressources que PostgreSQL
- ✅ **Compatible** : Parfait avec Django

## 🎉 Résumé

1. **Démarrez XAMPP** et créez la base `event_management`
2. **Configurez** les variables d'environnement
3. **Testez** en local avec `python manage.py runserver`
4. **Déployez** sur Render avec `settings_render.py`
5. **Configurez** un service cron externe pour les mails

Votre système fonctionnera parfaitement avec XAMPP + MySQL ! 🎯
