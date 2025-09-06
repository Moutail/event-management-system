// Test des URLs d'images
const getImageUrl = (imagePath) => {
  if (!imagePath) return null;
  
  // Si c'est déjà une URL complète, la retourner
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath;
  }
  
  // Construire l'URL correcte pour les images (pas via l'API)
  const BASE_URL = 'http://localhost:8001';
  
  // Si le chemin commence par /media/, l'utiliser directement
  if (imagePath.startsWith('/media/')) {
    return `${BASE_URL}${imagePath}`;
  }
  
  // Sinon, ajouter /media/ si nécessaire
  if (!imagePath.startsWith('/')) {
    imagePath = `/${imagePath}`;
  }
  
  return `${BASE_URL}${imagePath}`;
};

// Tests
console.log('🧪 Test des URLs d\'images');
console.log('=' * 50);

const testCases = [
  '/media/events/posters/image.jpg',
  'media/events/posters/image.jpg',
  'events/posters/image.jpg',
  'http://example.com/image.jpg',
  null,
  ''
];

testCases.forEach((path, index) => {
  const result = getImageUrl(path);
  console.log(`Test ${index + 1}: "${path}"`);
  console.log(`   Résultat: ${result}`);
  console.log('');
});

console.log('✅ Test terminé!');
















