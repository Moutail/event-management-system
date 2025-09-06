# 🚨 GUIDE DE DEBUG - SYSTÈME DE SESSIONS MULTIPLES

## 🎯 **OBJECTIF**
Identifier **EXACTEMENT** où le système de sessions échoue et pourquoi les utilisateurs voient les données des autres.

## 🔍 **OUTILS DE DEBUG CRÉÉS**

### 1️⃣ **Logs détaillés dans la console**
- ✅ `authSlice.js` : Logs pour login/logout/refresh/getCurrentUser
- ✅ `api.js` : Logs pour intercepteurs et gestion des tokens
- ✅ `App.js` : Logs pour initialisation de l'authentification
- ✅ `SessionTester.js` : Logs pour chaque action de test

### 2️⃣ **Page de debug HTML**
- ✅ `test_localStorage_debug.html` : Test direct du localStorage
- ✅ Création/suppression de sessions de test
- ✅ Changement de session active
- ✅ Affichage en temps réel du localStorage

## 🚀 **ÉTAPES DE DEBUG**

### **ÉTAPE 1 : Démarrer l'application avec logs**
```bash
cd frontend
npm start
```

### **ÉTAPE 2 : Ouvrir la console (F12)**
- Aller sur `http://localhost:3000`
- Ouvrir la console du navigateur
- **REGARDER** tous les logs qui commencent par 🔍, ✅, ❌, 🚀

### **ÉTAPE 3 : Tester le localStorage directement**
- Ouvrir `frontend/test_localStorage_debug.html` dans un nouvel onglet
- Créer plusieurs sessions de test
- Vérifier que chaque session est isolée

### **ÉTAPE 4 : Tester l'application React**
- Aller sur `http://localhost:3000/test-sessions`
- Utiliser les boutons de test
- **REGARDER** la console pour chaque action

## 🔍 **CE QU'IL FAUT CHERCHER**

### **❌ PROBLÈMES POSSIBLES**

#### **1. Problème d'initialisation**
```
🚀 [AUTH_SLICE] Initialisation avec sessionData: AUCUNE
❌ [AUTH_SLICE] Aucun current_session_id trouvé
```
**→ Solution** : Vérifier que `getCurrentSessionData()` fonctionne

#### **2. Problème de sauvegarde**
```
🔐 [AUTH_SLICE] LOGIN démarré pour: userA
✅ [AUTH_SLICE] Réponse API login reçue
❌ [AUTH_SLICE] Erreur lors de la sauvegarde
```
**→ Solution** : Vérifier que `localStorage.setItem` fonctionne

#### **3. Problème de récupération**
```
🔍 [API] getCurrentSessionToken() appelé
❌ [API] Aucune sessionData trouvée pour: session_123
```
**→ Solution** : Vérifier que la session existe dans localStorage

#### **4. Problème de sessionId**
```
🆔 [AUTH_SLICE] Nouveau sessionId généré: session_123
❌ [AUTH_SLICE] SessionId null dans le state
```
**→ Solution** : Vérifier que le sessionId est bien passé au state Redux

### **✅ CE QUI DOIT MARCHER**

#### **1. Initialisation correcte**
```
🚀 [AUTH_SLICE] Initialisation avec sessionData: {
  sessionId: "session_123",
  user: "userA",
  role: "participant"
}
```

#### **2. Sauvegarde correcte**
```
💾 [AUTH_SLICE] Sauvegarde session dans localStorage: {
  key: "auth_session_session_123",
  user: "userA"
}
✅ [AUTH_SLICE] Session sauvegardée avec succès
```

#### **3. Récupération correcte**
```
🔍 [API] Token récupéré pour session: {
  sessionId: "session_123",
  user: "userA",
  hasAccessToken: true
}
```

## 🧪 **TESTS CRITIQUES À FAIRE**

### **TEST 1 : Session unique**
1. Se connecter avec User A
2. Vérifier dans la console :
   - ✅ Session créée avec sessionId unique
   - ✅ localStorage contient `auth_session_${sessionId}`
   - ✅ `current_session_id` pointe vers la bonne session

### **TEST 2 : Sessions multiples**
1. **Onglet 1** : Connecter User A
2. **Onglet 2** : Connecter User B
3. **Vérifier** que chaque onglet a sa propre session
4. **Actualiser** chaque onglet
5. **Vérifier** qu'il n'y a pas de mélange

### **TEST 3 : Isolation des données**
1. Créer 3 sessions différentes
2. Changer de session active
3. Vérifier que `getCurrentSessionToken()` retourne le bon token
4. Vérifier que l'API utilise le bon token

## 🚨 **SIGNES D'ALERTE**

### **⚠️ Si vous voyez :**
```
❌ [AUTH_SLICE] Aucun current_session_id trouvé
❌ [API] Aucune sessionData trouvée
❌ [AUTH_SLICE] Session expirée
```

### **🚨 Si vous voyez :**
```
🔄 [API] Tentative de refresh token pour: /auth/user/
❌ [API] Erreur refresh token
🗑️ [API] Suppression session après échec refresh
```

### **💥 Si vous voyez :**
```
❌ [AUTH_SLICE] Erreur parsing session
❌ [API] Erreur parsing sessionData
```

## 🔧 **SOLUTIONS RAPIDES**

### **1. Vérifier localStorage**
```javascript
// Dans la console du navigateur
console.log('localStorage:', localStorage);
console.log('current_session_id:', localStorage.getItem('current_session_id'));
```

### **2. Vérifier les sessions**
```javascript
// Lister toutes les sessions
Object.keys(localStorage).filter(key => key.startsWith('auth_session_'))
```

### **3. Nettoyer et recommencer**
```javascript
// Supprimer toutes les sessions
Object.keys(localStorage).forEach(key => {
  if (key.startsWith('auth_session_') || key === 'current_session_id') {
    localStorage.removeItem(key);
  }
});
```

## 📞 **EN CAS DE PROBLÈME**

### **1. Copier TOUS les logs de la console**
- Depuis le démarrage de l'application
- Pour chaque action de test
- Inclure les erreurs en rouge

### **2. Décrire le comportement observé**
- Que se passe-t-il exactement ?
- À quel moment le problème survient ?
- Quels utilisateurs sont affectés ?

### **3. Tester avec l'outil HTML**
- Utiliser `test_localStorage_debug.html`
- Vérifier que le localStorage fonctionne
- Tester la création de sessions

## 🎯 **RÉSULTAT ATTENDU**

**CHAQUE UTILISATEUR DOIT AVOIR :**
- ✅ Son propre `sessionId` unique
- ✅ Ses propres données dans `auth_session_${sessionId}`
- ✅ Son propre `current_session_id`
- ✅ Aucun accès aux sessions des autres

**LA CONSOLE DOIT MONTRER :**
- ✅ Logs de création de session
- ✅ Logs de sauvegarde réussie
- ✅ Logs de récupération correcte
- ✅ Aucune erreur de parsing ou de session

---

## 🚀 **COMMENCER LE DEBUG MAINTENANT !**

1. **Démarrer l'application** : `npm start`
2. **Ouvrir la console** : F12
3. **Aller sur** `/test-sessions`
4. **Tester étape par étape**
5. **Copier tous les logs** en cas de problème

**ON VA IDENTIFIER LE PROBLÈME !** 🔍💪















