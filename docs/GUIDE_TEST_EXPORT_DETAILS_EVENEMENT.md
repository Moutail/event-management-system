# Guide de Test - Export dans les Détails d'Événement

## 🚨 Problème Signalé
L'export CSV/Excel fonctionne dans le composant de test mais pas dans l'interface des détails d'événement.

## 🔍 Diagnostic du Problème

### 1. Vérifier la Console du Navigateur
1. **Ouvrir les outils de développement** (F12)
2. **Aller dans l'onglet Console**
3. **Ouvrir les détails d'un événement**
4. **Cliquer sur les boutons CSV ou Excel**
5. **Noter tous les messages** (erreurs, logs, etc.)

### 2. Messages de Debug Ajoutés
Les fonctions d'export affichent maintenant des messages détaillés :

#### ✅ Messages de Succès
```
🔍 Début export CSV pour événement: [ID]
✅ Export CSV réussi: [Réponse]
📁 Fichier CSV téléchargé avec succès
```

#### ❌ Messages d'Erreur
```
❌ Erreur lors de l'export CSV: [Erreur]
📊 Réponse erreur CSV: Status [Code] [Détails]
```

## 🧪 Tests à Effectuer

### Test 1 : Vérifier la Visibilité des Boutons
1. **Ouvrir les détails d'un événement**
2. **Aller à la section "Statistiques des Inscriptions"**
3. **Vérifier que les boutons CSV et Excel sont visibles**
4. **Vérifier qu'ils ne sont pas désactivés**

### Test 2 : Tester l'Export CSV
1. **Cliquer sur le bouton "CSV"**
2. **Vérifier la console pour les messages**
3. **Vérifier si un fichier est téléchargé**
4. **Noter toute erreur affichée**

### Test 3 : Tester l'Export Excel
1. **Cliquer sur le bouton "Excel"**
2. **Vérifier la console pour les messages**
3. **Vérifier si un fichier est téléchargé**
4. **Noter toute erreur affichée**

### Test 4 : Vérifier l'État de Chargement
1. **Cliquer sur un bouton d'export**
2. **Vérifier que le bouton affiche "Export..."**
3. **Vérifier que les boutons sont désactivés pendant l'export**
4. **Attendre la fin de l'export**

## 📋 Erreurs Possibles et Solutions

### Erreur 401 - Authentification
```
Erreur d'authentification. Veuillez vous reconnecter.
```
**Cause** : Token expiré ou invalide
**Solution** : Se déconnecter et se reconnecter

### Erreur 403 - Permissions
```
Accès refusé. Vérifiez vos permissions.
```
**Cause** : Utilisateur non super admin
**Solution** : Vérifier le rôle de l'utilisateur

### Erreur 404 - Événement
```
Événement non trouvé. Vérifiez l'ID.
```
**Cause** : ID d'événement invalide
**Solution** : Utiliser un événement valide

### Erreur 500 - Serveur
```
Erreur serveur. Vérifiez les logs backend.
```
**Cause** : Problème côté serveur
**Solution** : Contacter l'administrateur

### Erreur JavaScript
```
TypeError: Cannot read property '...' of undefined
```
**Cause** : Variable non définie
**Solution** : Vérifier la structure des données

## 🔧 Vérifications Techniques

### 1. Vérifier l'API
```javascript
// Dans la console, tester manuellement
fetch('/api/admin/events/1/export_csv/', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
}).then(r => console.log(r.status, r))
```

### 2. Vérifier l'Authentification
```javascript
// Dans la console
console.log('Token:', localStorage.getItem('token'));
console.log('User:', localStorage.getItem('user'));
```

### 3. Vérifier les Données de l'Événement
```javascript
// Dans la console
console.log('Event Details:', eventDetails);
console.log('Event ID:', eventId);
```

## 🎯 Points de Vérification

### ✅ Interface
- [ ] Boutons CSV et Excel visibles
- [ ] Boutons non désactivés
- [ ] Section "Statistiques des Inscriptions" affichée

### ✅ Fonctionnalité
- [ ] Clic sur CSV déclenche l'export
- [ ] Clic sur Excel déclenche l'export
- [ ] Messages de debug dans la console
- [ ] Gestion des erreurs appropriée

### ✅ Données
- [ ] Événement chargé correctement
- [ ] ID d'événement valide
- [ ] Statistiques d'inscription disponibles

## 🚀 Si le Problème Persiste

### 1. Comparer avec le Composant de Test
- Le composant de test fonctionne
- L'interface des détails ne fonctionne pas
- **Différence** : Contexte d'utilisation

### 2. Vérifier les Différences
- **Permissions** : Même utilisateur ?
- **Contexte** : Même événement ?
- **État** : Même données chargées ?

### 3. Test de Contournement
- Utiliser le composant de test pour l'export
- Noter les différences de comportement
- Identifier la cause exacte

## 📞 Support Technique

### Informations à Fournir
1. **Messages de la console** (copier-coller)
2. **ID de l'événement** testé
3. **Rôle de l'utilisateur** connecté
4. **Actions effectuées** (étapes détaillées)
5. **Résultat attendu** vs **résultat obtenu**

### Logs Utiles
- Console du navigateur
- Réseau (Network tab)
- Erreurs JavaScript
- Réponses API

## 🎉 Résolution Attendue

Une fois le problème identifié et résolu :
- ✅ Boutons d'export visibles et fonctionnels
- ✅ Export CSV et Excel opérationnels
- ✅ Messages de debug informatifs
- ✅ Gestion d'erreur appropriée
- ✅ Téléchargement des fichiers réussi

## 🔍 Prochaines Étapes

1. **Suivre ce guide de test**
2. **Noter tous les messages de debug**
3. **Identifier le type d'erreur**
4. **Appliquer la solution appropriée**
5. **Vérifier que l'export fonctionne**
