# 📧 Guide du Système de Notifications Automatiques

## 🎯 Fonctionnalités

Le système envoie automatiquement des emails de rappel :
- **📅 24h avant** l'événement (rappel J-1)
- **⏰ 1h avant** l'événement (rappel dernière heure)
- **🎉 12h après** l'événement (remerciement)

## 🚀 Installation et Configuration

### 1. Configuration Email

Assurez-vous que les paramètres SMTP sont configurés dans votre fichier `.env` :

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre.email@gmail.com
EMAIL_HOST_PASSWORD=votre_mot_de_passe_app
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=votre.email@gmail.com
```

### 2. Test Manuel

Pour tester le système manuellement :

```bash
# Activer l'environnement virtuel (si nécessaire)
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows

# Exécuter la commande de notifications
python manage.py send_event_notifications
```

### 3. Exécution Automatique

#### Option 1: Script PowerShell (Windows)

```powershell
# Exécuter avec intervalle par défaut (15 minutes)
.\run_notifications.ps1

# Exécuter avec intervalle personnalisé (ex: 10 minutes)
.\run_notifications.ps1 -IntervalMinutes 10
```

#### Option 2: Script Bash (Linux/macOS)

```bash
# Rendre le script exécutable
chmod +x run_notifications.sh

# Exécuter avec intervalle par défaut (15 minutes)
./run_notifications.sh

# Exécuter avec intervalle personnalisé (ex: 10 minutes)
./run_notifications.sh 10
```

#### Option 3: Cron (Linux/macOS) - Production

Ajoutez cette ligne à votre crontab (`crontab -e`) :

```bash
# Exécuter toutes les 15 minutes
*/15 * * * * cd /path/to/your/project && source .venv/bin/activate && python manage.py send_event_notifications >> /var/log/notifications.log 2>&1
```

#### Option 4: Tâche Planifiée Windows - Production

1. Ouvrir "Planificateur de tâches"
2. Créer une tâche de base
3. **Déclencheur** : Répéter toutes les 15 minutes
4. **Action** : Démarrer un programme
   - Programme : `PowerShell`
   - Arguments : `-File "C:\path\to\your\project\run_notifications.ps1"`

## 📋 Logs et Surveillance

### Fichiers de Log

- **notifications.log** : Log principal du script automatique
- **Console Django** : Logs en temps réel si le serveur Django est en cours d'exécution

### Types de Notifications Trackées

Le système évite les doublons grâce au modèle `NotificationLog` :
- `reminder_1d` : Rappel 24h avant
- `reminder_1h` : Rappel 1h avant  
- `reminder_day` : Rappel jour J (obsolète, remplacé par 1h)
- `thank_you` : Remerciement post-événement

## 🔧 Personnalisation

### Templates d'Email

Les templates sont dans `events/templates/emails/` :
- `reminder_1d.txt/.html` : Rappel 24h
- `reminder_1h.txt/.html` : Rappel 1h
- `thank_you.txt/.html` : Remerciement

### Modifier les Intervalles

Dans `send_event_notifications.py`, vous pouvez ajuster :
- **Rappel 24h** : `hours=23, minutes=30` à `hours=24, minutes=30`
- **Rappel 1h** : `minutes=45` à `minutes=75`

## 🐛 Dépannage

### Problèmes Courants

1. **Emails non envoyés** : Vérifiez la configuration SMTP
2. **Doublons** : Le système les évite automatiquement via `NotificationLog`
3. **Erreurs de timing** : Les événements doivent avoir `status='published'`

### Debug

```bash
# Voir les événements concernés
python manage.py shell
>>> from events.models import Event
>>> from django.utils import timezone
>>> now = timezone.now()
>>> events_24h = Event.objects.filter(
...     start_date__gte=now + timezone.timedelta(hours=23, minutes=30),
...     start_date__lt=now + timezone.timedelta(hours=24, minutes=30),
...     status='published'
... )
>>> print(f"Événements dans 24h: {events_24h.count()}")
```

## 📊 Statut du Service

Pour vérifier si le service fonctionne :
1. Consultez `notifications.log`
2. Vérifiez les entrées dans la table `NotificationLog`
3. Testez manuellement avec `python manage.py send_event_notifications`

---

**🎉 Le système est maintenant entièrement fonctionnel !**

Les participants recevront automatiquement leurs rappels aux bons moments ! 📧⏰






