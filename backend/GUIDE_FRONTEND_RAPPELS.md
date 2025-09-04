# 🎯 GUIDE FRONTEND POUR LE SYSTÈME DE RAPPELS

## ✅ **API BACKEND 100% FONCTIONNELLE !**

L'API backend fonctionne parfaitement. Le problème vient du frontend qui n'est pas encore configuré pour utiliser le nouveau champ `send_mode`.

---

## 🔧 **MODIFICATIONS NÉCESSAIRES CÔTÉ FRONTEND**

### **1. Ajouter le champ `send_mode` dans le formulaire**

Dans `CreateReminderDialog.js`, ajoutez ce champ :

```javascript
// Dans l'état initial du composant
const [formData, setFormData] = useState({
  // ... autres champs existants
  send_mode: 'manual', // Nouveau champ
});

// Dans le formulaire JSX, ajoutez ce bouton de sélection
<div className="form-group">
  <label htmlFor="send_mode">Mode d'envoi :</label>
  <div className="radio-group">
    <label className="radio-option">
      <input
        type="radio"
        name="send_mode"
        value="manual"
        checked={formData.send_mode === 'manual'}
        onChange={(e) => setFormData({...formData, send_mode: e.target.value})}
      />
      <span>📝 Envoi manuel (brouillon)</span>
    </label>
    <label className="radio-option">
      <input
        type="radio"
        name="send_mode"
        value="automatic"
        checked={formData.send_mode === 'automatic'}
        onChange={(e) => setFormData({...formData, send_mode: e.target.value})}
      />
      <span>⏰ Envoi automatique (programmé)</span>
    </label>
  </div>
</div>
```

### **2. Gestion conditionnelle du champ `scheduled_at`**

```javascript
// Afficher le champ de programmation seulement en mode automatique
{formData.send_mode === 'automatic' && (
  <div className="form-group">
    <label htmlFor="scheduled_at">Date et heure d'envoi :</label>
    <input
      type="datetime-local"
      id="scheduled_at"
      value={formData.scheduled_at || ''}
      onChange={(e) => setFormData({...formData, scheduled_at: e.target.value})}
      required={formData.send_mode === 'automatic'}
    />
  </div>
)}
```

### **3. Validation côté frontend**

```javascript
const validateForm = () => {
  const errors = {};
  
  // ... validations existantes
  
  // Validation pour le mode automatique
  if (formData.send_mode === 'automatic') {
    if (!formData.scheduled_at) {
      errors.scheduled_at = 'Une date et heure sont requises pour l\'envoi automatique';
    } else {
      const scheduledDate = new Date(formData.scheduled_at);
      const now = new Date();
      if (scheduledDate <= now) {
        errors.scheduled_at = 'La date doit être dans le futur';
      }
    }
  }
  
  return errors;
};
```

### **4. Envoi des données à l'API**

```javascript
const handleSubmit = async (e) => {
  e.preventDefault();
  
  const errors = validateForm();
  if (Object.keys(errors).length > 0) {
    setErrors(errors);
    return;
  }
  
  try {
    const payload = {
      ...formData,
      // Convertir la date en format ISO si nécessaire
      scheduled_at: formData.scheduled_at ? new Date(formData.scheduled_at).toISOString() : null,
    };
    
    const response = await api.post('/custom-reminders/', payload);
    
    if (response.status === 201) {
      // Succès
      console.log('Rappel créé:', response.data);
      // Fermer le dialogue ou rediriger
    }
  } catch (error) {
    console.error('Erreur lors de la sauvegarde:', error);
    setErrors({ general: 'Erreur lors de la création du rappel' });
  }
};
```

---

## 🎨 **STYLES CSS SUGGÉRÉS**

```css
.radio-group {
  display: flex;
  gap: 20px;
  margin-top: 8px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.radio-option:hover {
  border-color: #007bff;
  background-color: #f8f9fa;
}

.radio-option input[type="radio"] {
  margin: 0;
}

.radio-option input[type="radio"]:checked + span {
  font-weight: bold;
  color: #007bff;
}

.radio-option:has(input[type="radio"]:checked) {
  border-color: #007bff;
  background-color: #e3f2fd;
}
```

---

## 📋 **COMPORTEMENT ATTENDU**

### **Mode Manuel (par défaut) :**
- ✅ Rappel créé en statut `draft`
- ✅ Pas de champ `scheduled_at` requis
- ✅ Envoi manuel possible via bouton "Envoyer maintenant"
- ✅ Contrôle total sur l'envoi

### **Mode Automatique :**
- ✅ Champ `scheduled_at` requis
- ✅ Validation que la date est dans le futur
- ✅ Rappel créé en statut `scheduled`
- ✅ Envoi automatique à l'heure programmée

---

## 🔍 **DÉBOGAGE**

### **Si l'erreur persiste :**

1. **Vérifiez la console du navigateur** pour voir l'erreur exacte
2. **Vérifiez les données envoyées** dans l'onglet Network
3. **Vérifiez l'authentification** (token JWT valide)
4. **Vérifiez la structure des données** envoyées à l'API

### **Exemple de données correctes :**

```json
{
  "event": 123,
  "title": "Mon Rappel",
  "message": "Message du rappel",
  "reminder_type": "general",
  "target_audience": "all",
  "send_email": true,
  "send_sms": false,
  "send_mode": "manual",
  "scheduled_at": "2025-09-04T10:00:00Z"  // Optionnel pour mode manuel
}
```

---

## 🎉 **RÉSULTAT FINAL**

Avec ces modifications, vous aurez :

1. **✅ Choix manuel/automatique** dans le formulaire
2. **✅ Validation appropriée** selon le mode choisi
3. **✅ Interface intuitive** et claire
4. **✅ Compatibilité totale** avec l'API backend
5. **✅ Contrôle total** sur le comportement des rappels

**L'API backend est prête, il ne reste plus qu'à adapter le frontend ! 🚀**
