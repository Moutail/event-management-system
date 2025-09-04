# 📧 GUIDE DES RAPPELS PERSONNALISÉS

## 🎯 Vue d'ensemble

Le système de rappels personnalisés permet aux **organisateurs** et **super admins** d'envoyer des messages personnalisés à leurs participants d'événements via **email** et **SMS**.

## 🔧 Fonctionnalités

### ✅ Types de rappels
- **Rappel général** : Message d'information générale
- **Rappel d'événement** : Rappel de l'événement à venir
- **Mise à jour** : Informations mises à jour sur l'événement
- **Annulation** : Notification d'annulation
- **Report** : Notification de report
- **Message personnalisé** : Message libre

### ✅ Audience cible
- **Tous les participants** : Tous les inscrits (confirmés, liste d'attente, présents)
- **Participants confirmés uniquement** : Seulement les inscriptions confirmées
- **Liste d'attente uniquement** : Seulement les inscriptions en attente
- **Participants présents uniquement** : Seulement les inscriptions marquées comme présentes
- **Sélection personnalisée** : Choix manuel des destinataires

### ✅ Canaux d'envoi
- **Email** : Envoi par courriel avec template HTML
- **SMS** : Envoi par SMS via Twilio
- **Les deux** : Email + SMS simultanément

## 🚀 Utilisation

### 1. Créer un rappel

**Endpoint :** `POST /api/custom-reminders/`

**Headers :**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Payload :**
```json
{
    "event": 123,
    "title": "Rappel Important",
    "message": "N'oubliez pas notre événement demain !",
    "reminder_type": "reminder",
    "target_audience": "confirmed",
    "send_email": true,
    "send_sms": true,
    "custom_recipient_ids": [456, 789]  // Optionnel pour ciblage personnalisé
}
```

### 2. Envoyer immédiatement

**Endpoint :** `POST /api/custom-reminders/{id}/send_now/`

**Headers :**
```
Authorization: Bearer <token>
```

**Réponse :**
```json
{
    "message": "Rappel envoyé avec succès",
    "statistics": {
        "total_recipients": 15,
        "emails_sent": 15,
        "sms_sent": 12,
        "emails_failed": 0,
        "sms_failed": 3
    }
}
```

### 3. Programmer l'envoi

**Endpoint :** `POST /api/custom-reminders/{id}/schedule/`

**Headers :**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Payload :**
```json
{
    "scheduled_at": "2024-01-15T10:00:00Z"
}
```

### 4. Lister les rappels

**Endpoint :** `GET /api/custom-reminders/`

**Headers :**
```
Authorization: Bearer <token>
```

**Filtres disponibles :**
- `event` : ID de l'événement
- `reminder_type` : Type de rappel
- `status` : Statut (draft, scheduled, sent, failed)
- `target_audience` : Audience cible

### 5. Rappels par événement

**Endpoint :** `GET /api/custom-reminders/event_reminders/?event_id=123`

**Headers :**
```
Authorization: Bearer <token>
```

## 🔐 Permissions

### Organisateurs
- Peuvent créer des rappels pour **leurs propres événements**
- Peuvent voir tous leurs rappels
- Peuvent envoyer et programmer leurs rappels

### Super Admins
- Peuvent créer des rappels pour **tous les événements**
- Peuvent voir tous les rappels
- Peuvent envoyer et programmer tous les rappels

## 📊 Statistiques

Chaque rappel enregistre :
- **Total destinataires** : Nombre total de personnes ciblées
- **Emails envoyés** : Nombre d'emails envoyés avec succès
- **SMS envoyés** : Nombre de SMS envoyés avec succès
- **Emails échoués** : Nombre d'emails qui ont échoué
- **SMS échoués** : Nombre de SMS qui ont échoué

## 🎨 Templates

### Email
- Template HTML responsive
- Template texte simple
- Informations de l'événement incluses
- Personnalisation par nom du destinataire

### SMS
- Message concis (160 caractères recommandés)
- Titre du rappel
- Message personnalisé
- Informations essentielles de l'événement

## 🔍 Debug et Logs

Le système enregistre des logs détaillés :
```
🔍 DEBUG: ===== DÉBUT ENVOI RAPPEL PERSONNALISÉ =====
🔍 DEBUG: Rappel ID: 123
🔍 DEBUG: Titre: Rappel Important
🔍 DEBUG: Type: reminder
🔍 DEBUG: Audience: confirmed
🔍 DEBUG: Email: True
🔍 DEBUG: SMS: True
🔍 DEBUG: Destinataires: 15
🔍 DEBUG: Email envoyé à participant@example.com
🔍 DEBUG: SMS envoyé à +15141234567
🔍 DEBUG: ===== FIN ENVOI RAPPEL PERSONNALISÉ =====
```

## 🧪 Test

Utilisez le script de test :
```bash
cd backend
python test_custom_reminders.py
```

## ⚠️ Notes importantes

1. **SMS** : Nécessite une configuration Twilio valide
2. **Email** : Nécessite une configuration SMTP valide
3. **Permissions** : Seuls les organisateurs et super admins peuvent créer des rappels
4. **Limites** : Respectez les limites de taux de votre fournisseur SMS
5. **Templates** : Les templates email sont dans `backend/templates/emails/`

## 🎯 Cas d'usage

### Rappel 24h avant
```json
{
    "title": "Rappel - Événement demain",
    "message": "N'oubliez pas notre événement demain à 14h !",
    "reminder_type": "reminder",
    "target_audience": "confirmed"
}
```

### Mise à jour importante
```json
{
    "title": "Mise à jour importante",
    "message": "L'événement a été déplacé au bâtiment B.",
    "reminder_type": "update",
    "target_audience": "all"
}
```

### Annulation
```json
{
    "title": "Événement annulé",
    "message": "Malheureusement, nous devons annuler l'événement.",
    "reminder_type": "cancellation",
    "target_audience": "all"
}
```

## 🚀 Prochaines étapes

1. **Interface utilisateur** : Créer une interface pour les organisateurs
2. **Templates avancés** : Plus de templates personnalisables
3. **Programmation avancée** : Rappels récurrents
4. **Analytics** : Statistiques détaillées d'ouverture
5. **A/B Testing** : Tester différents messages


