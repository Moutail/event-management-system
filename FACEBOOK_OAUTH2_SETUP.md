# 🔐 Configuration Facebook OAuth2 - Guide Complet

## 🚀 **Étape 1 : Créer une application Facebook**

1. **Allez sur [Facebook Developers](https://developers.facebook.com/)**
2. **Cliquez sur "Se connecter" avec votre compte Facebook**
3. **Cliquez sur "Créer une application"**
4. **Sélectionnez "Consommateur" comme type d'application**
5. **Nom de l'application** : `Event Management System`
6. **Email de contact** : Votre email
7. **Cliquez sur "Créer une application"**

## 🔧 **Étape 2 : Ajouter le produit Facebook Login**

1. **Dans le tableau de bord de votre application, cliquez sur "Ajouter un produit"**
2. **Recherchez "Facebook Login" et cliquez sur "Configurer"**
3. **Sélectionnez "Web" comme plateforme**
4. **URL du site** : `http://localhost:3000`
5. **Cliquez sur "Enregistrer et continuer"**

## ⚙️ **Étape 3 : Configurer Facebook Login**

1. **Dans le menu latéral, cliquez sur "Facebook Login" > "Paramètres"**
2. **URIs de redirection OAuth valides** :
   - `http://localhost:3000/auth/facebook/callback`
   - `http://127.0.0.1:3000/auth/facebook/callback`
3. **Cliquez sur "Enregistrer les modifications"**

## 🔑 **Étape 4 : Récupérer les clés**

1. **Dans le menu latéral, cliquez sur "Paramètres" > "Général"**
2. **Copiez l'"ID de l'application"** (ex: `123456789012345`)
3. **Cliquez sur "Afficher" à côté de "Secret de l'application"**
4. **Copiez le "Secret de l'application"** (ex: `abcdefghijklmnopqrstuvwxyz123456`)

## 🔧 **Étape 5 : Configurer l'écran de consentement**

1. **Dans le menu latéral, cliquez sur "Facebook Login" > "Paramètres"**
2. **Scopes et permissions** :
   - ✅ `email` (obligatoire)
   - ✅ `public_profile` (obligatoire)
3. **Cliquez sur "Enregistrer les modifications"**

## 📋 **Étape 6 : Mettre à jour les fichiers .env**

### **Backend (.env)**
```env
FACEBOOK_APP_ID=votre-app-id-ici
FACEBOOK_APP_SECRET=votre-app-secret-ici
FACEBOOK_REDIRECT_URI=http://localhost:3000/auth/facebook/callback
```

### **Frontend (.env)**
```env
REACT_APP_FACEBOOK_APP_ID=votre-app-id-ici
REACT_APP_FACEBOOK_REDIRECT_URI=http://localhost:3000/auth/facebook/callback
```

## 🧪 **Étape 7 : Tester la configuration**

1. **Redémarrez le serveur backend** : `python manage.py runserver 8001`
2. **Redémarrez le frontend** : `npm start`
3. **Allez sur la page de connexion**
4. **Cliquez sur "Continuer avec Facebook"**
5. **Vérifiez que vous êtes redirigé vers Facebook**

## 🚨 **Dépannage**

### **Erreur "Identifiant d'application invalide"**
- Vérifiez que l'APP_ID dans `.env` est correct
- Vérifiez que l'application Facebook est active
- Vérifiez que Facebook Login est configuré

### **Erreur "redirect_uri_mismatch"**
- Vérifiez que l'URI dans `.env` correspond exactement à celui dans Facebook
- Pas d'espaces en trop, pas de slash final

### **Erreur "App not configured"**
- Vérifiez que l'application Facebook est en mode développement
- Vérifiez que vous êtes connecté avec un compte développeur

## ✅ **Vérification finale**

- ✅ Application Facebook créée
- ✅ Produit Facebook Login ajouté
- ✅ URIs de redirection configurés
- ✅ Scopes et permissions configurés
- ✅ Fichiers .env mis à jour
- ✅ Test de connexion réussi

---

**🎉 Facebook OAuth2 est maintenant configuré !**






