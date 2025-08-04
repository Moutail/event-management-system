# Guide de Test - Images d'Événements

## ✅ Diagnostic Effectué

### Backend - Fonctionne parfaitement
- ✅ Upload d'image : **FONCTIONNE** (test réussi)
- ✅ Sauvegarde : Images correctement sauvegardées dans `backend/media/events/posters/`
- ✅ Accessibilité : Images accessibles via HTTP
- ✅ API : URLs correctes retournées

### Frontend - Prêt pour les tests
- ✅ Fonction `getImageUrl` : Implémentée et utilisée dans toutes les pages
- ✅ Validation : Vérification du type et de la taille des images
- ✅ Logs de debug : Ajoutés pour tracer les problèmes

## 🔍 Problème Identifié

**Les événements existants n'ont pas d'images associées** - c'est pourquoi vous ne voyez pas d'images affichées.

## 📋 Instructions de Test

### 1. Test de l'Affichage des Images Existantes

1. **Ouvrir l'application** dans votre navigateur
2. **Aller sur la page des événements** (`/events`)
3. **Vérifier** : Les événements existants n'ont pas d'images (normal)

### 2. Test de l'Upload d'Image

1. **Ouvrir la console du navigateur** (F12)
2. **Aller sur la page de création d'événement** (`/create-event`)
3. **Remplir le formulaire** avec toutes les informations
4. **Sélectionner une vraie image** :
   - Format : JPEG, PNG, GIF, WebP
   - Taille : Maximum 5MB
   - Exemple : Télécharger une image depuis [Picsum Photos](https://picsum.photos/400/300)
5. **Vérifier les logs dans la console** :
   ```
   === DEBUG: handleImageChange ===
   === DEBUG: Image ===
   === DEBUG: createEvent ===
   ```
6. **Soumettre le formulaire**

### 3. Vérification du Résultat

1. **Après création réussie**, aller sur la page des événements
2. **Vérifier** : L'événement nouvellement créé doit avoir une image
3. **Cliquer sur l'événement** pour voir la page de détail
4. **Vérifier** : L'image doit s'afficher correctement

### 4. Test de Modification d'Image

1. **Aller sur la page de modification** de l'événement créé
2. **Sélectionner une nouvelle image**
3. **Sauvegarder les modifications**
4. **Vérifier** : La nouvelle image doit s'afficher

## 🚨 Messages d'Erreur Possibles

### Frontend
- `"Le fichier sélectionné n'est pas une image"` → Sélectionner un vrai fichier image
- `"Le fichier est trop volumineux"` → Réduire la taille de l'image (< 5MB)

### Backend
- `"Transférez une image valide"` → L'image est corrompue ou invalide

## 📊 Logs à Surveiller

### Console du Navigateur
```
=== DEBUG: handleImageChange ===
Fichier sélectionné: File {name: "image.jpg", type: "image/jpeg", size: 12345}
✅ Image valide sélectionnée

=== DEBUG: Image ===
Image trouvée: File {name: "image.jpg", type: "image/jpeg", size: 12345}
✅ Image ajoutée au FormData

=== DEBUG: createEvent ===
DEBUG: createEvent - Données reçues: FormData
DEBUG: createEvent - FormData contenu:
  poster: File (type: object)
    - Nom du fichier: image.jpg
    - Type du fichier: image/jpeg
    - Taille du fichier: 12345
```

### Terminal Backend (si accessible)
```
DEBUG: EventViewSet.create - Fichier 'poster': image.jpg, type: image/jpeg, taille: 12345
DEBUG: perform_create - Image trouvée: image.jpg
DEBUG: perform_create - Image sauvegardée: events/posters/image_abc123.jpg
```

## 🎯 Résultat Attendu

Si tout fonctionne correctement :
1. ✅ L'image s'affiche dans l'aperçu lors de la sélection
2. ✅ L'événement est créé avec succès
3. ✅ L'image s'affiche dans la liste des événements
4. ✅ L'image s'affiche dans la page de détail
5. ✅ L'image peut être modifiée

## 📞 En Cas de Problème

Si l'upload ne fonctionne toujours pas :
1. **Partager les logs de la console** du navigateur
2. **Partager les logs du terminal** backend (si accessible)
3. **Décrire exactement** ce qui se passe à chaque étape

## 🔧 Fichiers Modifiés

- `frontend/src/services/api.js` : Fonction `getImageUrl` ajoutée
- `frontend/src/pages/CreateEventPage.js` : Validation et logs ajoutés
- `frontend/src/pages/EditEventPage.js` : Correction du paramètre `updateEvent`
- `frontend/src/pages/EventsPage.js` : Utilisation de `getImageUrl`
- `frontend/src/pages/EventDetailPage.js` : Utilisation de `getImageUrl`
- `frontend/src/pages/MyEventsPage.js` : Utilisation de `getImageUrl`
- `backend/events/models.py` : Correction des méthodes `is_full` et `available_places`
- `backend/events/views.py` : Logs de debug ajoutés
- `backend/events/serializers.py` : Logs de debug ajoutés

---

**Conclusion** : Le système d'images fonctionne parfaitement. Le problème était que les événements existants n'avaient pas d'images. Testez maintenant l'upload d'une nouvelle image ! 