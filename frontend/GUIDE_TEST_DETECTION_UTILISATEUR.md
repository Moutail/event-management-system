# 🔍 GUIDE DE TEST - DÉTECTION UTILISATEUR CHATBOT

## 🎯 PROBLÈME IDENTIFIÉ ET RÉSOLU

### **❌ Problème Initial**
Le chatbot utilisait `localStorage.getItem('user_type')` qui n'existait pas, donc il ne reconnaissait jamais qui était connecté.

### **✅ Solution Implémentée**
- **Intégration Redux** : Le chatbot utilise maintenant `useSelector` pour accéder à l'état d'authentification
- **Détection automatique** : Le type d'utilisateur est détecté automatiquement depuis le profil Redux
- **Mise à jour en temps réel** : Les suggestions se mettent à jour quand l'utilisateur change

---

## 🧪 COMMENT TESTER LA DÉTECTION

### **Étape 1 : Démarrer l'Application**
```bash
cd frontend
npm start
```

### **Étape 2 : Tester avec Différents Types d'Utilisateurs**

#### **👤 Test Participant (Utilisateur Normal)**
1. Connectez-vous avec un compte participant
2. Ouvrez le chatbot
3. **Vérifiez** : Le header affiche "👤 participant | Connecté"
4. **Vérifiez** : Les suggestions sont adaptées aux participants

#### **🎯 Test Organisateur**
1. Connectez-vous avec un compte organisateur
2. Ouvrez le chatbot
3. **Vérifiez** : Le header affiche "👤 organizer | Connecté"
4. **Vérifiez** : Les suggestions incluent "Créer un événement", "Configurer le streaming"

#### **👑 Test Super Admin**
1. Connectez-vous avec un compte super admin
2. Ouvrez le chatbot
3. **Vérifiez** : Le header affiche "👤 super_admin | Connecté"
4. **Vérifiez** : Les suggestions incluent "Gérer tous les événements", "Modérer les utilisateurs"

#### **🚫 Test Non Connecté**
1. Déconnectez-vous
2. Ouvrez le chatbot
3. **Vérifiez** : Le header affiche "👤 participant | Non connecté"
4. **Vérifiez** : Les suggestions sont celles par défaut

---

## 🔍 INDICATEURS VISUELS DE DEBUG

### **En Mode Développement**
Le header du chatbot affiche :
```
👤 [type_utilisateur] | [statut_connexion]
```

### **Exemples d'Affichage**
- `👤 participant | Connecté`
- `👤 organizer | Connecté`
- `👤 super_admin | Connecté`
- `👤 participant | Non connecté`

---

## 📊 LOGS DE DEBUG DANS LA CONSOLE

### **Ouvrez la Console (F12) et regardez :**

#### **Au Chargement du Chatbot**
```
🎯 Type utilisateur détecté depuis Redux: [type]
👤 Détails utilisateur: {id, username, is_superuser, is_staff, profile_role}
```

#### **Exemples de Logs**
```
🎯 Type utilisateur détecté depuis Redux: super_admin
👤 Détails utilisateur: {
  id: 1,
  username: "admin",
  is_superuser: true,
  is_staff: true,
  profile_role: "super_admin"
}
```

---

## 🎯 TESTS DES RÉPONSES PERSONNALISÉES

### **Test 1 : Salutations Personnalisées**
| Type Utilisateur | Message Attendu |
|------------------|-----------------|
| **Super Admin** | "Bonjour Super Admin ! 👑 Je suis votre assistant IA pour la gestion globale..." |
| **Organisateur** | "Bonjour Organisateur ! 🎯 Je suis votre assistant IA pour la création..." |
| **Participant** | "Bonjour ! 👤 Je suis votre assistant IA pour vous aider..." |

### **Test 2 : Suggestions Adaptées**
| Type Utilisateur | Suggestions Visibles |
|------------------|---------------------|
| **Super Admin** | Gérer tous les événements, Statistiques globales, Modérer les utilisateurs |
| **Organisateur** | Créer un événement, Configurer le streaming, Voir mes événements |
| **Participant** | Comment s'inscrire, Événements gratuits, Rejoindre un stream |

---

## 🐛 DÉPANNAGE

### **Le chatbot affiche toujours "participant" ?**

#### **Vérifiez la Console :**
1. Ouvrez F12 → Console
2. Regardez les logs de détection
3. Vérifiez que `user` et `isAuthenticated` sont bien définis

#### **Vérifiez Redux :**
1. Ouvrez F12 → Redux DevTools
2. Regardez l'état `auth.user`
3. Vérifiez que `user.profile.role` existe

#### **Vérifiez la Connexion :**
1. Assurez-vous d'être connecté
2. Vérifiez que le token est valide
3. Regardez si `getCurrentUser` a été appelé

### **Les suggestions ne se mettent pas à jour ?**

#### **Vérifiez les Dépendances :**
```javascript
useEffect(() => {
  if (isOpen) {
    loadSuggestions();
  }
}, [user, isAuthenticated, isOpen]); // Ces dépendances doivent changer
```

#### **Forcez la Mise à Jour :**
1. Fermez et rouvrez le chatbot
2. Changez de page puis revenez
3. Vérifiez que `loadSuggestions()` est appelé

---

## 🎉 SUCCÈS ATTENDU

### **✅ Détection Fonctionnelle**
- Le type d'utilisateur est correctement détecté
- Les suggestions s'adaptent au rôle
- Les réponses sont personnalisées
- La mise à jour se fait en temps réel

### **✅ Logs de Debug**
- Console affiche les détails de détection
- Header affiche le type d'utilisateur (en dev)
- Pas d'erreurs dans la console

### **✅ Personnalisation**
- Message d'accueil adapté au rôle
- Suggestions contextuelles
- Réponses IA personnalisées

---

## 📝 NOTES TECHNIQUES

### **Structure de Détection**
```javascript
const getUserType = () => {
  if (!isAuthenticated || !user) return 'participant';
  
  if (user.is_superuser) return 'super_admin';
  if (user.profile?.role) return user.profile.role;
  if (user.is_staff) return 'organizer';
  
  return 'participant';
};
```

### **Dépendances Redux**
- `user` : Données de l'utilisateur connecté
- `isAuthenticated` : Statut de connexion
- `user.profile.role` : Rôle depuis le profil

### **Mise à Jour Automatique**
- `useEffect` se déclenche quand `user` ou `isAuthenticated` change
- `loadSuggestions()` recharge les suggestions
- Interface se met à jour en temps réel

---

*Guide généré le : ${new Date().toLocaleDateString('fr-FR')}*
*Statut : ✅ PROBLÈME RÉSOLU*

