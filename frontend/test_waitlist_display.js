// Test de l'affichage des places avec liste d'attente
const testWaitlistDisplay = () => {
  console.log('🧪 Test de l\'affichage des places avec liste d\'attente');
  console.log('=' * 60);

  // Test 1: Événement avec places disponibles
  const availableEvent = {
    place_type: 'limited',
    max_capacity: 100,
    current_registrations: 25
  };

  const availablePlaces = availableEvent.max_capacity - availableEvent.current_registrations;
  const availableDisplay = availablePlaces > 0 ? 
    `${availablePlaces} places disponibles` : 
    'Complet - Liste d\'attente';

  console.log('Test 1 - Places disponibles:');
  console.log(`   Capacité max: ${availableEvent.max_capacity}`);
  console.log(`   Inscriptions: ${availableEvent.current_registrations}`);
  console.log(`   Places libres: ${availablePlaces}`);
  console.log(`   Affichage: ${availableDisplay}`);
  console.log('');

  // Test 2: Événement complet (liste d'attente)
  const fullEvent = {
    place_type: 'limited',
    max_capacity: 50,
    current_registrations: 50
  };

  const fullPlaces = fullEvent.max_capacity - fullEvent.current_registrations;
  const fullDisplay = fullPlaces > 0 ? 
    `${fullPlaces} places disponibles` : 
    'Complet - Liste d\'attente';

  console.log('Test 2 - Événement complet:');
  console.log(`   Capacité max: ${fullEvent.max_capacity}`);
  console.log(`   Inscriptions: ${fullEvent.current_registrations}`);
  console.log(`   Places libres: ${fullPlaces}`);
  console.log(`   Affichage: ${fullDisplay}`);
  console.log('');

  // Test 3: Événement presque complet
  const almostFullEvent = {
    place_type: 'limited',
    max_capacity: 100,
    current_registrations: 98
  };

  const almostFullPlaces = almostFullEvent.max_capacity - almostFullEvent.current_registrations;
  const almostFullDisplay = almostFullPlaces > 0 ? 
    `${almostFullPlaces} places disponibles` : 
    'Complet - Liste d\'attente';

  console.log('Test 3 - Presque complet:');
  console.log(`   Capacité max: ${almostFullEvent.max_capacity}`);
  console.log(`   Inscriptions: ${almostFullEvent.current_registrations}`);
  console.log(`   Places libres: ${almostFullPlaces}`);
  console.log(`   Affichage: ${almostFullDisplay}`);
  console.log('');

  // Test 4: Événement avec places illimitées
  const unlimitedEvent = {
    place_type: 'unlimited',
    max_capacity: null,
    current_registrations: 0
  };

  const unlimitedDisplay = 'Places illimitées';

  console.log('Test 4 - Places illimitées:');
  console.log(`   place_type: ${unlimitedEvent.place_type}`);
  console.log(`   max_capacity: ${unlimitedEvent.max_capacity}`);
  console.log(`   Affichage: ${unlimitedDisplay}`);
  console.log('');

  console.log('✅ Test terminé!');
  console.log('📝 Résumé de l\'affichage:');
  console.log('   - Places disponibles > 0: "X places disponibles"');
  console.log('   - Places disponibles = 0: "Complet - Liste d\'attente"');
  console.log('   - Places illimitées: "Places illimitées"');
  console.log('   - Message liste d\'attente: "Vous pouvez vous inscrire et serez placé sur liste d\'attente"');
};

// Exécuter le test
testWaitlistDisplay();














