# Guide de Test - Visibilité des Remboursements

## Vue d'ensemble

Ce guide détaille les tests pour vérifier que :
1. Les demandes de remboursement sont visibles dans le dashboard super admin
2. Les détails des événements affichent les vraies données de remboursement
3. L'API backend retourne correctement les informations de remboursement

## Fonctionnalités à Tester

### 1. Visibilité des Remboursements dans le Super Admin
- **Onglet "Remboursements"** : Doit afficher toutes les demandes de remboursement
- **Liste des remboursements** : Avec filtrage par statut et pagination
- **Actions sur les remboursements** : Approuver, rejeter, voir les détails

### 2. Détails des Événements - Section Remboursements
- **Section "Demandes de Remboursement"** : Doit afficher les vraies données
- **Informations affichées** : Montant, utilisateur, statut, raison
- **Résumé** : Total des demandes et montant total

### 3. API Backend - Données de Remboursement
- **Endpoint `/admin/events/{id}/detail/`** : Doit retourner `refund_requests`
- **Structure des données** : Informations complètes des remboursements
- **Relations** : Lien entre événement, inscription et demande de remboursement

## Tests de Fonctionnalités

### 1. Test de l'Onglet Remboursements du Super Admin
1. Se connecter en tant que super admin
2. Aller dans l'onglet "Remboursements" (4ème onglet)
3. **Résultat attendu** : 
   - Affichage de la liste des demandes de remboursement
   - Filtrage par statut (pending, approved, rejected, processed)
   - Boutons d'action pour chaque remboursement

### 2. Test de la Section Remboursements dans les Détails d'Événement
1. Dans l'onglet "Événements", cliquer sur "Voir les détails" d'un événement
2. Vérifier la section "Demandes de Remboursement"
3. **Résultat attendu** :
   - Affichage des vraies demandes de remboursement
   - Montant, nom d'utilisateur, statut et raison
   - Total des demandes et montant total
   - Limitation à 3 demandes avec indication du total

### 3. Test de l'API Backend des Détails d'Événement
1. Appeler l'endpoint `/api/admin/events/{id}/detail/` avec un token valide
2. Vérifier la structure de la réponse
3. **Résultat attendu** :
   - Champ `refund_requests` présent dans la réponse
   - Chaque remboursement contient : id, user, amount_paid, refund_amount, status, reason, dates

## Tests de Robustesse

### 1. Test avec Événement sans Remboursements
1. Sélectionner un événement sans demandes de remboursement
2. Ouvrir les détails
3. **Résultat attendu** : Message "Aucune demande de remboursement"

### 2. Test avec Événement avec Plus de 3 Remboursements
1. Sélectionner un événement avec plus de 3 demandes de remboursement
2. Ouvrir les détails
3. **Résultat attendu** : Affichage des 3 premiers + indication du total

### 3. Test de Filtrage des Remboursements
1. Dans l'onglet "Remboursements", utiliser le filtre par statut
2. **Résultat attendu** : Liste filtrée selon le statut sélectionné

## Tests d'Intégration

### 1. Test de Cohérence des Données
1. Comparer les données affichées dans l'onglet "Remboursements"
2. Avec les données affichées dans les détails d'événement
3. **Résultat attendu** : Cohérence parfaite entre les deux vues

### 2. Test de Navigation
1. Depuis l'onglet "Remboursements", cliquer sur "Voir les détails"
2. Depuis les détails d'événement, naviguer vers l'onglet "Remboursements"
3. **Résultat attendu** : Navigation fluide entre les vues

## Validation des Données

### 1. Vérification des Montants
1. Contrôler que les montants affichés correspondent aux vraies données
2. Vérifier le calcul du total des remboursements
3. **Résultat attendu** : Montants exacts et calculs corrects

### 2. Vérification des Statuts
1. Contrôler que les statuts affichés sont corrects
2. Vérifier la cohérence avec la base de données
3. **Résultat attendu** : Statuts à jour et cohérents

### 3. Vérification des Relations
1. Contrôler que les utilisateurs et événements sont correctement liés
2. Vérifier l'intégrité des données
3. **Résultat attendu** : Relations correctes et données cohérentes

## Tests de l'Interface Utilisateur

### 1. Test de Responsivité
1. Tester sur différentes tailles d'écran
2. **Résultat attendu** : Interface adaptée à toutes les tailles

### 2. Test d'Accessibilité
1. Vérifier les contrastes de couleurs
2. Vérifier la lisibilité des textes
3. **Résultat attendu** : Interface accessible et lisible

## Résolution des Problèmes

### Si les Remboursements ne s'Affichent Pas
1. Vérifier la console pour les erreurs JavaScript
2. Contrôler que l'API backend fonctionne
3. Vérifier l'authentification et les permissions
4. Contrôler la structure des données retournées

### Si les Données sont Incorrectes
1. Vérifier les requêtes SQL dans le backend
2. Contrôler la logique de calcul des montants
3. Vérifier la cohérence des modèles de données

### Si l'Interface est Lente
1. Optimiser les requêtes de base de données
2. Implémenter la pagination si nécessaire
3. Mettre en cache les données statiques

## Conclusion

Les remboursements doivent maintenant être visibles dans :
- L'onglet "Remboursements" du dashboard super admin
- La section "Demandes de Remboursement" des détails d'événement
- L'API backend avec la structure correcte

Tous les tests doivent passer pour valider le bon fonctionnement de la visibilité des remboursements.
