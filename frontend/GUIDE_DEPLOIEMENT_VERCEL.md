# 🚀 Guide de Déploiement Frontend sur Vercel

## ✅ Configuration Prête

Votre frontend est déjà configuré pour Vercel avec :
- ✅ `vercel.json` configuré
- ✅ `package.json` avec scripts de build
- ✅ Variables d'environnement définies
- ✅ Backend URL mise à jour

## 📋 Étapes de Déploiement

### 1. **Préparation du Repository**

Assurez-vous que votre code est poussé sur GitHub :
```bash
# Test local avant déploiement
cd frontend
node test-build.js

# Si le test réussit, pousser sur GitHub
git add .
git commit -m "Configuration Vercel corrigée pour CRACO"
git push origin main
```

### 2. **Déploiement sur Vercel**

#### **Option A : Via l'interface Vercel (Recommandé)**

1. **Connectez-vous** à [vercel.com](https://vercel.com)
2. **Cliquez** sur "New Project"
3. **Importez** votre repository GitHub
4. **Sélectionnez** le dossier `frontend` comme racine
5. **Configurez** les variables d'environnement (voir section ci-dessous)
6. **Cliquez** sur "Deploy"

#### **Option B : Via Vercel CLI**

```bash
# Installer Vercel CLI
npm i -g vercel

# Se connecter à Vercel
vercel login

# Déployer depuis le dossier frontend
cd frontend
vercel

# Suivre les instructions
```

### 3. **Configuration des Variables d'Environnement**

Dans l'interface Vercel, ajoutez ces variables :

```
REACT_APP_API_URL = https://event-management-backend-7uux.onrender.com/api
REACT_APP_BASE_URL = https://event-management-backend-7uux.onrender.com
REACT_APP_STRIPE_PK = pk_live_votre_cle_stripe_publique
REACT_APP_GOOGLE_CLIENT_ID = votre_google_client_id
REACT_APP_FACEBOOK_APP_ID = votre_facebook_app_id
```

### 4. **Configuration du Build**

Vercel détectera automatiquement :
- **Framework** : Create React App
- **Build Command** : `npm run build`
- **Output Directory** : `build`
- **Install Command** : `npm install`

## 🔧 Configuration Avancée

### **vercel.json** (déjà configuré)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/media/(.*)",
      "dest": "https://event-management-backend-7uux.onrender.com/media/$1"
    },
    {
      "src": "/api/(.*)",
      "dest": "https://event-management-backend-7uux.onrender.com/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

### **Redirection des API**

Les requêtes `/api/*` sont automatiquement redirigées vers votre backend Render.

## 🧪 Test du Déploiement

### **URLs de Test**

1. **Page d'accueil** : `https://votre-projet.vercel.app`
2. **API Health** : `https://votre-projet.vercel.app/api/health/`
3. **Admin** : `https://votre-projet.vercel.app/admin/`

### **Vérifications**

- ✅ **Chargement** de la page d'accueil
- ✅ **Connexion** au backend (vérifier les requêtes réseau)
- ✅ **Authentification** (login/register)
- ✅ **Création d'événements**
- ✅ **Paiements Stripe**

## 🚨 Résolution de Problèmes

### **Erreur de Build CRACO/cross-spawn**

Si vous rencontrez l'erreur `Cannot find module './lib/parse'` :

```bash
# Solution 1: Nettoyer et rebuilder avec CRACO
rm -rf node_modules package-lock.json
npm ci --legacy-peer-deps
npm run build

# Solution 2: Test de build local
node test-build.js
```

### **Erreur de Build Générale**

```bash
# Nettoyer et rebuilder
rm -rf node_modules package-lock.json
npm ci --legacy-peer-deps
npm run build
```

### **Erreur CORS**

Le backend est configuré avec `CORS_ALLOW_ALL_ORIGINS = True`, donc pas de problème CORS.

### **Variables d'Environnement**

Vérifiez que toutes les variables sont correctement définies dans Vercel.

### **Redirection API**

Si les requêtes API ne fonctionnent pas, vérifiez la configuration des routes dans `vercel.json`.

## 📊 Monitoring

### **Vercel Analytics**

- **Performance** : Temps de chargement
- **Erreurs** : Erreurs JavaScript
- **Trafic** : Visiteurs et pages vues

### **Logs**

- **Build Logs** : Dans l'interface Vercel
- **Function Logs** : Pour les redirections API
- **Real-time Logs** : Via Vercel CLI

## 🔄 Déploiements Automatiques

### **GitHub Integration**

- ✅ **Push automatique** : Chaque push sur `main` déclenche un déploiement
- ✅ **Preview** : Les pull requests créent des previews
- ✅ **Rollback** : Possibilité de revenir à une version précédente

### **Branches**

- **Production** : `main` → `votre-projet.vercel.app`
- **Preview** : `feature/*` → `votre-projet-git-feature.vercel.app`

## 🎯 Prochaines Étapes

1. **Déployez** sur Vercel
2. **Testez** toutes les fonctionnalités
3. **Configurez** un domaine personnalisé (optionnel)
4. **Activez** Vercel Analytics
5. **Configurez** les webhooks pour les notifications

## 📞 Support

- **Documentation Vercel** : [vercel.com/docs](https://vercel.com/docs)
- **Community** : [github.com/vercel/vercel/discussions](https://github.com/vercel/vercel/discussions)
- **Status** : [vercel-status.com](https://vercel-status.com)

---

**Votre frontend est prêt pour Vercel ! 🚀**
