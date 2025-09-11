# 🚀 GUIDE DE DÉPLOIEMENT COMPLET

## 📋 **ÉTAPES POUR DÉPLOYER VOS CHANGEMENTS :**

### **1. PRÉPARATION LOCALE :**

```bash
# 1. Vérifier que tous les fichiers sont ajoutés
git status

# 2. Ajouter tous les nouveaux fichiers
git add .

# 3. Commiter les changements
git commit -m "Fix: Correction connexion frontend-backend + création super admin"

# 4. Pousser vers GitHub
git push origin main
```

### **2. VÉRIFICATION RENDER (Backend) :**

**A. Vérifier la configuration :**
- ✅ Service connecté à GitHub
- ✅ Auto-deploy activé
- ✅ Branche : `main`
- ✅ Build Command : `chmod +x build.sh && ./build.sh`
- ✅ Start Command : `gunicorn event_management.wsgi:application`

**B. Surveiller le déploiement :**
1. Allez sur le dashboard Render
2. Cliquez sur votre service backend
3. Allez dans l'onglet "Logs"
4. Surveillez les logs de build

**C. Logs attendus :**
```
🚀 Démarrage du build sur Render...
📦 Installation des dépendances...
🗄️ Application des migrations...
👑 Création du super admin...
📁 Collecte des fichiers statiques...
✅ Build terminé avec succès !
```

### **3. VÉRIFICATION VERCEL (Frontend) :**

**A. Vérifier la configuration :**
- ✅ Projet connecté à GitHub
- ✅ Auto-deploy activé
- ✅ Branche : `main`
- ✅ Framework : Create React App
- ✅ Build Command : `GENERATE_SOURCEMAP=false npm run build`

**B. Surveiller le déploiement :**
1. Allez sur le dashboard Vercel
2. Cliquez sur votre projet frontend
3. Allez dans l'onglet "Deployments"
4. Surveillez le statut du déploiement

### **4. TESTS DE VÉRIFICATION :**

**A. Test du backend :**
```bash
# Test de l'API
curl https://event-management-backend-7uux.onrender.com/api/events/

# Test de l'authentification
curl -X POST https://event-management-backend-7uux.onrender.com/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**B. Test du frontend :**
1. Allez sur votre site Vercel
2. Ouvrez la console développeur (F12)
3. Vérifiez qu'il n'y a plus d'erreurs 500/401
4. Essayez de vous connecter avec `admin` / `admin123`

### **5. DÉPANNAGE :**

**Si Render ne se déploie pas :**
- Vérifiez les logs d'erreur
- Vérifiez que le fichier `build.sh` est exécutable
- Vérifiez que toutes les dépendances sont dans `requirements.txt`

**Si Vercel ne se déploie pas :**
- Vérifiez les logs de build
- Vérifiez que `package.json` est correct
- Vérifiez que `vercel.json` est valide

**Si la connexion ne fonctionne pas :**
- Vérifiez les URLs dans `vercel.json`
- Vérifiez la configuration CORS dans `settings.py`
- Vérifiez que le super admin a été créé

## 🎯 **RÉSULTAT ATTENDU :**

Après le déploiement, vous devriez avoir :
- ✅ Backend accessible sur Render
- ✅ Frontend accessible sur Vercel
- ✅ Connexion fonctionnelle entre les deux
- ✅ Super admin créé (`admin` / `admin123`)
- ✅ Plus d'erreurs 500/401 dans la console

---

**🚀 Suivez ces étapes et vos changements seront déployés automatiquement !**