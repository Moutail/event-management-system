# 🔐 Configuration Google OAuth2 - Guide Complet

## 🚀 **Étape 1 : Créer un projet Google Cloud**

1. **Allez sur [Google Cloud Console](https://console.cloud.google.com/)**
2. **Cliquez sur "Sélectionner un projet" puis "Nouveau projet"**
3. **Nom du projet** : `event-management-system`
4. **Cliquez sur "Créer"**

## 🔧 **Étape 2 : Activer l'API Google+ API**

1. **Dans le menu latéral, cliquez sur "APIs et services" > "Bibliothèque"**
2. **Recherchez "Google+ API"**
3. **Cliquez sur "Google+ API" puis "Activer"**

## 🔑 **Étape 3 : Créer les identifiants OAuth2**

1. **Dans le menu latéral, cliquez sur "APIs et services" > "Identifiants"**
2. **Cliquez sur "Créer des identifiants" > "ID client OAuth 2.0"**
3. **Si demandé, configurez l'écran de consentement OAuth :**
   - **Nom de l'application** : `Event Management System`
   - **Email de support** : Votre email
   - **Domaine de l'application** : `localhost` (pour le développement)

## ⚙️ **Étape 4 : Configurer l'ID client OAuth2**

1. **Type d'application** : `Application Web`
2. **Nom** : `Event Management System Web Client`
3. **URIs de redirection autorisés** :
   - `http://localhost:3000/auth/google/callback`
   - `http://127.0.0.1:3000/auth/google/callback`
4. **Cliquez sur "Créer"**

## 📋 **Étape 5 : Récupérer les clés**

1. **Copiez le "ID client"** (ex: `123456789-abcdefghijklmnop.apps.googleusercontent.com`)
2. **Copiez le "Secret client"** (ex: `GOCSPX-abcdefghijklmnopqrstuvwxyz`)

## 🔧 **Étape 6 : Mettre à jour les fichiers .env**

### **Backend (.env)**
```env
GOOGLE_CLIENT_ID=votre-id-client-ici
GOOGLE_CLIENT_SECRET=votre-secret-client-ici
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
```

### **Frontend (.env)**
```env
REACT_APP_GOOGLE_CLIENT_ID=votre-id-client-ici
REACT_APP_GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback
```

## 🧪 **Étape 7 : Tester la configuration**

1. **Redémarrez le serveur backend** : `python manage.py runserver 8001`
2. **Redémarrez le frontend** : `npm start`
3. **Allez sur la page de connexion**
4. **Cliquez sur "Continuer avec Google"**
5. **Vérifiez que vous êtes redirigé vers Google**

## 🚨 **Dépannage**

### **Erreur "Access blocked"**
- Vérifiez que l'API Google+ API est activée
- Vérifiez que l'écran de consentement est configuré
- Vérifiez que les URIs de redirection sont corrects

### **Erreur "redirect_uri_mismatch"**
- Vérifiez que l'URI dans `.env` correspond exactement à celui dans Google Cloud Console
- Pas d'espaces en trop, pas de slash final

## ✅ **Vérification finale**

- ✅ Projet Google Cloud créé
- ✅ API Google+ API activée
- ✅ ID client OAuth2 créé
- ✅ URIs de redirection configurés
- ✅ Fichiers .env mis à jour
- ✅ Test de connexion réussi

---

**🎉 Google OAuth2 est maintenant configuré !**





