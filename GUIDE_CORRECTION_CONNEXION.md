# 🔧 GUIDE DE CORRECTION - PROBLÈME DE CONNEXION FRONTEND-BACKEND

## 🚨 **PROBLÈMES IDENTIFIÉS :**

1. **Erreur 500 sur `/events/`** - Sérialiseur complexe causant des erreurs
2. **Erreur 401 sur `/auth/token/`** - Utilisateur admin manquant
3. **Configuration CORS incorrecte** - Domaines Vercel non autorisés
4. **URLs de configuration incorrectes**

## ✅ **CORRECTIONS APPLIQUÉES :**

### 1. **Configuration CORS corrigée**
```python
# backend/event_management/settings.py
CORS_ALLOWED_ORIGINS = [
    "https://event-management-system-three-bay.vercel.app",
    "https://event-management-frontend.vercel.app", 
    "https://event-management-frontend-git-main.vercel.app",
    "https://event-management-frontend-git-develop.vercel.app",
    "https://*.vercel.app",  # Tous les sous-domaines Vercel
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

### 2. **Sérialiseurs simplifiés créés**
- `backend/events/simple_serializers.py` - Sérialiseurs sans relations complexes
- `backend/events/simple_views.py` - Vues simplifiées pour éviter les erreurs 500
- URLs mises à jour pour utiliser les vues simplifiées

### 3. **Script de création d'utilisateur de test**
- `backend/create_test_user.py` - Crée un utilisateur admin pour les tests

## 🚀 **ÉTAPES DE DÉPLOIEMENT :**

### **Backend (Render) :**

1. **Créer l'utilisateur de test :**
```bash
cd backend
python create_test_user.py
```

2. **Redéployer le backend sur Render :**
   - Les fichiers modifiés seront automatiquement déployés
   - Vérifier que le déploiement s'est bien passé

3. **Tester la connexion :**
```bash
python test_connection.py
```

### **Frontend (Vercel) :**

1. **Vérifier la configuration Vercel :**
   - Le fichier `vercel.json` est déjà correct
   - Les variables d'environnement sont définies

2. **Redéployer le frontend :**
   - Push les changements sur GitHub
   - Vercel redéploiera automatiquement

## 🔍 **VÉRIFICATIONS :**

### **1. Test du backend :**
```bash
curl https://event-management-backend-7uux.onrender.com/api/events/
```
**Résultat attendu :** Status 200 avec liste des événements

### **2. Test de l'authentification :**
```bash
curl -X POST https://event-management-backend-7uux.onrender.com/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```
**Résultat attendu :** Status 200 avec tokens JWT

### **3. Test CORS :**
```bash
curl -H "Origin: https://event-management-system-three-bay.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS https://event-management-backend-7uux.onrender.com/api/events/
```
**Résultat attendu :** Status 200 avec en-têtes CORS

## 🎯 **IDENTIFIANTS DE TEST :**

- **Super Admin :** `admin` / `admin123`
- **Utilisateur normal :** `testuser` / `test123`

## 📱 **TEST FRONTEND :**

1. Aller sur votre site Vercel
2. Essayer de se connecter avec `admin` / `admin123`
3. Vérifier que les événements s'affichent
4. Vérifier la console pour les erreurs

## 🚨 **SI LES PROBLÈMES PERSISTENT :**

1. **Vérifier les logs Render :**
   - Aller sur le dashboard Render
   - Consulter les logs de déploiement

2. **Vérifier les logs Vercel :**
   - Aller sur le dashboard Vercel
   - Consulter les logs de build et de déploiement

3. **Tester avec curl :**
   - Utiliser les commandes de test ci-dessus
   - Identifier l'endpoint qui pose problème

## ✅ **RÉSULTAT ATTENDU :**

Après ces corrections, vous devriez pouvoir :
- ✅ Vous connecter avec les identifiants admin
- ✅ Voir la liste des événements
- ✅ Naviguer dans l'application sans erreurs 500/401
- ✅ Avoir une connexion stable entre frontend et backend

---

**🎉 Votre application devrait maintenant fonctionner correctement !**
