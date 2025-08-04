# Guide de Debug - Upload d'Image Frontend

## 🔍 Diagnostic du Problème

Le backend fonctionne parfaitement (testé et validé). Le problème vient du frontend. Voici comment identifier et résoudre le problème :

## 📋 Étapes de Debug

### 1. **Vérifier la Console du Navigateur**

1. **Ouvrez la console** (F12)
2. **Allez sur la page de création d'événement**
3. **Sélectionnez une image**
4. **Vérifiez les logs** :

```
=== DEBUG: handleImageChange ===
Fichier sélectionné: File {name: "image.jpg", type: "image/jpeg", size: 12345}
✅ Image valide sélectionnée
✅ Aperçu de l'image généré
```

### 2. **Vérifier l'Upload**

1. **Remplissez le formulaire** avec toutes les informations
2. **Soumettez le formulaire**
3. **Vérifiez les logs** :

```
=== DEBUG: Données du formulaire ===
Données: {title: "Test", description: "Test", ...}
Tags sélectionnés: [1, 2]

=== DEBUG: Image ===
Image trouvée: File {name: "image.jpg", type: "image/jpeg", size: 12345}
✅ Image ajoutée au FormData
✅ Image confirmée dans FormData: image.jpg

=== DEBUG: Contenu du FormData ===
title: Test
description: Test
poster: File
...
```

### 3. **Vérifier la Modification**

1. **Allez sur la page de modification** d'un événement
2. **Sélectionnez une nouvelle image**
3. **Vérifiez les logs** :

```
=== DEBUG: EditEventPage handleImageChange ===
Fichier sélectionné: File {name: "new_image.jpg", type: "image/jpeg", size: 12345}
✅ Image valide sélectionnée
✅ Aperçu de l'image généré

=== DEBUG: EditEventPage onSubmit ===
=== DEBUG: Image ===
Image trouvée: File {name: "new_image.jpg", type: "image/jpeg", size: 12345}
✅ Image ajoutée au FormData
✅ Image confirmée dans FormData: new_image.jpg
```

## 🚨 Problèmes Possibles et Solutions

### Problème 1 : Aucun fichier sélectionné
**Symptômes :**
```
❌ Aucun fichier sélectionné
❌ Aucune image trouvée
```

**Solutions :**
- Vérifiez que vous cliquez bien sur le bouton "Choisir une image"
- Vérifiez que le fichier est bien une image (JPEG, PNG, GIF)
- Vérifiez que la taille est inférieure à 5MB

### Problème 2 : Fichier non-image
**Symptômes :**
```
❌ Le fichier sélectionné n'est pas une image
```

**Solutions :**
- Sélectionnez un vrai fichier image (pas un PDF, document, etc.)
- Formats acceptés : JPEG, PNG, GIF, WebP

### Problème 3 : Fichier trop volumineux
**Symptômes :**
```
❌ Le fichier est trop volumineux
```

**Solutions :**
- Réduisez la taille de l'image (max 5MB)
- Utilisez un outil de compression d'image

### Problème 4 : Image non ajoutée au FormData
**Symptômes :**
```
❌ Image non trouvée dans FormData
```

**Solutions :**
- Vérifiez que l'input file a l'ID `poster-input`
- Vérifiez que la fonction `handleImageChange` est bien appelée

### Problème 5 : Erreur lors de l'envoi
**Symptômes :**
```
❌ Erreur lors de la création: 400
```

**Solutions :**
- Vérifiez que tous les champs obligatoires sont remplis
- Vérifiez que l'image est valide
- Regardez les détails de l'erreur dans la console

## 🧪 Test de Validation

### Test 1 : Image Simple
1. **Téléchargez une image de test** depuis [Picsum Photos](https://picsum.photos/400/300)
2. **Créez un événement** avec cette image
3. **Vérifiez** que l'image s'affiche

### Test 2 : Modification d'Image
1. **Allez sur un événement existant**
2. **Modifiez l'image**
3. **Vérifiez** que la nouvelle image s'affiche

### Test 3 : Événement sans Image
1. **Créez un événement sans image**
2. **Modifiez-le** pour ajouter une image
3. **Vérifiez** que l'image s'affiche

## 📊 Logs Attendus

### Création d'Événement Réussie
```
=== DEBUG: handleImageChange ===
Fichier sélectionné: File {name: "test.jpg", type: "image/jpeg", size: 12345}
✅ Image valide sélectionnée
✅ Aperçu de l'image généré

=== DEBUG: Données du formulaire ===
Données: {title: "Test", ...}
Tags sélectionnés: [1]

=== DEBUG: Image ===
Image trouvée: File {name: "test.jpg", type: "image/jpeg", size: 12345}
✅ Image ajoutée au FormData
✅ Image confirmée dans FormData: test.jpg

=== DEBUG: Contenu du FormData ===
title: Test
description: Test
poster: File
...

Envoi de la requête...
✅ Succès: {id: 19, title: "Test", poster: "http://localhost:8000/media/events/posters/test_abc123.jpg"}
```

### Modification d'Événement Réussie
```
=== DEBUG: EditEventPage handleImageChange ===
Fichier sélectionné: File {name: "new.jpg", type: "image/jpeg", size: 12345}
✅ Image valide sélectionnée
✅ Aperçu de l'image généré

=== DEBUG: EditEventPage onSubmit ===
Données: {title: "Test", ...}
Tags sélectionnés: [1]

=== DEBUG: Image ===
Image trouvée: File {name: "new.jpg", type: "image/jpeg", size: 12345}
✅ Image ajoutée au FormData
✅ Image confirmée dans FormData: new.jpg

Envoi de la requête de mise à jour...
✅ Mise à jour réussie
```

## 🔧 Corrections Apportées

### 1. **EditEventPage.js**
- ✅ Ajout de logs détaillés dans `handleImageChange`
- ✅ Ajout de validation d'image (type et taille)
- ✅ Ajout de logs détaillés dans `onSubmit`
- ✅ Amélioration de la gestion des erreurs

### 2. **CreateEventPage.js**
- ✅ Logs détaillés déjà présents
- ✅ Validation d'image déjà présente
- ✅ Gestion des erreurs déjà présente

## 📞 En Cas de Problème Persistant

Si le problème persiste après avoir suivi ce guide :

1. **Partagez les logs complets** de la console
2. **Décrivez exactement** ce qui se passe à chaque étape
3. **Indiquez** le type et la taille du fichier que vous essayez d'uploader
4. **Précisez** si c'est lors de la création ou de la modification

## 🎯 Résultat Attendu

Après avoir suivi ce guide et appliqué les corrections :

- ✅ **Création d'événement** : L'image s'upload et s'affiche
- ✅ **Modification d'événement** : L'image se modifie et s'affiche
- ✅ **Logs détaillés** : Toutes les étapes sont tracées
- ✅ **Validation** : Seuls les fichiers images valides sont acceptés 