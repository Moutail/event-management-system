# Guide de Test - Export des Participants dans les Détails d'Événement

## Vue d'ensemble

Ce guide détaille les tests pour vérifier que l'exportation des participants fonctionne correctement dans la section "Participants" des détails d'événement.

## Problème Résolu

**Avant** : La section "Participants" était manquante dans le composant EventDetailModal, et la vue backend ne renvoyait pas la liste complète des participants.

**Après** : 
- Ajout de la section "Participants" avec affichage de la liste complète
- Boutons d'exportation CSV et Excel dans cette section
- Vue backend modifiée pour renvoyer toutes les données des participants

## Fonctionnalités à Tester

### 1. Affichage de la Section Participants
- **Visibilité** : La section "Participants (X)" doit être visible dans les détails d'événement
- **Compteur** : Le nombre de participants doit correspondre aux statistiques
- **Liste** : Affichage de tous les participants avec leurs informations

### 2. Informations des Participants
- **Données utilisateur** : Nom, prénom, email, username
- **Statut inscription** : confirmed, pending, cancelled, attended
- **Paiement** : Prix payé, statut de paiement
- **Type de billet** : Nom du type de billet
- **Date d'inscription** : Format français
- **Demandes de remboursement** : Statut et montant si applicable

### 3. Boutons d'Exportation
- **Localisation** : Boutons CSV et Excel dans l'en-tête de la section Participants
- **Fonctionnalité** : Téléchargement des fichiers avec les bonnes données
- **Gestion d'erreur** : Messages d'erreur appropriés en cas de problème

## Tests de Fonctionnalités

### 1. Test d'Affichage de la Section Participants
1. Se connecter en tant que super admin
2. Ouvrir les détails d'un événement avec des participants
3. **Résultat attendu** : 
   - Section "Participants (X)" visible
   - X correspond au nombre total d'inscriptions
   - Liste des participants affichée avec toutes les informations

### 2. Test d'Export CSV depuis la Section Participants
1. Dans la section "Participants", cliquer sur le bouton "CSV"
2. **Résultat attendu** : 
   - Téléchargement du fichier CSV
   - Nom du fichier : `inscriptions_event_{id}.csv`
   - Contenu : Toutes les colonnes avec les données des participants

### 3. Test d'Export Excel depuis la Section Participants
1. Dans la section "Participants", cliquer sur le bouton "Excel"
2. **Résultat attendu** : 
   - Téléchargement du fichier Excel
   - Nom du fichier : `inscriptions_event_{id}.xlsx`
   - Contenu : Toutes les colonnes avec les données des participants
   - Colonnes ajustées automatiquement

### 4. Test avec Événement sans Participants
1. Ouvrir les détails d'un événement sans inscriptions
2. **Résultat attendu** : 
   - Section "Participants (0)" visible
   - Message "Aucun participant inscrit à cet événement"
   - Boutons d'exportation toujours disponibles

### 5. Test avec Participants avec Demandes de Remboursement
1. Ouvrir les détails d'un événement avec des demandes de remboursement
2. **Résultat attendu** : 
   - Chips de statut de remboursement visibles
   - Couleurs appropriées selon le statut
   - Informations de remboursement dans l'export

## Tests de Robustesse

### 1. Test de Gestion des Erreurs
1. Tenter l'export avec un événement inexistant
2. **Résultat attendu** : Message d'erreur approprié

### 2. Test de Performance
1. Ouvrir les détails d'un événement avec beaucoup de participants
2. **Résultat attendu** : Chargement rapide, pas de blocage

### 3. Test de Cohérence des Données
1. Comparer les données affichées dans la liste
2. Avec les données exportées
3. **Résultat attendu** : Cohérence parfaite

## Validation des Données Exportées

### 1. Colonnes CSV/Excel Attendues
- **ID Inscription** : Identifiant unique de l'inscription
- **Username** : Nom d'utilisateur
- **Email** : Adresse email
- **Nom** : Nom de famille
- **Prénom** : Prénom
- **Status** : Statut de l'inscription
- **Type de Billet** : Nom du type de billet
- **Prix Payé** : Montant payé
- **Date d'inscription** : Date et heure d'inscription
- **Statut Paiement** : Statut du paiement
- **Demande de Remboursement** : Oui/Non
- **Statut Remboursement** : Statut de la demande

### 2. Données des Participants
- **Informations complètes** : Tous les champs remplis
- **Format des dates** : Format français (DD/MM/YYYY HH:MM)
- **Montants** : Format monétaire approprié
- **Statuts** : Traduction en français si applicable

## Tests d'Intégration

### 1. Navigation depuis la Section Participants
1. Depuis la section Participants, naviguer vers d'autres sections
2. **Résultat attendu** : Navigation fluide, pas de perte de données

### 2. Cohérence avec les Statistiques
1. Vérifier que le nombre de participants affiché correspond
2. Aux statistiques dans la section "Statistiques des Inscriptions"
3. **Résultat attendu** : Cohérence parfaite

## Résolution des Problèmes

### 1. Section Participants Non Visible
- Vérifier que le composant EventDetailModal a été mis à jour
- Vérifier que la vue backend renvoie les données `registrations`
- Vérifier la console du navigateur pour les erreurs JavaScript

### 2. Exportation Ne Fonctionne Pas
- Vérifier que les routes d'export sont correctement configurées
- Vérifier les permissions super admin
- Vérifier les logs du backend pour les erreurs
- Vérifier que les fonctions d'export sont correctement importées

### 3. Données Manquantes dans l'Export
- Vérifier que la vue backend renvoie tous les champs nécessaires
- Vérifier que les relations sont correctement préchargées
- Vérifier que les données sont correctement formatées

## Validation Finale

Après avoir effectué tous les tests :

1. ✅ Section Participants visible avec le bon compteur
2. ✅ Liste des participants affichée avec toutes les informations
3. ✅ Boutons d'exportation CSV et Excel fonctionnels
4. ✅ Fichiers téléchargés avec les bonnes données
5. ✅ Gestion des erreurs appropriée
6. ✅ Performance acceptable même avec beaucoup de participants

## Notes Techniques

- **Frontend** : Composant EventDetailModal modifié pour inclure la section Participants
- **Backend** : Vue `super_admin_event_detail` modifiée pour renvoyer `registrations`
- **Export** : Fonctions `super_admin_export_registrations_csv` et `super_admin_export_registrations_excel`
- **Permissions** : Requiert les droits super admin
- **Performance** : Utilisation de `select_related` et `prefetch_related` pour optimiser les requêtes
