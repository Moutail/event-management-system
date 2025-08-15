# Guide de Test - Suppression d'Événements par l'Admin

## Problème Résolu

L'erreur de suppression d'événements était causée par l'utilisation incorrecte de l'endpoint `/admin/moderate_event/` pour l'action `'delete'`. Cet endpoint ne gère que les actions de modération (`'approve'`, `'suspend'`, `'reject'`, `'publish'`).

## Solution Implémentée

Le composant `EventManagement.js` a été corrigé pour :
1. **Utiliser l'endpoint dédié** `/admin/events/{id}/delete/` pour la suppression
2. **Continuer à utiliser** `/admin/moderate_event/` pour les autres actions

## Code Corrigé

```javascript
const confirmAction = async () => {
  try {
    let response;
    
    if (actionType === 'delete') {
      // Pour la suppression, utiliser l'endpoint dédié
      response = await api.delete(`/admin/events/${selectedEvent.id}/delete/`);
    } else {
      // Pour les autres actions (approve, suspend, reject), utiliser moderate_event
      const payload = {
        event_id: selectedEvent.id,
        action: actionType
      };
      response = await api.post('/admin/moderate_event/', payload);
    }
    
    showSnackbar('Action effectuée avec succès', 'success');
    setActionDialog(false);
    setSelectedEvent(null);
    setActionType('');
    loadEvents(); // Recharger les données
  } catch (error) {
    console.error('Erreur lors de l\'action:', error);
    showSnackbar('Erreur lors de l\'action', 'error');
  }
};
```

## Endpoints Utilisés

### Suppression d'Événements
- **URL** : `DELETE /api/admin/events/{id}/delete/`
- **Permissions** : Super Admin uniquement
- **Fonction** : `super_admin_delete_event` dans `backend/events/views.py`

### Modération d'Événements
- **URL** : `POST /api/admin/moderate_event/`
- **Permissions** : Super Admin uniquement
- **Actions supportées** : `approve`, `suspend`, `reject`, `publish`

## Test de la Correction

### 1. Test via l'Interface Admin
1. Se connecter en tant que Super Admin
2. Aller dans l'onglet "Événements"
3. Cliquer sur l'icône de suppression (🗑️) d'un événement
4. Confirmer la suppression dans le dialogue
5. Vérifier que l'événement disparaît de la liste

### 2. Test Direct de l'API
```bash
# Test sans authentification (doit retourner 401)
curl -X DELETE http://localhost:8000/api/admin/events/1/delete/

# Test avec authentification (doit fonctionner)
curl -X DELETE \
  -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/admin/events/1/delete/
```

### 3. Vérification des Logs
- Vérifier que l'action est enregistrée dans `EventHistory`
- Vérifier que l'événement est bien supprimé de la base de données

## Fonctionnalités Disponibles

### Actions sur les Événements
- ✅ **Voir les détails** : Modal avec informations complètes
- ✅ **Approuver** : Changer le statut de `draft` à `published`
- ✅ **Suspendre** : Changer le statut de `published` à `draft`
- ✅ **Supprimer** : Suppression définitive de l'événement
- ✅ **Filtrage** : Par statut, catégorie, recherche textuelle
- ✅ **Pagination** : Navigation entre les pages d'événements

### Sécurité
- Toutes les actions nécessitent l'authentification Super Admin
- Confirmation requise pour les actions destructives
- Historique des actions conservé dans `EventHistory`

## Maintenance

### Vérification des Endpoints
```bash
# Lister tous les endpoints admin
python manage.py show_urls | grep admin
```

### Logs et Monitoring
- Surveiller les erreurs 500 dans les logs Django
- Vérifier les tentatives d'accès non autorisées
- Monitorer les suppressions d'événements

## Évolutions Futures

1. **Soft Delete** : Option pour archiver au lieu de supprimer
2. **Bulk Actions** : Suppression multiple d'événements
3. **Notifications** : Informer les participants des suppressions
4. **Audit Trail** : Historique détaillé des modifications
