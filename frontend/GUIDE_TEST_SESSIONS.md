# Guide de Test - Types de Sessions 🎯

## 🎯 **Objectif**
Vérifier que les types de sessions fonctionnent correctement dans le système d'événements.

## ✅ **Fonctionnalités à Tester**

### 1. **Affichage des Sessions dans le Modal d'Inscription**
- [ ] **Problème identifié** : Seulement une session s'affiche au lieu de deux
- [ ] **Solution appliquée** : Ajout de logs de debug pour identifier le problème
- [ ] **Vérification** : Ouvrir la console et vérifier les logs de debug

### 2. **Affichage de la Session dans la Liste des Participants**
- [ ] **Problème identifié** : La session n'est pas visible dans la liste des participants
- [ ] **Solution appliquée** : Ajout du champ `session_type_name` dans le serializer
- [ ] **Vérification** : La session doit apparaître dans l'affichage des participants

## 🔍 **Tests à Effectuer**

### **Test 1 : Debug des Sessions**
1. **Ouvrir le navigateur** et aller sur la page d'un événement
2. **Cliquer sur "S'inscrire"** pour ouvrir le modal d'inscription
3. **Ouvrir la console** (F12 → Console)
4. **Vérifier les logs de debug** :
   ```
   🔍 DEBUG: Sessions récupérées: [...]
   🔍 DEBUG: Nombre de sessions: X
   🔍 DEBUG: Affichage des sessions - Total: X
   🔍 DEBUG: Sessions actives: X
   🔍 DEBUG: Sessions triées: [...]
   ```

### **Test 2 : Affichage des Sessions**
1. **Dans le modal d'inscription**, vérifier le dropdown "Type de session *"
2. **Vérifier que toutes les sessions créées s'affichent** (pas seulement une)
3. **Vérifier que les sessions sont triées** par ordre d'affichage
4. **Vérifier que les sessions complètes sont désactivées**

### **Test 3 : Affichage des Participants avec Session**
1. **Aller dans les détails de l'événement** (si organisateur/super-admin)
2. **Vérifier la section "Participants"**
3. **Vérifier que la session est affichée** pour chaque participant :
   ```
   email@example.com • Type de billet • Prix • Session: Nom de la session
   ```

## 🚨 **Problèmes Identifiés et Solutions**

### **Problème 1 : Une seule session s'affiche**
- **Cause possible** : Filtrage incorrect des sessions actives
- **Solution** : Ajout de logs de debug pour identifier le problème
- **Vérification** : Consulter les logs dans la console

### **Problème 2 : Session non visible dans la liste des participants**
- **Cause** : Champ `session_type_name` manquant dans le serializer
- **Solution** : Ajout du champ dans `EventRegistrationSerializer`
- **Vérification** : La session doit apparaître dans l'affichage des participants

## 📋 **Checklist de Vérification**

### **Frontend - Modal d'Inscription**
- [ ] Section "Type de session *" visible si des sessions existent
- [ ] Toutes les sessions créées s'affichent dans le dropdown
- [ ] Sessions triées par ordre d'affichage
- [ ] Sessions complètes désactivées
- [ ] Validation obligatoire si sessions existent

### **Frontend - Liste des Participants**
- [ ] Section "Participants" visible pour les organisateurs
- [ ] Session affichée pour chaque participant inscrit
- [ ] Format : `email • billet • prix • Session: nom_session`

### **Backend - API**
- [ ] Endpoint `/events/{id}/session_types/` fonctionne
- [ ] Serializer `EventRegistrationSerializer` inclut `session_type_name`
- [ ] Données des sessions correctement récupérées

## 🎯 **Résultat Attendu**

1. **✅ Toutes les sessions créées s'affichent** dans le modal d'inscription
2. **✅ La session est visible** dans la liste des participants
3. **✅ Le système de validation** fonctionne correctement
4. **✅ L'intégration avec le paiement** inclut le `session_type_id`

## 🔧 **En Cas de Problème**

### **Si les sessions ne s'affichent toujours pas :**
1. Vérifier les logs de debug dans la console
2. Vérifier que l'API retourne bien les données
3. Vérifier que les sessions sont marquées comme `is_active: true`

### **Si la session n'apparaît pas dans la liste des participants :**
1. Vérifier que le serializer inclut bien `session_type_name`
2. Vérifier que l'inscription a bien été créée avec un `session_type_id`
3. Vérifier que la vue backend inclut bien les données de session

---

**🎉 Une fois tous les tests passés, le système de types de sessions sera entièrement fonctionnel !**




