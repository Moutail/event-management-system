# Diagnostic - Problème d'Export CSV/Excel

## Problème Signalé
L'utilisateur ne peut pas exporter les données des inscriptions aux événements en CSV ou Excel.

## Vérifications Effectuées

### 1. ✅ Backend - Fonctions d'Export
- **Fonction CSV** : `super_admin_export_registrations_csv` ✅ Présente
- **Fonction Excel** : `super_admin_export_registrations_excel` ✅ Présente
- **Imports** : `csv`, `HttpResponse`, `Workbook` ✅ Présents
- **Permissions** : `@permission_classes([IsAuthenticated, IsSuperAdmin])` ✅ Configurées

### 2. ✅ Backend - URLs
- **Route CSV** : `/admin/events/{id}/export_csv/` ✅ Configurée
- **Route Excel** : `/admin/events/{id}/export_excel/` ✅ Configurée
- **Imports** : Fonctions correctement importées ✅

### 3. ✅ Frontend - Interface
- **Boutons CSV** : Présent dans EventDetailModal ✅
- **Boutons Excel** : Présent dans EventDetailModal ✅
- **Fonctions** : `handleExportCSV` et `handleExportExcel` ✅ Présentes

## Tests à Effectuer

### 1. Test de l'API Backend
```bash
# Test sans authentification (doit retourner 401)
curl -X GET "http://localhost:8000/api/admin/events/1/export_csv/"

# Test avec token valide (doit retourner le fichier ou une erreur logique)
curl -X GET "http://localhost:8000/api/admin/events/1/export_csv/" \
  -H "Authorization: Bearer TOKEN_VALIDE"
```

### 2. Test de l'Interface Frontend
1. Se connecter en tant que super admin
2. Ouvrir les détails d'un événement
3. Vérifier que les boutons CSV et Excel sont visibles
4. Cliquer sur CSV - vérifier la console pour les erreurs
5. Cliquer sur Excel - vérifier la console pour les erreurs

### 3. Vérification des Erreurs Console
Ouvrir la console du navigateur et vérifier :
- Erreurs JavaScript
- Erreurs de réseau (Network tab)
- Messages d'erreur spécifiques

## Causes Possibles

### 1. Problème d'Authentification
- **Symptôme** : Erreur 401 Unauthorized
- **Cause** : Token expiré ou invalide
- **Solution** : Se reconnecter

### 2. Problème de Permissions
- **Symptôme** : Erreur 403 Forbidden
- **Cause** : Utilisateur non super admin
- **Solution** : Vérifier le rôle de l'utilisateur

### 3. Problème de Données
- **Symptôme** : Erreur 404 Not Found
- **Cause** : Événement inexistant
- **Solution** : Vérifier l'ID de l'événement

### 4. Problème Frontend
- **Symptôme** : Erreur JavaScript
- **Cause** : Problème dans le code frontend
- **Solution** : Vérifier la console

## Étapes de Diagnostic

### Étape 1 : Vérifier l'Authentification
1. Se déconnecter et se reconnecter
2. Vérifier que le token est valide
3. Vérifier que l'utilisateur est super admin

### Étape 2 : Tester l'API Directement
1. Utiliser un outil comme Postman ou curl
2. Tester avec un token valide
3. Vérifier la réponse de l'API

### Étape 3 : Vérifier les Logs Backend
1. Regarder les logs du serveur Django
2. Vérifier s'il y a des erreurs 500
3. Vérifier les exceptions Python

### Étape 4 : Vérifier la Console Frontend
1. Ouvrir les outils de développement
2. Aller dans l'onglet Console
3. Reproduire l'erreur et noter les messages

## Solutions

### Si Problème d'Authentification
```javascript
// Vérifier que l'utilisateur est connecté
console.log('Token:', localStorage.getItem('token'));
console.log('User:', localStorage.getItem('user'));
```

### Si Problème de Permissions
```python
# Vérifier le rôle de l'utilisateur
user = request.user
profile = user.profile
print(f"User: {user.username}, Role: {profile.role}")
```

### Si Problème de Données
```python
# Vérifier que l'événement existe
try:
    event = Event.objects.get(id=event_id)
    print(f"Event found: {event.title}")
except Event.DoesNotExist:
    print(f"Event {event_id} not found")
```

## Test Rapide

Pour tester rapidement, créer un événement de test :
1. Créer un événement simple
2. S'inscrire avec un utilisateur
3. Tester l'export avec cet événement

## Conclusion

L'infrastructure d'export est correctement configurée. Le problème vient probablement de :
- L'authentification (token expiré)
- Les permissions (utilisateur non super admin)
- Une erreur dans les données (événement inexistant)

Suivre les étapes de diagnostic pour identifier la cause exacte.
