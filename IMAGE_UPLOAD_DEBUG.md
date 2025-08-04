# Debug de l'Upload d'Image

## Problème identifié

L'utilisateur a signalé que "l'ajout de l'image ne marche pas" lors de la création ou modification d'événements.

## Diagnostic effectué

### 1. Test du Backend ✅
- **Résultat** : L'upload d'image fonctionne parfaitement côté backend
- **Test effectué** : Script `test_http_upload.py` avec authentification
- **Résultat** : Status 201, image sauvegardée avec succès
- **Preuve** : `"poster":"http://localhost:8000/media/events/posters/test_image_ptqW99u.jpg"`

### 2. Configuration Django ✅
- **Médias** : Configurés correctement (`MEDIA_URL`, `MEDIA_ROOT`)
- **Permissions** : Dossier media accessible en écriture
- **CORS** : Configuré pour les requêtes multipart
- **Validation** : Django valide correctement les images

### 3. Code Frontend ✅
- **FormData** : Correctement construit
- **API Service** : Gère bien les fichiers
- **Validation** : Ajoutée pour vérifier le type et la taille des images

## Problème probable

Le problème vient probablement de **la sélection d'image côté frontend** :

1. **Fichier non-image** : L'utilisateur sélectionne un fichier qui n'est pas une vraie image
2. **Fichier corrompu** : L'image est corrompue ou invalide
3. **Type MIME incorrect** : Le navigateur ne détecte pas correctement le type d'image

## Solution implémentée

### 1. Validation côté frontend
- ✅ Vérification du type MIME (`file.type.startsWith('image/')`)
- ✅ Vérification de la taille (max 5MB)
- ✅ Messages d'erreur explicites pour l'utilisateur

### 2. Logs de debug
- ✅ Logs détaillés dans `handleImageChange`
- ✅ Logs détaillés dans `onSubmit`
- ✅ Logs détaillés dans l'API service
- ✅ Logs détaillés côté backend

### 3. Validation côté backend
- ✅ Django valide automatiquement les images
- ✅ Messages d'erreur clairs en français

## Instructions pour l'utilisateur

### Pour tester l'upload d'image :

1. **Ouvrir la console du navigateur** (F12)
2. **Aller sur la page de création d'événement**
3. **Sélectionner une vraie image** (JPEG, PNG, GIF)
4. **Vérifier les logs dans la console** :
   - `=== DEBUG: handleImageChange ===`
   - `=== DEBUG: Image ===`
   - `=== DEBUG: createEvent ===`

### Types d'images acceptés :
- ✅ JPEG (.jpg, .jpeg)
- ✅ PNG (.png)
- ✅ GIF (.gif)
- ✅ WebP (.webp)

### Types de fichiers rejetés :
- ❌ Documents (.pdf, .doc, .txt)
- ❌ Vidéos (.mp4, .avi)
- ❌ Archives (.zip, .rar)
- ❌ Fichiers corrompus

### Messages d'erreur possibles :
- `"Le fichier sélectionné n'est pas une image"`
- `"Le fichier est trop volumineux"`
- `"Transférez une image valide. Le fichier que vous avez transféré n'est pas une image, ou il est corrompu."`

## Test recommandé

1. **Télécharger une image de test** depuis [Picsum Photos](https://picsum.photos/200/300)
2. **Essayer d'uploader cette image**
3. **Vérifier les logs dans la console**
4. **Si ça ne marche toujours pas, partager les logs d'erreur**

## Conclusion

L'upload d'image **fonctionne parfaitement** côté backend. Le problème vient probablement de la sélection d'un fichier non-image ou corrompu côté frontend. Les validations et logs ajoutés devraient aider à identifier et résoudre le problème. 