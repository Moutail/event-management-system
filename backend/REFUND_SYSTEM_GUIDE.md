# 💰 Guide Complet du Système de Remboursements

## 🎯 Vue d'ensemble

Le système de remboursements automatisés permet de gérer les annulations avec flexibilité :
- **Remboursements manuels** : Validation par l'organisateur
- **Remboursements automatiques** : Traitement automatique après délai
- **Remboursements mixtes** : Manuel puis automatique si pas de réponse
- **Remboursements désactivés** : Aucun remboursement autorisé

## 🏗️ Architecture

### Modèles créés :

1. **`RefundPolicy`** : Politique de remboursement par événement
2. **`RefundRequest`** : Demandes de remboursement individuelles

### Nouvelles APIs :

1. **`POST /api/registrations/{id}/request_refund/`** : Demander un remboursement
2. **`POST /api/registrations/{id}/process_refund/`** : Traiter manuellement (organisateur)

## 📋 Configuration des Politiques

### Types de remboursement :

```python
REFUND_MODE_CHOICES = [
    ('disabled', 'Remboursements désactivés'),
    ('manual', 'Remboursement manuel uniquement'),      # Par défaut
    ('auto', 'Remboursement automatique'),              # Immédiat
    ('mixed', 'Manuel puis automatique après délai'),   # Recommandé
]
```

### Paramètres configurables :

- **`auto_refund_delay_hours`** : Délai avant traitement auto (défaut: 24h)
- **`refund_percentage_immediate`** : % remboursé immédiatement (défaut: 100%)
- **`refund_percentage_after_delay`** : % après délai (défaut: 80%)
- **`cutoff_hours_before_event`** : Limite avant événement (défaut: 24h)
- **`allow_partial_refunds`** : Remboursements partiels autorisés
- **`require_reason`** : Raison obligatoire pour annuler
- **`notify_organizer_on_cancellation`** : Notifier l'organisateur

## 🔄 Flux de remboursement

### 1. Demande de remboursement

```bash
POST /api/registrations/123/request_refund/
{
  "reason": "Empêchement de dernière minute"
}
```

**Réponse :**
```json
{
  "message": "Demande de remboursement créée avec succès",
  "refund_request_id": 456,
  "refund_amount": 25.00,
  "refund_percentage": 100,
  "status": "pending",
  "auto_process_at": "2025-08-16T10:00:00Z",
  "expires_at": "2025-08-17T08:00:00Z"
}
```

### 2. Traitement selon le mode

#### Mode `auto` : 
- ✅ Remboursement immédiat via Stripe
- 📧 Email de confirmation envoyé

#### Mode `manual` :
- ⏳ En attente de validation organisateur
- 📧 Notification organisateur (si configuré)

#### Mode `mixed` :
- ⏳ En attente 24h (configurable)
- ✅ Traitement automatique après délai
- 📧 Emails à chaque étape

### 3. Actions organisateur

```bash
# Approuver
POST /api/registrations/123/process_refund/
{"action": "approve"}

# Rejeter  
POST /api/registrations/123/process_refund/
{"action": "reject"}
```

## ⚙️ Traitement automatique

### Commande dédiée :

```bash
python manage.py process_auto_refunds
```

### Intégration avec notifications :

Le traitement automatique est intégré dans `send_event_notifications` et s'exécute toutes les 15 minutes avec le script de notifications.

## 📊 Statuts des demandes

- **`pending`** : En attente de traitement
- **`approved`** : Approuvé (en cours)
- **`processed`** : Traité avec succès
- **`rejected`** : Refusé par l'organisateur
- **`expired`** : Expiré (trop tard)

## 💳 Intégration Stripe

### Remboursements partiels :
```python
stripe.Refund.create(
    payment_intent=payment_reference,
    amount=int(refund_amount * 100),  # Centimes
    reason='requested_by_customer'
)
```

### Gestion des erreurs :
- Retry automatique en cas d'erreur temporaire
- Logs détaillés pour debug
- Notifications admin en cas d'échec

## 📧 Emails automatiques

### Templates créés :

1. **`refund_confirmation.txt/.html`** : Confirmation remboursement
2. **`organizer_cancellation_notice.txt/.html`** : Notification organisateur

### Variables disponibles :

```python
context = {
    'user': registration.user,
    'event': event,
    'refund_request': refund_request,
    'refund_amount': refund_request.refund_amount,
    'organizer': event.organizer,
    'reason': reason
}
```

## 🎛️ Exemples de configuration

### Événement gratuit (pas de remboursement) :
```python
RefundPolicy.objects.create(
    event=event,
    mode='disabled'
)
```

### Événement payant - remboursement flexible :
```python
RefundPolicy.objects.create(
    event=event,
    mode='mixed',
    auto_refund_delay_hours=48,
    refund_percentage_immediate=100,
    refund_percentage_after_delay=90,
    cutoff_hours_before_event=12,
    require_reason=True,
    notify_organizer_on_cancellation=True
)
```

### Événement premium - validation manuelle :
```python
RefundPolicy.objects.create(
    event=event,
    mode='manual',
    refund_percentage_immediate=80,
    cutoff_hours_before_event=72,
    require_reason=True
)
```

## 🔍 Monitoring et Analytics

### Logs à surveiller :

- Nombre de demandes par jour
- Taux d'approbation/rejet
- Montants remboursés
- Délais de traitement

### Métriques utiles :

```python
# Demandes en attente
pending_refunds = RefundRequest.objects.filter(status='pending').count()

# Montant total remboursé ce mois
from django.db.models import Sum
total_refunded = RefundRequest.objects.filter(
    status='processed',
    processed_at__month=current_month
).aggregate(Sum('refund_amount'))
```

## 🚨 Gestion des erreurs

### Erreurs Stripe courantes :

- **Insufficient funds** : Pas assez de fonds sur le compte
- **Payment not found** : Référence de paiement invalide
- **Already refunded** : Déjà remboursé

### Actions correctives :

1. **Retry automatique** pour erreurs temporaires
2. **Notification admin** pour erreurs critiques
3. **Status 'failed'** avec possibilité de re-traitement manuel

## 🔒 Sécurité

### Permissions :

- **Utilisateur** : Peut demander remboursement de ses propres inscriptions
- **Organisateur** : Peut traiter les remboursements de ses événements
- **Staff** : Accès complet

### Validations :

- Vérification des montants
- Contrôle des délais
- Protection contre double remboursement
- Audit trail complet

---

## 🎉 Le système est maintenant COMPLET !

**Fonctionnalités implémentées :**
- ✅ Politiques configurables par événement
- ✅ Remboursements automatiques et manuels
- ✅ Intégration Stripe complète
- ✅ Emails automatiques
- ✅ Traitement en arrière-plan
- ✅ Gestion des erreurs
- ✅ Audit et monitoring

**Prochaines étapes suggérées :**
1. Interface web pour configurer les politiques
2. Dashboard analytics pour les organisateurs
3. Notifications push mobile
4. Système de credits/vouchers



