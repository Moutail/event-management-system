# Guide de Test - Export des Inscriptions et Gestion des Remboursements

## Vue d'ensemble

Ce guide détaille les tests pour vérifier que :
1. Les demandes de remboursement sont correctement enregistrées dans la base de données
2. L'admin peut voir et gérer les demandes de remboursement
3. L'export des données des personnes inscrites aux événements fonctionne
4. Les données exportées incluent les informations de remboursement

## Fonctionnalités à Tester

### 1. Gestion des Demandes de Remboursement
- **Création automatique** : Lorsqu'un utilisateur annule son inscription
- **Enregistrement en base** : Vérification que la demande est bien sauvegardée
- **Visibilité admin** : L'admin peut voir toutes les demandes
- **Statuts** : Gestion des différents statuts (pending, approved, processed, rejected)

### 2. Export des Inscriptions
- **Export CSV** : Téléchargement des données en format CSV
- **Export Excel** : Téléchargement des données en format Excel
- **Données complètes** : Inclusions de toutes les informations pertinentes
- **Informations remboursement** : Statut des demandes de remboursement

## Tests de Fonctionnalités

### 1. Test de Création d'une Demande de Remboursement
1. Créer un événement avec politique de remboursement
2. Inscrire un utilisateur à l'événement
3. Annuler l'inscription de l'utilisateur
4. **Résultat attendu** : 
   - Demande de remboursement créée automatiquement
   - Statut initial : 'pending'
   - Montants calculés correctement
   - Date d'expiration définie

### 2. Test de Visibilité des Remboursements pour l'Admin
1. Se connecter en tant que super admin
2. Aller dans l'onglet "Remboursements"
3. **Résultat attendu** : 
   - Liste des demandes de remboursement visible
   - Filtrage par statut fonctionnel
   - Actions (approuver, rejeter) disponibles

### 3. Test de la Section Remboursements dans les Détails d'Événement
1. Ouvrir les détails d'un événement avec des demandes de remboursement
2. Vérifier la section "Demandes de Remboursement"
3. **Résultat attendu** : 
   - Affichage des vraies demandes
   - Montants et statuts corrects
   - Total des demandes et montant total

### 4. Test d'Export CSV des Inscriptions
1. Dans les détails d'un événement, cliquer sur le bouton "CSV"
2. **Résultat attendu** : 
   - Téléchargement du fichier CSV
   - Fichier contient toutes les colonnes attendues
   - Données des remboursements incluses

### 5. Test d'Export Excel des Inscriptions
1. Dans les détails d'un événement, cliquer sur le bouton "Excel"
2. **Résultat attendu** : 
   - Téléchargement du fichier Excel
   - Fichier contient toutes les colonnes attendues
   - Données des remboursements incluses
   - Colonnes ajustées automatiquement

## Tests de Robustesse

### 1. Test avec Événement sans Inscriptions
1. Sélectionner un événement sans inscriptions
2. Tenter l'export
3. **Résultat attendu** : Fichier avec en-têtes uniquement

### 2. Test avec Événement avec Demandes de Remboursement
1. Sélectionner un événement avec des demandes de remboursement
2. Vérifier l'export
3. **Résultat attendu** : Colonnes de remboursement remplies

### 3. Test de Gestion des Erreurs
1. Tenter l'export d'un événement inexistant
2. **Résultat attendu** : Message d'erreur approprié

## Tests d'Intégration

### 1. Test de Cohérence des Données
1. Comparer les données affichées dans l'interface
2. Avec les données exportées
3. **Résultat attendu** : Cohérence parfaite

### 2. Test de Navigation
1. Depuis l'onglet "Remboursements", naviguer vers les détails d'événement
2. Depuis les détails, naviguer vers l'onglet "Remboursements"
3. **Résultat attendu** : Navigation fluide

## Validation des Données Exportées

### 1. Colonnes CSV/Excel Attendues
- **ID Inscription** : Identifiant unique de l'inscription
- **Username** : Nom d'utilisateur
- **Email** : Adresse email
- **Nom** : Prénom de l'utilisateur
- **Prénom** : Nom de famille de l'utilisateur
- **Status** : Statut de l'inscription
- **Type de Billet** : Type de billet sélectionné
- **Prix Payé** : Montant payé
- **Date d'inscription** : Date et heure d'inscription
- **Statut Paiement** : Statut du paiement
- **Demande de Remboursement** : Oui/Non
- **Statut Remboursement** : Statut de la demande

### 2. Vérification des Données de Remboursement
1. **Demande de Remboursement** : Doit indiquer "Oui" ou "Non"
2. **Statut Remboursement** : Doit indiquer le statut actuel ou "Aucune"

## Tests de Performance

### 1. Test avec Beaucoup d'Inscriptions
1. Créer un événement avec de nombreuses inscriptions
2. Tester l'export
3. **Résultat attendu** : Export rapide et fichier correct

### 2. Test de Taille de Fichier
1. Vérifier la taille des fichiers exportés
2. **Résultat attendu** : Fichiers de taille raisonnable

## Tests de Sécurité

### 1. Test d'Authentification
1. Tenter l'export sans être connecté
2. **Résultat attendu** : Erreur 401 Unauthorized

### 2. Test de Permissions
1. Tenter l'export avec un utilisateur non-admin
2. **Résultat attendu** : Erreur 403 Forbidden

## Résolution des Problèmes

### Si les Remboursements ne s'Affichent Pas
1. Vérifier que les demandes sont bien créées en base
2. Contrôler les relations entre modèles
3. Vérifier les permissions d'accès

### Si l'Export ne Fonctionne Pas
1. Vérifier la console pour les erreurs JavaScript
2. Contrôler que l'API backend fonctionne
3. Vérifier l'authentification et les permissions
4. Contrôler que openpyxl est installé pour Excel

### Si les Données Exportées sont Incorrectes
1. Vérifier la structure des données en base
2. Contrôler la logique d'export
3. Vérifier la cohérence des modèles

## Conclusion

Les fonctionnalités de gestion des remboursements et d'export des inscriptions doivent maintenant fonctionner correctement :

- ✅ **Demandes de remboursement** : Créées automatiquement et visibles par l'admin
- ✅ **Export CSV** : Téléchargement des données en format CSV
- ✅ **Export Excel** : Téléchargement des données en format Excel
- ✅ **Données complètes** : Inclusions de toutes les informations pertinentes
- ✅ **Gestion des erreurs** : Messages d'erreur appropriés

Tous les tests doivent passer pour valider le bon fonctionnement de ces fonctionnalités.
