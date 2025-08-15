# Guide de Test - Modération des Événements

## Vue d'ensemble

Ce guide détaille le système de modération des événements pour les super administrateurs, incluant les fonctionnalités de base et avancées.

## Fonctionnalités de Modération

### 1. Actions de Modération Individuelle
- **Approuver** : Changer le statut de `draft` à `published`
- **Rejeter** : Changer le statut à `cancelled` avec raison
- **Suspendre** : Changer le statut de `published` à `draft` avec raison
- **Publier** : Forcer la publication d'un événement

### 2. Modération en Lot (Bulk Moderation)
- **Sélection multiple** d'événements
- **Action groupée** sur plusieurs événements
- **Rapport détaillé** des résultats

### 3. Historique de Modération
- **Traçabilité complète** de toutes les actions
- **Détails des modifications** (champs, anciennes/nouvelles valeurs)
- **Informations sur l'administrateur** ayant effectué l'action

## Endpoints API

### Modération Individuelle
```
POST /api/admin/moderate_event/
```

**Payload :**
```json
{
  "event_id": 123,
  "action": "approve|reject|suspend|publish",
  "reason": "Raison (requise pour reject/suspend)"
}
```

### Modération en Lot
```
POST /api/admin/bulk_moderate_events/
```

**Payload :**
```json
{
  "event_ids": [123, 124, 125],
  "action": "approve|reject|suspend",
  "reason": "Raison (requise pour reject/suspend)"
}
```

### Historique de Modération
```
GET /api/admin/events/{id}/event_history/
```

## Tests de Fonctionnalités

### 1. Test de Modération Individuelle

#### 1.1 Approuver un Événement
1. **Prérequis** : Événement avec statut `draft`
2. **Action** : Cliquer sur l'icône ✓ (Approuver)
3. **Vérification** :
   - Statut change à `published`
   - Notification de succès
   - Événement visible dans l'onglet "Publiés"

#### 1.2 Rejeter un Événement
1. **Prérequis** : Événement avec statut `draft`
2. **Action** : Cliquer sur l'icône ✗ (Rejeter)
3. **Saisie** : Raison obligatoire
4. **Vérification** :
   - Statut change à `cancelled`
   - Raison enregistrée
   - Événement visible dans l'onglet "Rejetés"

#### 1.3 Suspendre un Événement
1. **Prérequis** : Événement avec statut `published`
2. **Action** : Cliquer sur l'icône ⏸️ (Suspendre)
3. **Saisie** : Raison obligatoire
4. **Vérification** :
   - Statut change à `draft`
   - Raison enregistrée
   - Événement visible dans l'onglet "En Attente"

### 2. Test de Modération en Lot

#### 2.1 Sélection Multiple
1. **Action** : Cocher plusieurs événements
2. **Vérification** : Bouton "Modérer en lot" apparaît

#### 2.2 Action Groupée
1. **Action** : Choisir l'action (Approuver/Rejeter/Suspendre)
2. **Saisie** : Raison si nécessaire
3. **Vérification** :
   - Tous les événements sont modifiés
   - Rapport de résultats affiché
   - Notifications individuelles

### 3. Test de l'Historique

#### 3.1 Consultation de l'Historique
1. **Action** : Cliquer sur l'icône 👁️ (Voir détails)
2. **Navigation** : Onglet "Historique de Modération"
3. **Vérification** :
   - Liste chronologique des actions
   - Détails des modifications
   - Informations sur l'administrateur

#### 3.2 Traçabilité des Actions
1. **Vérification** : Chaque action est enregistrée avec :
   - Type d'action
   - Champ modifié
   - Ancienne et nouvelle valeur
   - Timestamp
   - Administrateur responsable

## Tests d'Interface

### 1. Navigation par Onglets
- **Onglet "En Attente"** : Événements `draft`
- **Onglet "Publiés"** : Événements `published`
- **Onglet "Rejetés"** : Événements `cancelled`
- **Onglet "Tous"** : Tous les événements

