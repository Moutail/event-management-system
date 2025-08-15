# Guide de Test - Modération d'Événements

## Vue d'ensemble

Ce guide explique comment tester le système de modération d'événements pour les super administrateurs. Le système permet d'approuver, suspendre, rejeter et supprimer des événements.

## Prérequis

1. **Serveur backend démarré** : `python manage.py runserver`
2. **Frontend démarré** : `npm start`
3. **Compte super admin** : Connecté avec les permissions appropriées
4. **Événements de test** : Au moins un événement en statut "draft" dans la base de données

## Test de l'Interface de Modération

### 1. Accès au Dashboard Super Admin

1. Connectez-vous avec un compte super admin
2. Naviguez vers le dashboard super admin
3. Sélectionnez l'onglet "Test Modération"

### 2. Test de Modération d'Événements

#### Test d'Approbation
1. Entrez l'ID d'un événement en statut "draft"
2. Sélectionnez l'action "Approuver"
3. Cliquez sur "Tester la modération"
4. Vérifiez que l'événement passe au statut "published"

#### Test de Suspension
1. Entrez l'ID d'un événement en statut "published"
2. Sélectionnez l'action "Suspendre"
3. Entrez une raison (ex: "Contenu à vérifier")
4. Cliquez sur "Tester la modération"
5. Vérifiez que l'événement passe au statut "draft"

#### Test de Rejet
1. Entrez l'ID d'un événement
2. Sélectionnez l'action "Rejeter"
3. Entrez une raison (ex: "Contenu inapproprié")
4. Cliquez sur "Tester la modération"
5. Vérifiez que l'événement passe au statut "cancelled"

## Test via l'Interface de Gestion des Événements

### 1. Accès à la Gestion des Événements

1. Dans le dashboard super admin, sélectionnez l'onglet "Événements"
2. La liste des événements s'affiche avec leurs statuts actuels

### 2. Actions sur les Événements

#### Approuver un Événement
1. Trouvez un événement avec le statut "Brouillon"
2. Cliquez sur l'icône de validation (✓) verte
3. Confirmez l'action dans le dialog
4. Vérifiez que le statut change à "Publié"

#### Suspendre un Événement
1. Trouvez un événement avec le statut "Publié"
2. Cliquez sur l'icône de suspension (⚠️) orange
3. Confirmez l'action dans le dialog
4. Vérifiez que le statut change à "Brouillon"

#### Supprimer un Événement
1. Trouvez n'importe quel événement
2. Cliquez sur l'icône de suppression (🗑️) rouge
3. Confirmez l'action dans le dialog
4. Vérifiez que l'événement disparaît de la liste

## Test des API Backend

### 1. Test Direct de l'API

#### Endpoint de Modération
```bash
POST /api/admin/moderate_event/
Content-Type: application/json
Authorization: Bearer <token>

{
  "event_id": 123,
  "action": "approve"
}
```

#### Réponse Attendue
```json
{
  "message": "Événement approuvé par username",
  "event_status": "published"
}
```

### 2. Test avec Raison
```bash
POST /api/admin/moderate_event/
Content-Type: application/json
Authorization: Bearer <token>

{
  "event_id": 123,
  "action": "suspend",
  "reason": "Test de suspension"
}
```

## Vérification des Résultats

### 1. Dans l'Interface
- Le statut de l'événement change immédiatement
- Un message de confirmation s'affiche
- La liste des événements se met à jour

### 2. Dans la Base de Données
- Le champ `status` de l'événement est mis à jour
- Une entrée est créée dans `EventHistory`
- Les timestamps sont correctement enregistrés

### 3. Dans les Logs
- Les actions de modération sont tracées
- Les erreurs sont loggées avec détails

## Dépannage

### Erreur 400 - Bad Request
- Vérifiez que `event_id` et `action` sont fournis
- Vérifiez que l'action est valide (approve, suspend, reject)

### Erreur 404 - Not Found
- Vérifiez que l'ID de l'événement existe
- Vérifiez que l'événement n'a pas été supprimé

### Erreur 500 - Internal Server Error
- Vérifiez les logs du serveur Django
- Vérifiez que la base de données est accessible
- Vérifiez que les modèles sont correctement définis

### Problèmes d'Interface
- Vérifiez la console du navigateur pour les erreurs JavaScript
- Vérifiez que l'utilisateur a les permissions super admin
- Vérifiez que l'API backend répond correctement

## Cas de Test Recommandés

### 1. Workflow Complet
1. Créer un événement en brouillon
2. L'approuver (draft → published)
3. Le suspendre (published → draft)
4. L'approuver à nouveau (draft → published)
5. Le rejeter (published → cancelled)

### 2. Test des Permissions
1. Tester avec un compte non-super admin
2. Vérifier que l'accès est refusé
3. Tester avec un compte super admin
4. Vérifier que toutes les actions sont autorisées

### 3. Test des Données
1. Tester avec un ID d'événement invalide
2. Tester avec des actions invalides
3. Tester sans raison pour les actions qui en nécessitent une

## Conclusion

Le système de modération d'événements doit permettre aux super administrateurs de :
- **Approuver** les événements en brouillon
- **Suspendre** les événements publiés
- **Rejeter** les événements avec justification
- **Supprimer** définitivement les événements
- **Suivre** l'historique de toutes les actions

Tous ces tests doivent passer avec succès pour valider le bon fonctionnement du système.
