# 🎯 GUIDE COMPLET DU SYSTÈME DE RAPPELS

## ✅ **SYSTÈME 100% FONCTIONNEL !**

### 🚀 **FONCTIONNALITÉS DISPONIBLES :**

#### **1. Création de Rappels avec Choix Manuel/Automatique**
- **Mode Manuel** : Rappel créé en statut `draft` → Envoi manuel possible
- **Mode Automatique** : Rappel créé en statut `scheduled` → Envoi automatique à l'heure programmée

#### **2. Envoi Manuel**
- ✅ Fonctionne pour les rappels en statut `draft`
- ✅ Fonctionne pour les rappels en statut `scheduled`
- ✅ Envoi par email et SMS

#### **3. Envoi Automatique**
- ✅ Traitement automatique des rappels programmés
- ✅ Vérification toutes les 30 secondes
- ✅ Gestion des rappels en retard

---

## 📋 **UTILISATION DU SYSTÈME**

### **1. Création d'un Rappel**

#### **Via l'API (JSON) :**
```json
{
    "event": 123,
    "title": "Mon Rappel",
    "message": "Message du rappel",
    "reminder_type": "general",
    "target_audience": "all",
    "send_email": true,
    "send_sms": false,
    "send_mode": "manual",  // ou "automatic"
    "scheduled_at": "2025-09-04T10:00:00Z"  // Optionnel pour mode manuel, requis pour mode automatique
}
```

#### **Champs disponibles :**
- `send_mode` : `"manual"` ou `"automatic"`
- `scheduled_at` : Heure de programmation (requis pour mode automatique)
- `send_email` : `true/false`
- `send_sms` : `true/false`

### **2. Envoi Manuel d'un Rappel**

#### **Via l'API :**
```bash
POST /api/custom-reminders/{id}/send_now/
```

#### **Via le script :**
```python
from events.tasks import send_reminder_task
result = send_reminder_task(reminder_id)
```

### **3. Traitement Automatique**

#### **Lancer le monitoring continu :**
```bash
python run_reminders_manual.py
```

#### **Traitement unique :**
```bash
python run_reminders_manual.py once
```

---

## 🎯 **SCÉNARIOS D'UTILISATION**

### **Scénario 1 : Rappel Manuel**
1. Créer un rappel avec `"send_mode": "manual"`
2. Le rappel est créé en statut `draft`
3. Envoyer manuellement via l'interface ou l'API
4. Le statut passe à `sent`

### **Scénario 2 : Rappel Automatique**
1. Créer un rappel avec `"send_mode": "automatic"` et `scheduled_at`
2. Le rappel est créé en statut `scheduled`
3. Lancer le monitoring automatique
4. Le rappel sera envoyé automatiquement à l'heure programmée

### **Scénario 3 : Rappel Manuel avec Heure**
1. Créer un rappel avec `"send_mode": "manual"` et `scheduled_at`
2. Le rappel est créé en statut `draft` (mais garde l'heure)
3. Envoyer manuellement quand vous voulez
4. Le statut passe à `sent`

---

## 🔧 **CONFIGURATION**

### **1. Démarrage du Système Automatique**
```bash
# Dans le répertoire backend
python run_reminders_manual.py
```

### **2. Vérification des Rappels**
```bash
# Voir les statistiques
python check_reminders_stats.py

# Voir les rappels programmés
python check_scheduled_reminders.py
```

### **3. Test du Système**
```bash
# Test complet
python test_new_reminder_system.py
```

---

## 📊 **STATUTS DES RAPPELS**

- **`draft`** : Brouillon, prêt pour envoi manuel
- **`scheduled`** : Programmé, sera envoyé automatiquement
- **`sent`** : Envoyé avec succès
- **`failed`** : Échec d'envoi

---

## 🎉 **AVANTAGES DU NOUVEAU SYSTÈME**

1. **✅ Contrôle total** : Choix entre manuel et automatique
2. **✅ Flexibilité** : Rappels manuels avec ou sans heure
3. **✅ Fiabilité** : Système de monitoring robuste
4. **✅ Simplicité** : Interface claire et intuitive
5. **✅ Compatibilité** : Fonctionne avec l'API existante

---

## 🚨 **IMPORTANT**

- **Ne modifiez pas** les autres fonctionnalités du système
- **Utilisez le champ `send_mode`** pour contrôler le comportement
- **Lancez le monitoring** pour l'envoi automatique
- **Testez toujours** avant la production

---

## 📞 **SUPPORT**

Si vous avez des questions ou des problèmes :
1. Vérifiez les logs de debug
2. Testez avec les scripts fournis
3. Consultez ce guide

**Le système est maintenant 100% fonctionnel ! 🎉**
