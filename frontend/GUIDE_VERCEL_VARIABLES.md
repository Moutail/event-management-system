# 🔧 Guide Variables d'Environnement Vercel

## ✅ Problème Résolu

J'ai supprimé la section `env` du `vercel.json` pour éviter les conflits avec les variables secrètes. Maintenant, configurez les variables directement dans l'interface Vercel.

## 🚀 Configuration Vercel

### **1. Déployez d'abord le projet**

1. Poussez le code sur GitHub
2. Importez le projet dans Vercel
3. Sélectionnez le dossier `frontend`

### **2. Configurez les Variables d'Environnement**

Dans l'interface Vercel, allez dans **Settings > Environment Variables** et ajoutez :

#### **Variables Requises :**

```
REACT_APP_API_URL = https://event-management-backend-7uux.onrender.com/api
REACT_APP_BASE_URL = https://event-management-backend-7uux.onrender.com
REACT_APP_STRIPE_PK = pk_test_51RxzOq2NgztfBRhsPKZ5VAUd2GIGiBN220HOaG2Egpie9JSLGo5aK4nYG29g9ejU30CCGziRyNUJos71iCnmQfHv00L5znX6H1
```

#### **Variables Optionnelles (si vous les utilisez) :**

```
REACT_APP_GOOGLE_CLIENT_ID = votre_google_client_id
REACT_APP_FACEBOOK_APP_ID = votre_facebook_app_id
```

### **3. Redéployez**

Après avoir ajouté les variables, redéployez le projet.

## 🔍 Vérification

### **Vérifiez que les variables sont bien chargées :**

1. **Ouvrez** votre site Vercel
2. **Ouvrez** les outils de développement (F12)
3. **Console** : Tapez `console.log(process.env.REACT_APP_STRIPE_PK)`
4. **Vérifiez** que la clé Stripe s'affiche

## 🚨 Résolution de Problèmes

### **Erreur "Secret does not exist" :**
- ✅ **Résolu** : Supprimé les références `@secret` du vercel.json
- ✅ **Solution** : Utilisez l'interface Vercel pour les variables

### **Variables non chargées :**
- Vérifiez l'orthographe des noms de variables
- Assurez-vous qu'elles commencent par `REACT_APP_`
- Redéployez après avoir ajouté les variables

### **Erreur Stripe :**
- Vérifiez que `REACT_APP_STRIPE_PK` est bien définie
- Testez avec les cartes de test Stripe

## 📋 Checklist Déploiement

- [ ] Code poussé sur GitHub
- [ ] Projet importé dans Vercel
- [ ] Variables d'environnement ajoutées
- [ ] Déploiement réussi
- [ ] Site accessible
- [ ] Variables chargées (vérification console)
- [ ] Test de paiement Stripe

## 🎯 Prochaines Étapes

1. **Ajoutez** les variables dans Vercel
2. **Redéployez** le projet
3. **Testez** le site
4. **Vérifiez** les paiements Stripe

---

**Votre configuration Vercel est maintenant simplifiée ! 🚀**