### 2. Filtres et Recherche
- **Recherche textuelle** : Titre, lieu, organisateur
- **Filtre par statut** : Sélection du statut
- **Filtre par catégorie** : Sélection de la catégorie

### 3. Pagination
- **Navigation** : Première, précédente, suivante, dernière page
- **Taille de page** : 20 événements par page

## Tests de Sécurité

### 1. Authentification
- **Sans token** : Erreur 401
- **Token invalide** : Erreur 401
- **Token expiré** : Erreur 401

### 2. Permissions
- **Utilisateur normal** : Accès refusé
- **Organisateur** : Accès refusé
- **Super Admin** : Accès autorisé

### 3. Validation des Données
- **Event ID invalide** : Erreur 404
- **Action invalide** : Erreur 400
- **Raison manquante** : Erreur 400 (pour reject/suspend)

## Tests de Performance

### 1. Chargement des Données
- **Temps de réponse** : < 2 secondes
- **Pagination** : Chargement progressif
- **Filtres** : Application en temps réel

### 2. Modération en Lot
- **10 événements** : < 5 secondes
- **50 événements** : < 15 secondes
- **100 événements** : < 30 secondes

## Scénarios de Test

### Scénario 1 : Workflow de Modération Standard
1. Créer un événement en brouillon
2. Approuver l'événement
3. Vérifier la publication
4. Suspendre l'événement
5. Vérifier le retour en brouillon

### Scénario 2 : Modération en Lot
1. Créer plusieurs événements en brouillon
2. Sélectionner tous les événements
3. Approuver en lot
4. Vérifier la publication de tous

### Scénario 3 : Gestion des Erreurs
1. Tenter de rejeter sans raison
2. Vérifier le message d'erreur
3. Ajouter une raison
4. Vérifier le succès

### Scénario 4 : Historique et Traçabilité
1. Effectuer plusieurs actions sur un événement
2. Consulter l'historique
3. Vérifier la chronologie
4. Vérifier les détails des modifications

## Validation des Résultats

### 1. Base de Données
- **Statut des événements** : Mise à jour correcte
- **Historique** : Enregistrement des actions
- **Raisons** : Stockage des justifications

### 2. Interface Utilisateur
- **Notifications** : Messages de succès/erreur
- **Mise à jour** : Rafraîchissement des données
- **Navigation** : Changement d'onglets automatique

### 3. API
- **Réponses** : Codes de statut corrects
- **Données** : Format JSON valide
- **Erreurs** : Messages d'erreur explicites

## Maintenance et Surveillance

### 1. Logs
- **Actions de modération** : Traçabilité complète
- **Erreurs** : Enregistrement des problèmes
- **Performance** : Temps de réponse

### 2. Métriques
- **Taux de succès** : Actions réussies vs échouées
- **Temps de modération** : Performance du système
- **Utilisation** : Fréquence des actions

### 3. Alertes
- **Erreurs critiques** : Notifications immédiates
- **Performance** : Seuils de temps de réponse
- **Sécurité** : Tentatives d'accès non autorisées

## Évolutions Futures

### 1. Fonctionnalités Planifiées
- **Modération automatique** : Règles prédéfinies
- **Notifications** : Alertes aux organisateurs
- **Rapports** : Statistiques de modération

### 2. Améliorations Techniques
- **Cache** : Optimisation des performances
- **Webhooks** : Intégrations externes
- **API GraphQL** : Requêtes plus flexibles

## Conclusion

Le système de modération des événements offre un contrôle complet et sécurisé sur le contenu de la plateforme. Les fonctionnalités de modération individuelle et en lot, combinées à un historique détaillé, permettent une administration efficace et transparente.

La traçabilité complète des actions garantit la conformité et facilite la résolution des problèmes. L'interface intuitive et les validations robustes assurent une utilisation fiable du système.
