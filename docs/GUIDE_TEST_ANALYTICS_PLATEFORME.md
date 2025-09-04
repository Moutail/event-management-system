# Guide de Test - Analytics de la Plateforme

## Vue d'ensemble

Ce guide détaille les tests pour vérifier que la partie "Analytics de la Plateforme" du super admin charge et affiche correctement les vraies données de la base de données.

## Fonctionnalités à Tester

### 1. Chargement des Données
- **API Endpoint** : `/api/admin/analytics/`
- **Authentification** : Requiert un token JWT valide
- **Permissions** : Seuls les super admins peuvent accéder
- **Source des données** : Base de données en temps réel

### 2. Affichage des Métriques
- **Utilisateurs totaux** : Nombre total d'utilisateurs de la plateforme
- **Organisateurs actifs** : Nombre d'organisateurs avec des événements
- **Événements publiés** : Nombre d'événements au statut 'published'
- **Revenus ce mois** : Chiffre d'affaires des 30 derniers jours (en dollars $)

### 3. Statistiques Quotidiennes
- **Période** : 7 derniers jours
- **Données** : Nouveaux utilisateurs, événements, inscriptions, revenus (en dollars $)
- **Format** : Tableau avec dates et métriques

### 4. Métriques de Croissance
- **Croissance utilisateurs** : Pourcentage sur 30 jours
- **Croissance événements** : Pourcentage sur 30 jours
- **Croissance revenus** : Pourcentage sur 30 jours

### 5. Statistiques des Remboursements
- **Remboursements en attente** : Nombre de demandes 'pending'
- **Remboursements approuvés** : Nombre de demandes 'approved'
- **Remboursements rejetés** : Nombre de demandes 'rejected'
- **Montant total** : Somme des montants approuvés (en dollars $)

### 6. Top Organisateurs
- **Classement** : Par revenus totaux
- **Informations** : Nom, nombre d'événements, revenus (en dollars $)
- **Visualisation** : Barres de progression

### 7. Top Événements par Revenus
- **Classement** : Top 10 événements
- **Informations** : Titre, organisateur, date, revenus (en dollars $)
- **Format** : Tableau avec chips de rang

## Tests de Fonctionnalités

### 1. Test de Chargement Initial
1. Se connecter en tant que super admin
2. Aller dans l'onglet "Analytics de la Plateforme"
3. **Résultat attendu** : 
   - Affichage d'un indicateur de chargement (CircularProgress)
   - Puis affichage des données ou d'un message d'erreur

### 2. Test de l'API Backend
1. Vérifier que l'endpoint `/api/admin/analytics/` est accessible
2. **Résultat attendu** : Réponse 200 avec données JSON structurées

### 3. Test d'Affichage des Métriques Principales
1. Vérifier l'affichage des 4 cartes principales
2. Contrôler que les valeurs correspondent aux vraies données
3. **Résultat attendu** : Métriques affichées avec icônes et couleurs appropriées

### 4. Test des Statistiques Quotidiennes
1. Vérifier le tableau des 7 derniers jours
2. Contrôler que les dates sont correctes
3. **Résultat attendu** : Données quotidiennes affichées dans un tableau

### 5. Test des Métriques de Croissance
1. Vérifier l'affichage des 3 cartes de croissance
2. Contrôler que les pourcentages sont calculés correctement
3. **Résultat attendu** : Pourcentages affichés avec icônes de tendance

### 6. Test des Statistiques de Remboursements
1. Vérifier l'affichage des 4 métriques de remboursements
2. Contrôler que les couleurs correspondent aux statuts
3. **Résultat attendu** : Statistiques affichées avec codes couleur appropriés

### 7. Test du Top des Organisateurs
1. Vérifier l'affichage des organisateurs
2. Contrôler que les barres de progression sont proportionnelles
3. **Résultat attendu** : Liste des organisateurs avec barres de progression

### 8. Test du Top des Événements
1. Vérifier l'affichage du tableau des événements
2. Contrôler que les chips de rang sont colorés correctement
3. **Résultat attendu** : Tableau avec événements classés par revenus

