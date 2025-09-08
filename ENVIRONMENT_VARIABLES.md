# 🔧 Variables d'Environnement pour le Déploiement

## 📋 Variables Backend (Render)

### Configuration de Base
```bash
DEBUG=False
ALLOWED_HOSTS=event-management-backend.onrender.com,localhost,127.0.0.1
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/database
```

### Configuration Celery
```bash
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Configuration Email
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@eventmanagement.com
```

### Configuration Stripe
```bash
STRIPE_PUBLIC_KEY=pk_live_your_stripe_public_key
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
```

### Configuration Twilio (SMS)
```bash
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_FROM_NUMBER=your_twilio_phone_number
```

### Configuration OAuth2
```bash
GOOGLE_OAUTH2_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH2_CLIENT_SECRET=your_google_client_secret
FACEBOOK_OAUTH2_CLIENT_ID=your_facebook_app_id
FACEBOOK_OAUTH2_CLIENT_SECRET=your_facebook_app_secret
```

### Configuration Streaming
```bash
YOUTUBE_API_KEY=your_youtube_api_key
ZOOM_ACCOUNT_ID=your_zoom_account_id
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
```

## 🎨 Variables Frontend (Vercel)

### Configuration API
```bash
REACT_APP_API_URL=https://event-management-backend.onrender.com/api
REACT_APP_BASE_URL=https://event-management-backend.onrender.com
```

### Configuration Stripe
```bash
REACT_APP_STRIPE_PK=pk_live_your_stripe_public_key
```

### Configuration OAuth2
```bash
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
REACT_APP_FACEBOOK_APP_ID=your_facebook_app_id
```

## 🔐 Configuration des Services Externes

### 1. Gmail SMTP
1. Activez l'authentification à 2 facteurs sur votre compte Gmail
2. Créez un "mot de passe d'application" : https://myaccount.google.com/apppasswords
3. Utilisez ce mot de passe d'application (pas votre mot de passe principal)

### 2. Stripe
1. Créez un compte sur https://stripe.com
2. Récupérez vos clés API dans le dashboard Stripe
3. Utilisez les clés de production (pk_live_ et sk_live_)

### 3. Twilio
1. Créez un compte sur https://twilio.com
2. Récupérez votre Account SID et Auth Token
3. Achetez un numéro de téléphone

### 4. Google OAuth2
1. Allez sur https://console.developers.google.com
2. Créez un projet et activez l'API Google+
3. Créez des identifiants OAuth2
4. Ajoutez les domaines autorisés

### 5. Facebook OAuth2
1. Allez sur https://developers.facebook.com
2. Créez une application
3. Ajoutez le produit "Facebook Login"
4. Configurez les domaines autorisés

## 🚀 Déploiement

### Render (Backend)
1. Connectez votre repository GitHub
2. Sélectionnez le dossier `backend`
3. Configurez les variables d'environnement
4. Déployez

### Vercel (Frontend)
1. Connectez votre repository GitHub
2. Sélectionnez le dossier `frontend`
3. Configurez les variables d'environnement
4. Déployez

## 📧 Gestion des Mails Automatiques

Le système de mails automatiques fonctionne avec 3 services :

1. **Web Service** : API Django principal
2. **Celery Worker** : Traite les tâches d'envoi de mails
3. **Celery Beat** : Planifie les tâches périodiques

Ces services sont configurés pour fonctionner automatiquement sur Render.
