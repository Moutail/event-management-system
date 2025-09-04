# 🔐 Authentification Sociale - Guide d'utilisation

## 🎯 Vue d'ensemble

Votre système de gestion d'événements supporte maintenant l'authentification via **Google** et **Facebook** ! Les utilisateurs peuvent se connecter ou s'inscrire en un clic sans avoir à créer de mot de passe.

## ✨ Fonctionnalités

- 🔐 **Connexion Google** - Authentification OAuth2 avec Google
- 🔐 **Connexion Facebook** - Authentification OAuth2 avec Facebook
- 👤 **Création automatique de comptes** - Nouveaux utilisateurs
- 🔗 **Liaison de comptes** - Utilisateurs existants
- 🎭 **Gestion des rôles** - Attribution automatique du rôle "participant"
- 🔒 **Sécurité renforcée** - Protection CSRF et validation des tokens

## 🚀 Comment ça marche

### 1. **Côté utilisateur**
1. L'utilisateur clique sur "Continuer avec Google" ou "Continuer avec Facebook"
2. Il est redirigé vers la page d'authentification du provider
3. Après authentification, il revient sur votre site
4. Un compte est créé automatiquement ou lié à un compte existant
5. L'utilisateur est connecté et redirigé selon son rôle

### 2. **Côté technique**
1. **Frontend** : Redirection vers l'URL OAuth2 du provider
2. **Provider** : Authentification et retour avec un code d'autorisation
3. **Backend** : Échange du code contre un token d'accès
4. **Backend** : Récupération des informations utilisateur
5. **Backend** : Création/liaison du compte et génération du JWT
6. **Frontend** : Connexion automatique avec le JWT

## 🔧 Configuration requise

### **Variables d'environnement Backend** (`.env`)
```env
# Google OAuth2
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Facebook OAuth2
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
FACEBOOK_REDIRECT_URI=http://localhost:3000/auth/facebook/callback
```

### **Variables d'environnement Frontend** (`.env`)
```env
# Google OAuth2
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
REACT_APP_GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Facebook OAuth2
REACT_APP_FACEBOOK_APP_ID=your-facebook-app-id
REACT_APP_FACEBOOK_REDIRECT_URI=http://localhost:3000/auth/facebook/callback
```

## 📱 Interface utilisateur

### **Page de connexion**
- Bouton "Continuer avec Google" (rouge)
- Bouton "Continuer avec Facebook" (bleu)
- Séparateur "ou continuer avec"
- Message de sécurité expliquant le processus

### **Pages de callback**
- Page de chargement pendant l'authentification
- Gestion des erreurs avec redirection
- Messages informatifs pour l'utilisateur

## 🔒 Sécurité

### **Protection CSRF**
- Paramètre `state` aléatoire pour chaque requête
- Validation côté serveur
- Protection contre les attaques CSRF

### **Validation des tokens**
- Vérification des tokens avec les APIs Google/Facebook
- Validation des scopes et permissions
- Gestion des tokens expirés

### **Stockage sécurisé**
- Tokens chiffrés en base de données
- Pas de stockage côté client
- Expiration automatique des tokens

## 🧪 Tests

### **Test des modèles**
```bash
cd backend
python test_social_auth.py
```

### **Test manuel**
1. Configurez vos clés OAuth2
2. Démarrez le serveur backend et frontend
3. Testez la connexion avec Google/Facebook
4. Vérifiez la création des comptes

## 🚨 Dépannage

### **Erreurs courantes**

1. **"Client ID invalide"**
   - Vérifiez vos clés OAuth2
   - Vérifiez les URIs de redirection

2. **"URI de redirection non autorisé"**
   - Ajoutez l'URI dans la console Google/Facebook
   - Vérifiez qu'il n'y a pas d'espaces

3. **"Erreur de réseau"**
   - Vérifiez votre connexion internet
   - Vérifiez que les APIs sont activées

### **Logs de débogage**
Activez les logs détaillés dans `.env` :
```env
DEBUG=True
SOCIAL_AUTH_DEBUG=True
```

## 📚 Ressources

### **Documentation officielle**
- [Google OAuth2](https://developers.google.com/identity/protocols/oauth2)
- [Facebook OAuth2](https://developers.facebook.com/docs/facebook-login)

### **Console de développement**
- [Google Cloud Console](https://console.cloud.google.com/)
- [Facebook Developers](https://developers.facebook.com/)

## 🌐 Déploiement

### **Production**
1. Mettez à jour les URIs de redirection vers HTTPS
2. Configurez les variables d'environnement
3. Activez HTTPS sur votre serveur
4. Testez avec des comptes de production

### **Variables d'environnement**
```env
GOOGLE_REDIRECT_URI=https://votre-domaine.com/auth/google/callback
FACEBOOK_REDIRECT_URI=https://votre-domaine.com/auth/facebook/callback
```

## 🎉 Félicitations !

Votre système d'authentification sociale est maintenant **entièrement fonctionnel** ! 

### **Prochaines étapes suggérées**
1. ✅ Testez avec vos comptes Google/Facebook
2. ✅ Personnalisez les messages et l'interface
3. ✅ Ajoutez d'autres providers (GitHub, Twitter, etc.)
4. ✅ Implémentez la gestion des avatars de profil
5. ✅ Ajoutez la possibilité de lier/délier des comptes sociaux

---

**🔐 L'authentification sociale est prête à être utilisée !**





