# Système de Gestion d'Événements

Un système complet de gestion d'événements avec backend Django et frontend React.

## 🚀 Fonctionnalités

### Backend (Django)
- **API REST** avec Django REST Framework
- **Authentification JWT** (JSON Web Tokens)
- **Base de données MySQL** via XAMPP
- **Gestion des événements** (CRUD complet)
- **Système de catégories et tags**
- **Inscriptions aux événements**
- **Historique des modifications**
- **Filtrage et recherche avancés**
- **Gestion des images** (affiches, bannières)

### Frontend (React)
- **Interface moderne** avec Material-UI
- **Gestion d'état** avec Redux Toolkit
- **Navigation** avec React Router
- **Authentification** complète
- **Pages principales** :
  - Accueil avec événements en vedette
  - Liste des événements avec filtres
  - Détails d'événement
  - Création/édition d'événements
  - Mes événements
  - Tableau de bord
  - Profil utilisateur

## 🛠️ Technologies Utilisées

### Backend
- Python 3.11
- Django 4.2.7
- Django REST Framework
- MySQL (via XAMPP)
- JWT Authentication
- Pillow (gestion d'images)
- django-cors-headers
- django-filter

### Frontend
- React 18
- Material-UI (MUI)
- Redux Toolkit
- React Router
- Axios
- date-fns
- react-hook-form

## 📋 Prérequis

1. **Python 3.11** installé
2. **Node.js** (version 16 ou supérieure)
3. **XAMPP** avec MySQL démarré
4. **Git**

## 🚀 Installation

### 1. Cloner le projet
```bash
git clone <url-du-repo>
cd event-management-system
```

### 2. Configuration Backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer la base de données
# Assurez-vous que MySQL est démarré dans XAMPP
python manage.py makemigrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser

# Insérer des données de test (optionnel)
python insert_sample_data.py
```

### 3. Configuration Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm start
```

## 🏃‍♂️ Démarrage

### Backend
```bash
cd backend
.venv\Scripts\activate  # Windows
python manage.py runserver
```
Le serveur backend sera accessible sur `http://localhost:8000`

### Frontend
```bash
cd frontend
npm start
```
L'application frontend sera accessible sur `http://localhost:3001`

## 📊 Données de Test

Le projet inclut des scripts pour gérer les données de test :

### Insérer des données de test
```bash
cd backend
python insert_sample_data.py
```

### Nettoyer les données de test
```bash
cd backend
python clear_sample_data.py
```

## 👤 Comptes de Test

Après avoir exécuté `insert_sample_data.py`, vous aurez accès à :

- **Admin** : `admin` / `admin123`
- **Utilisateurs de test** : `testuser1` à `testuser5` / `test123`

## 🔧 Configuration

### Variables d'environnement Backend

Créer un fichier `.env` dans le dossier `backend/` :

```env
DEBUG=True
SECRET_KEY=votre-clé-secrète
DATABASE_URL=mysql://root:@localhost:3306/event_management
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3001,http://127.0.0.1:3001
```

### Configuration Base de Données

1. Démarrer XAMPP
2. Démarrer MySQL
3. Créer une base de données nommée `event_management`
4. Exécuter les migrations Django

## 📁 Structure du Projet

```
event-management-system/
├── backend/
│   ├── event_management/     # Configuration Django
│   ├── events/              # Application événements
│   ├── requirements.txt     # Dépendances Python
│   ├── insert_sample_data.py
│   └── clear_sample_data.py
├── frontend/
│   ├── public/              # Fichiers statiques
│   ├── src/
│   │   ├── components/      # Composants React
│   │   ├── pages/          # Pages de l'application
│   │   ├── store/          # Configuration Redux
│   │   ├── services/       # Services API
│   │   └── theme.js        # Configuration MUI
│   └── package.json
└── README.md
```

## 🔌 API Endpoints

### Authentification
- `POST /api/token/` - Connexion
- `POST /api/token/refresh/` - Rafraîchir le token
- `POST /api/auth/register/` - Inscription
- `GET /api/auth/user/` - Informations utilisateur

### Événements
- `GET /api/events/` - Liste des événements
- `POST /api/events/` - Créer un événement
- `GET /api/events/{id}/` - Détails d'un événement
- `PUT /api/events/{id}/` - Modifier un événement
- `DELETE /api/events/{id}/` - Supprimer un événement
- `POST /api/events/{id}/duplicate/` - Dupliquer un événement
- `POST /api/events/{id}/publish/` - Publier un événement
- `POST /api/events/{id}/cancel/` - Annuler un événement

### Catégories et Tags
- `GET /api/categories/` - Liste des catégories
- `GET /api/tags/` - Liste des tags

### Inscriptions
- `GET /api/registrations/` - Liste des inscriptions
- `POST /api/registrations/` - S'inscrire à un événement

## 🎨 Fonctionnalités Frontend

### Pages Principales
1. **Accueil** - Événements en vedette et à venir
2. **Événements** - Liste avec filtres et recherche
3. **Détail Événement** - Informations complètes et inscription
4. **Créer Événement** - Formulaire de création
5. **Mes Événements** - Événements créés par l'utilisateur
6. **Tableau de Bord** - Statistiques et aperçu
7. **Profil** - Gestion du compte utilisateur

### Fonctionnalités
- **Authentification** complète avec JWT
- **Filtrage** par catégorie, prix, date, lieu
- **Recherche** textuelle
- **Pagination** des résultats
- **Responsive design** pour mobile et desktop
- **Thème sombre/clair** (préparé)
- **Notifications** en temps réel

## 🐛 Dépannage

### Erreurs Courantes

1. **Erreur de connexion MySQL**
   - Vérifier que XAMPP est démarré
   - Vérifier que MySQL est actif
   - Vérifier les paramètres de connexion

2. **Erreurs CORS**
   - Vérifier que `CORS_ALLOWED_ORIGINS` inclut `http://localhost:3001`
   - Redémarrer le serveur backend

3. **Erreurs de migration**
   - Supprimer la base de données et la recréer
   - Exécuter `python manage.py makemigrations` puis `migrate`

4. **Erreurs frontend**
   - Vérifier que le backend est démarré sur le port 8000
   - Vérifier la configuration du proxy dans `package.json`

## 📝 Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

## 🤝 Support

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub. 