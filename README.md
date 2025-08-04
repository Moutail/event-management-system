# Système de Gestion d'Événements

Un système complet de gestion d'événements avec backend Django et frontend React.

## ⚡ Démarrage Rapide (pour les développeurs expérimentés)

```bash
# 1. Cloner et installer
git clone <url-du-repo>
cd event-management-system

# 2. Backend (dans un terminal)
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 3. Frontend (dans un autre terminal)
cd frontend
npm install
npm start
```

**🎯 Résultat :** 
- Frontend : http://localhost:3001
- Backend API : http://localhost:8000/api/
- Admin Django : http://localhost:8000/admin/

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
   - Télécharger depuis [python.org](https://www.python.org/downloads/)
   - Vérifier l'installation : `python --version`

2. **Node.js** (version 16 ou supérieure)
   - Télécharger depuis [nodejs.org](https://nodejs.org/)
   - Vérifier l'installation : `node --version` et `npm --version`

3. **XAMPP** avec MySQL
   - Télécharger depuis [apachefriends.org](https://www.apachefriends.org/)
   - Installer et démarrer MySQL via le panneau de contrôle XAMPP

4. **Git**
   - Télécharger depuis [git-scm.com](https://git-scm.com/)
   - Vérifier l'installation : `git --version`

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

# Créer un superuser (suivez les instructions)
python manage.py createsuperuser

# Insérer des données de test (optionnel)
python insert_sample_data.py
```

**⚠️ Important :** Si vous rencontrez des erreurs lors de l'installation des dépendances Python, essayez :
```bash
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances une par une si nécessaire
pip install Django==4.2.7
pip install djangorestframework==3.14.0
# ... etc
```

### 3. Configuration Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Démarrer le serveur de développement
npm start
```

**⚠️ Important :** Si vous rencontrez des erreurs lors de l'installation des dépendances Node.js, essayez :
```bash
# Nettoyer le cache npm
npm cache clean --force

# Supprimer node_modules et réinstaller
rm -rf node_modules package-lock.json
npm install
```

## 🏃‍♂️ Démarrage

### Backend
```bash
cd backend
# Activer l'environnement virtuel
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Démarrer le serveur
python manage.py runserver
```
Le serveur backend sera accessible sur `http://localhost:8000`

### Frontend
```bash
cd frontend
npm start
```
L'application frontend sera accessible sur `http://localhost:3001`

### Vérification
1. Ouvrez votre navigateur
2. Allez sur `http://localhost:3001` pour le frontend
3. L'API backend sera accessible sur `http://localhost:8000/api/`
4. L'interface d'administration Django : `http://localhost:8000/admin/`

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
DB_NAME=event_management
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3001,http://127.0.0.1:3001
```

**💡 Note :** Si vous n'avez pas de mot de passe pour votre utilisateur MySQL root, laissez `DB_PASSWORD=` vide.

### Configuration Base de Données

1. **Démarrer XAMPP**
   - Ouvrir XAMPP Control Panel
   - Cliquer sur "Start" pour Apache et MySQL
   - Vérifier que les services sont en vert

2. **Créer la base de données**
   - Ouvrir phpMyAdmin : `http://localhost/phpmyadmin`
   - Cliquer sur "Nouvelle base de données"
   - Nommer la base : `event_management`
   - Cliquer sur "Créer"

3. **Exécuter les migrations Django**
   ```bash
   cd backend
   python manage.py makemigrations
   python manage.py migrate
   ```

**🔧 Alternative :** Si vous préférez utiliser SQLite (plus simple pour les tests) :
- Modifiez `backend/event_management/settings.py` ligne 67-75
- Remplacez la configuration MySQL par :
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

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

#### 1. **Erreur de connexion MySQL**
```bash
# Symptômes : django.db.utils.OperationalError: (2002, "Can't connect to MySQL server")
# Solutions :
- Vérifier que XAMPP est démarré et MySQL actif
- Vérifier les paramètres dans .env
- Redémarrer XAMPP
```

#### 2. **Erreurs CORS**
```bash
# Symptômes : CORS policy: No 'Access-Control-Allow-Origin' header
# Solutions :
- Vérifier CORS_ALLOWED_ORIGINS dans .env
- Redémarrer le serveur backend
- Vider le cache du navigateur
```

#### 3. **Erreurs de migration**
```bash
# Symptômes : django.db.utils.OperationalError lors des migrations
# Solutions :
- Supprimer et recréer la base de données
- python manage.py makemigrations --empty events
- python manage.py makemigrations
- python manage.py migrate
```

#### 4. **Erreurs frontend**
```bash
# Symptômes : Cannot connect to backend API
# Solutions :
- Vérifier que le backend tourne sur le port 8000
- Vérifier la configuration proxy dans package.json
- Redémarrer les deux serveurs
```

#### 5. **Erreurs d'installation des dépendances**
```bash
# Python :
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Node.js :
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Commandes de diagnostic
```bash
# Vérifier les versions
python --version
node --version
npm --version

# Vérifier les services
# Windows : services.msc (chercher MySQL)
# Linux : sudo systemctl status mysql

# Vérifier les ports
netstat -an | grep 8000  # Backend
netstat -an | grep 3001  # Frontend
```

## ❓ FAQ

### **Q: Puis-je utiliser une autre base de données que MySQL ?**
**R:** Oui ! Le projet supporte SQLite (plus simple) et PostgreSQL. Modifiez `backend/event_management/settings.py` pour changer la configuration.

### **Q: Le frontend ne se connecte pas au backend, que faire ?**
**R:** Vérifiez que :
1. Le backend tourne sur le port 8000
2. Le frontend tourne sur le port 3001
3. Les deux serveurs sont démarrés simultanément

### **Q: Comment ajouter de nouveaux types d'événements ?**
**R:** Utilisez le système de catégories et tags intégré. Créez de nouvelles catégories via l'admin Django ou l'API.

### **Q: Puis-je déployer ce projet en production ?**
**R:** Oui ! Changez `DEBUG=False` dans les paramètres et configurez une base de données de production.

### **Q: Comment personnaliser le design ?**
**R:** Modifiez `frontend/src/theme.js` pour changer les couleurs et styles Material-UI.

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