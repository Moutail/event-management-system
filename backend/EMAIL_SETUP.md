# 📧 Configuration des Emails Automatiques

## ✅ État actuel
Tous les emails automatiques sont **fonctionnels** et testés avec succès !

## 🎯 Emails automatiques disponibles

### 1. **Inscriptions**
- ✅ **Confirmation d'inscription** : Envoyé quand un utilisateur s'inscrit avec succès
- ✅ **Inscription en liste d'attente** : Envoyé quand l'événement est plein
- ✅ **Annulation d'inscription** : Envoyé quand un utilisateur annule son inscription

### 2. **Événements**
- ✅ **Annulation d'événement** : Envoyé à tous les participants quand l'organisateur annule
- ✅ **Rejet d'événement** : Envoyé à l'organisateur quand un admin rejette l'événement

### 3. **Remboursements**
- ✅ **Remboursement approuvé** : Envoyé quand un remboursement est approuvé
- ✅ **Remboursement rejeté** : Envoyé quand un remboursement est rejeté
- ✅ **Remboursement traité** : Envoyé quand un remboursement est effectué

### 4. **Notifications automatiques**
- ✅ **Rappels événements** : J-1, 1h avant, jour J
- ✅ **Remerciements** : Après la fin de l'événement

## 🔧 Configuration pour la production

### Option 1: Gmail SMTP (Recommandé)
```python
# Dans backend/event_management/settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre-email@gmail.com'
EMAIL_HOST_PASSWORD = 'votre-mot-de-passe-d-application'
DEFAULT_FROM_EMAIL = 'noreply@votredomaine.com'
```

**⚠️ Important pour Gmail :**
1. Activez l'authentification à 2 facteurs sur votre compte Gmail
2. Créez un "mot de passe d'application" : https://myaccount.google.com/apppasswords
3. Utilisez ce mot de passe d'application (pas votre mot de passe principal)

### Option 2: Autres fournisseurs SMTP
```python
# SendGrid
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'votre-api-key-sendgrid'

# Mailgun
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'postmaster@votredomaine.mailgun.org'
EMAIL_HOST_PASSWORD = 'votre-api-key-mailgun'

# Amazon SES
EMAIL_HOST = 'email-smtp.eu-west-1.amazonaws.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'votre-access-key'
EMAIL_HOST_PASSWORD = 'votre-secret-key'
```

### Option 3: Service d'email transactionnel
```python
# Resend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.resend.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'resend'
EMAIL_HOST_PASSWORD = 're_votre-api-key'
```

## 🧪 Test des emails

### Test en développement (console)
```python
# Les emails s'affichent dans la console Django
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Test en production
1. Créez un événement de test
2. Inscrivez un utilisateur de test
3. Testez les différentes actions (annulation, remboursement, etc.)
4. Vérifiez que les emails sont reçus

## 📋 Templates disponibles

Tous les templates sont dans `backend/templates/emails/` :

- `registration_confirmation.html/txt` - Confirmation d'inscription
- `registration_waitlisted.html/txt` - Liste d'attente
- `registration_cancelled.html/txt` - Annulation d'inscription
- `event_cancelled_participant.html/txt` - Annulation d'événement
- `refund_approved.html/txt` - Remboursement approuvé
- `refund_rejected.html/txt` - Remboursement rejeté
- `refund_processed.html/txt` - Remboursement traité

## 🚀 Déploiement

1. **Configurez vos identifiants SMTP** dans `settings.py`
2. **Testez avec un événement de test**
3. **Vérifiez les logs** pour détecter d'éventuelles erreurs
4. **Surveillez la délivrabilité** des emails

## 🔍 Dépannage

### Erreurs courantes
- **"Authentication failed"** : Vérifiez vos identifiants SMTP
- **"Connection refused"** : Vérifiez le port et l'hôte SMTP
- **"TLS required"** : Activez `EMAIL_USE_TLS = True`

### Logs de débogage
```python
# Ajoutez dans settings.py pour plus de détails
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez la configuration SMTP
2. Testez avec un événement simple
3. Consultez les logs Django
4. Vérifiez la délivrabilité avec votre fournisseur SMTP

---

**🎉 Félicitations ! Votre système d'emails automatiques est maintenant 100% fonctionnel !**