## Tests de Robustesse

### 1. Test avec Base de Données Vide
1. Vider temporairement la base de données
2. Charger la page d'analytics
3. **Résultat attendu** : Affichage de valeurs 0 et messages appropriés

### 2. Test avec Données Partielles
1. Créer des données partielles (utilisateurs sans événements, etc.)
2. Charger la page d'analytics
3. **Résultat attendu** : Gestion gracieuse des données manquantes

### 3. Test de Performance
1. Créer un grand volume de données
2. Mesurer le temps de chargement
3. **Résultat attendu** : Chargement en moins de 5 secondes

## Tests d'Intégration

### 1. Test avec Authentification
1. Tester sans token JWT
2. **Résultat attendu** : Erreur 401 Unauthorized

### 2. Test avec Permissions Insuffisantes
1. Tester avec un utilisateur non-super-admin
2. **Résultat attendu** : Erreur 403 Forbidden

### 3. Test de Cohérence des Données
1. Comparer les données affichées avec la base de données
2. **Résultat attendu** : Cohérence parfaite entre affichage et données

## Tests Spécifiques au Composant

### 1. Test de l'État du Composant
1. Vérifier que `analytics` est initialisé à `null`
2. Vérifier que `loading` est initialisé à `true`
3. Vérifier que `error` est initialisé à `null`
4. **Résultat attendu** : États initiaux corrects

### 2. Test de la Fonction `loadAnalytics`
1. Vérifier que la fonction est appelée au montage du composant
2. Vérifier que l'API est appelée avec les bons paramètres
3. **Résultat attendu** : Fonction exécutée correctement

### 3. Test de Gestion des Erreurs
1. Simuler une erreur de l'API
2. Vérifier l'affichage du message d'erreur
3. Vérifier le bouton "Réessayer"
4. **Résultat attendu** : Gestion gracieuse des erreurs

## Validation des Données

### 1. Vérification des Compteurs
1. Compter manuellement les utilisateurs dans la base
2. Comparer avec l'affichage
3. **Résultat attendu** : Correspondance exacte

### 2. Vérification des Revenus
1. Calculer manuellement les revenus des 30 derniers jours
2. Comparer avec l'affichage
3. **Résultat attendu** : Correspondance exacte

### 3. Vérification des Croissances
1. Calculer manuellement les pourcentages de croissance
2. Comparer avec l'affichage
3. **Résultat attendu** : Correspondance exacte

## Tests de l'Interface Utilisateur

### 1. Test de Responsivité
1. Tester sur différentes tailles d'écran
2. **Résultat attendu** : Interface adaptée à toutes les tailles

### 2. Test d'Accessibilité
1. Vérifier les contrastes de couleurs
2. Vérifier la lisibilité des textes
3. **Résultat attendu** : Interface accessible et lisible

### 3. Test de Navigation
1. Vérifier que le bouton "Actualiser" fonctionne
2. **Résultat attendu** : Rechargement des données au clic

## Résolution des Problèmes

### Si les Données ne se Chargent Pas
1. Vérifier la console pour les erreurs JavaScript
2. Contrôler que l'API backend fonctionne
3. Vérifier l'authentification et les permissions
4. Contrôler la structure des données retournées

### Si les Données sont Incorrectes
1. Vérifier les requêtes SQL dans le backend
2. Contrôler la logique de calcul des métriques
3. Vérifier la cohérence des modèles de données

### Si l'Interface est Lente
1. Optimiser les requêtes de base de données
2. Implémenter la pagination si nécessaire
3. Mettre en cache les données statiques

## Conclusion

La partie "Analytics de la Plateforme" doit maintenant charger et afficher les vraies données de la base de données en temps réel. Tous les tests doivent passer pour valider le bon fonctionnement de cette fonctionnalité.

Les données affichées incluent :
- Métriques principales (utilisateurs, organisateurs, événements, revenus)
- Statistiques quotidiennes (7 derniers jours)
- Métriques de croissance (30 jours)
- Statistiques des remboursements
- Top des organisateurs et événements
- Répartition des rôles utilisateurs
