# 💳 Guide Configuration Stripe pour Vercel

## 🔍 Problème Résolu

Votre clé Stripe de test est maintenant configurée dans Vercel. Voici les détails :

### **Clé Stripe Configurée :**
```
pk_test_51RxzOq2NgztfBRhsPKZ5VAUd2GIGiBN220HOaG2Egpie9JSLGo5aK4nYG29g9ejU30CCGziRyNUJos71iCnmQfHv00L5znX6H1
```

## 🚀 Déploiement Vercel

### **Variables d'Environnement à configurer dans Vercel :**

1. **REACT_APP_API_URL** = `https://event-management-backend-7uux.onrender.com/api`
2. **REACT_APP_BASE_URL** = `https://event-management-backend-7uux.onrender.com`
3. **REACT_APP_STRIPE_PK** = `pk_test_51RxzOq2NgztfBRhsPKZ5VAUd2GIGiBN220HOaG2Egpie9JSLGo5aK4nYG29g9ejU30CCGziRyNUJos71iCnmQfHv00L5znX6H1`
4. **REACT_APP_GOOGLE_CLIENT_ID** = `votre_google_client_id`
5. **REACT_APP_FACEBOOK_APP_ID** = `votre_facebook_app_id`

## 🔄 Migration vers Production

### **Quand vous serez prêt pour la production :**

1. **Activez votre compte Stripe** (si pas déjà fait)
2. **Générez vos clés live** dans le dashboard Stripe
3. **Remplacez** `pk_test_...` par `pk_live_...`
4. **Mettez à jour** les variables d'environnement Vercel

### **Clés Stripe Live :**
```
REACT_APP_STRIPE_PK = pk_live_votre_cle_publique_live
```

## 🧪 Test des Paiements

### **Mode Test (Actuel) :**
- ✅ **Cartes de test** : Utilisez les cartes Stripe de test
- ✅ **Pas de vrais paiements** : Aucun argent réel ne sera débité
- ✅ **Dashboard Stripe** : Voir les paiements de test

### **Cartes de Test Stripe :**
```
Visa : 4242 4242 4242 4242
Mastercard : 5555 5555 5555 4444
American Express : 3782 822463 10005
```

## 🔧 Configuration Backend

Assurez-vous que votre backend utilise aussi la clé secrète de test :

### **Variables d'environnement Backend (Render) :**
```
STRIPE_SECRET_KEY = sk_test_votre_cle_secrete_test
STRIPE_PUBLISHABLE_KEY = pk_test_51RxzOq2NgztfBRhsPKZ5VAUd2GIGiBN220HOaG2Egpie9JSLGo5aK4nYG29g9ejU30CCGziRyNUJos71iCnmQfHv00L5znX6H1
```

## 📊 Monitoring

### **Dashboard Stripe :**
- **Mode Test** : [dashboard.stripe.com/test](https://dashboard.stripe.com/test)
- **Mode Live** : [dashboard.stripe.com](https://dashboard.stripe.com)

### **Logs Vercel :**
- Vérifiez les logs de build pour les erreurs Stripe
- Testez les paiements après déploiement

## 🚨 Résolution de Problèmes

### **Erreur "Invalid API Key" :**
- Vérifiez que la clé est correctement copiée
- Assurez-vous qu'il n'y a pas d'espaces avant/après

### **Erreur "Test mode" :**
- C'est normal en mode test
- Les paiements ne seront pas réels

### **Erreur CORS :**
- Le backend est configuré pour accepter Vercel
- Vérifiez la configuration CORS dans Django

## 🎯 Prochaines Étapes

1. **Déployez** sur Vercel avec la clé de test
2. **Testez** les paiements avec les cartes de test
3. **Vérifiez** que tout fonctionne
4. **Migrez** vers les clés live quand prêt

## 📞 Support

- **Documentation Stripe** : [stripe.com/docs](https://stripe.com/docs)
- **Support Stripe** : [support.stripe.com](https://support.stripe.com)
- **Vercel Support** : [vercel.com/help](https://vercel.com/help)

---

**Votre configuration Stripe est prête pour Vercel ! 💳**
