# Guide de Test Rapide - Export CSV/Excel

## 🚨 Problème Signalé
L'export CSV et Excel ne fonctionne pas dans l'interface super admin.

## 🔧 Solution Immédiate

### 1. Utiliser le Composant de Test
1. **Aller dans le dashboard super admin**
2. **Cliquer sur l'onglet "Test Export"** (dernier onglet)
3. **Cliquer sur "Tester l'Authentification"** pour vérifier votre statut
4. **Entrer l'ID d'un événement existant** (ex: 1, 2, 3...)
5. **Tester l'export CSV et Excel**

### 2. Vérifier la Console
- **Ouvrir les outils de développement** (F12)
- **Aller dans l'onglet Console**
- **Reproduire l'erreur** et noter les messages

## 🔍 Diagnostic Automatique

Le composant de test va automatiquement :
- ✅ Vérifier votre authentification
- ✅ Tester les permissions
- ✅ Identifier le type d'erreur
- ✅ Afficher des messages d'erreur clairs

## 📋 Messages d'Erreur Possibles

### Erreur 401 - Authentification
```
Erreur d'authentification. Veuillez vous reconnecter.
```
**Solution** : Se déconnecter et se reconnecter

### Erreur 403 - Permissions
```
Accès refusé. Vérifiez vos permissions.
```
**Solution** : Vérifier que vous êtes super admin

### Erreur 404 - Événement
```
Événement non trouvé. Vérifiez l'ID.
```
**Solution** : Utiliser un ID d'événement valide

### Erreur 500 - Serveur
```
Erreur serveur. Vérifiez les logs backend.
```
**Solution** : Contacter l'administrateur système

## 🧪 Test Pas à Pas

### Étape 1 : Vérifier l'Authentification
1. Cliquer sur "Tester l'Authentification"
2. **Résultat attendu** : Message de succès avec votre nom et rôle
3. **Si erreur** : Se reconnecter

### Étape 2 : Tester l'Export
1. Entrer l'ID d'un événement (ex: 1)
2. Cliquer sur "Test Export CSV"
3. Cliquer sur "Test Export Excel"
4. **Résultat attendu** : Fichier téléchargé

### Étape 3 : Vérifier les Erreurs
1. Ouvrir la console (F12)
2. Reproduire l'erreur
3. Noter les messages d'erreur
4. Suivre les instructions affichées

## 🎯 Points de Vérification

### ✅ Authentification
- [ ] Être connecté
- [ ] Avoir un token valide
- [ ] Être super admin

### ✅ Données
- [ ] Événement existe
- [ ] Événement a des inscriptions
- [ ] ID d'événement correct

### ✅ Backend
- [ ] Serveur fonctionne
- [ ] API accessible
- [ ] Pas d'erreurs 500

## 🚀 Si Tout Fonctionne

Si les tests d'export fonctionnent dans l'onglet "Test Export" mais pas dans l'interface normale :

1. **Vérifier l'interface EventDetailModal**
2. **Contrôler que les boutons d'export sont visibles**
3. **Vérifier qu'il n'y a pas d'erreurs JavaScript**

## 📞 Support

Si le problème persiste après ces tests :
1. **Noter tous les messages d'erreur**
2. **Vérifier la console du navigateur**
3. **Contacter l'équipe technique avec les détails**

## 🎉 Résolution

Une fois le problème identifié et résolu :
- ✅ Export CSV fonctionnel
- ✅ Export Excel fonctionnel
- ✅ Interface utilisateur opérationnelle
- ✅ Données correctement exportées
