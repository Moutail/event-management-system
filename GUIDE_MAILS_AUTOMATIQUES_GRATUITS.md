# 📧 Guide des Mails Automatiques Gratuits

## 🎯 Problème Résolu

Les services Celery Worker et Celery Beat ne sont pas gratuits sur Render. Voici des solutions **100% gratuites** pour gérer vos mails automatiques.

## 🚀 Solution 1 : Cron-job.org (RECOMMANDÉ)

### 1.1 Configuration

1. **Allez sur** https://cron-job.org
2. **Créez un compte gratuit**
3. **Cliquez sur "Create cronjob"**

### 1.2 Configuration du Cron Job

```yaml
Title: Event Management Notifications
URL: https://event-management-backend.onrender.com/cron/notifications/
Method: POST
Headers: 
  Authorization: Bearer YOUR_SECRET_KEY
  Content-Type: application/json
Schedule: */15 * * * *  # Toutes les 15 minutes
```

### 1.3 Variables d'Environnement

Ajoutez dans Render :
```bash
CRON_SECRET_KEY=your-secret-key-here
```

## 🚀 Solution 2 : Uptime Robot (GRATUIT)

### 2.1 Configuration

1. **Allez sur** https://uptimerobot.com
2. **Créez un compte gratuit**
3. **Cliquez sur "Add New Monitor"**

### 2.2 Configuration du Monitor

```yaml
Monitor Type: HTTP(s)
Friendly Name: Event Notifications
URL: https://event-management-backend.onrender.com/cron/notifications/
Monitoring Interval: 15 minutes
HTTP Method: POST
HTTP Headers: 
  Authorization: Bearer YOUR_SECRET_KEY
  Content-Type: application/json
```

## 🚀 Solution 3 : GitHub Actions (GRATUIT)

### 3.1 Création du Workflow

Créez le fichier `.github/workflows/notifications.yml` :

```yaml
name: Send Event Notifications

on:
  schedule:
    - cron: '*/15 * * * *'  # Toutes les 15 minutes
  workflow_dispatch:  # Permet l'exécution manuelle

jobs:
  send-notifications:
    runs-on: ubuntu-latest
    
    steps:
    - name: Trigger Notifications
      run: |
        curl -X POST \
          -H "Authorization: Bearer ${{ secrets.CRON_SECRET_KEY }}" \
          -H "Content-Type: application/json" \
          https://event-management-backend.onrender.com/cron/notifications/
```

### 3.2 Configuration des Secrets

1. **Allez dans** Settings → Secrets and variables → Actions
2. **Ajoutez** `CRON_SECRET_KEY` avec votre clé secrète

## 🚀 Solution 4 : Heroku Scheduler (GRATUIT)

### 4.1 Configuration

1. **Créez un compte Heroku gratuit**
2. **Installez l'addon Scheduler**
3. **Configurez la tâche**

### 4.2 Commande Scheduler

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  https://event-management-backend.onrender.com/cron/notifications/
```

## 🔧 Configuration du Backend

### 1. Mise à jour des Settings

Utilisez `settings_render.py` au lieu de `settings_production.py` :

```python
# Dans render.yaml
DJANGO_SETTINGS_MODULE=event_management.settings_render
```

### 2. Variables d'Environnement Requises

```bash
# Configuration de base
DEBUG=False
ALLOWED_HOSTS=event-management-backend.onrender.com,localhost,127.0.0.1
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/database

# Configuration Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@eventmanagement.com

# Configuration Cron
CRON_SECRET_KEY=your-secret-key-here

# Configuration Stripe
STRIPE_PUBLIC_KEY=pk_live_your_stripe_public_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key

# Configuration Twilio
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=your_twilio_phone_number
```

## 📋 Types de Notifications Automatiques

### 1. Rappels d'Événements
- **J-1** : 24h avant l'événement
- **1h avant** : 1h avant l'événement
- **Jour J** : Le jour de l'événement

### 2. Remerciements
- **12h après** : Après la fin de l'événement

### 3. Remboursements
- **Automatique** : Pour les événements annulés

## 🧪 Test des Notifications

### 1. Test Manuel

```bash
# Test de l'endpoint
curl -X POST \
  -H "Authorization: Bearer YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  https://event-management-backend.onrender.com/cron/notifications/

# Test de santé
curl https://event-management-backend.onrender.com/health/
```

### 2. Test en Local

```bash
# Dans le dossier backend
python manage.py send_notifications_cron
```

## 📊 Monitoring

### 1. Logs Render

Consultez les logs du service web pour voir les notifications envoyées.

### 2. Logs des Services Externes

- **Cron-job.org** : Dashboard avec historique
- **Uptime Robot** : Logs des requêtes
- **GitHub Actions** : Logs des workflows

### 3. Base de Données

Vérifiez la table `NotificationLog` pour l'historique des envois.

## 🚨 Dépannage

### Problèmes Courants

#### 1. Notifications non envoyées
```bash
# Vérifiez que le service cron externe fonctionne
# Vérifiez les logs Render
# Vérifiez la configuration SMTP
```

#### 2. Erreur 401 Unauthorized
```bash
# Vérifiez que CRON_SECRET_KEY est correct
# Vérifiez que l'Authorization header est bien envoyé
```

#### 3. Erreur 500 Internal Server Error
```bash
# Vérifiez les logs Render
# Vérifiez la configuration de la base de données
# Vérifiez que les templates d'email existent
```

## 🎉 Avantages de cette Solution

- ✅ **100% Gratuit** : Aucun coût supplémentaire
- ✅ **Fiable** : Services externes robustes
- ✅ **Flexible** : Facile à modifier la fréquence
- ✅ **Monitoring** : Logs et historique disponibles
- ✅ **Scalable** : Peut gérer de nombreux événements

## 📝 Résumé des Étapes

1. **Déployez le backend** sur Render avec `settings_render.py`
2. **Configurez les variables d'environnement**
3. **Choisissez un service cron externe** (recommandé : cron-job.org)
4. **Configurez le cron job** avec l'URL de votre backend
5. **Testez le système** avec des événements de test
6. **Surveillez les logs** pour vérifier le bon fonctionnement

Votre système de mails automatiques fonctionnera maintenant 24/7 sans coût supplémentaire ! 🎯
