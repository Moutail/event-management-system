// Test de l'affichage des places
const testCapacityDisplay = () => {
  console.log('🧪 Test de l\'affichage des places');
  console.log('=' * 50);

  // Test 1: Événement avec places limitées
  const limitedEvent = {
    place_type: 'limited',
    max_capacity: 100,
    current_registrations: 25
  };

  const limitedDisplay = limitedEvent.place_type === 'limited' && limitedEvent.max_capacity ? 
    `${limitedEvent.max_capacity - (limitedEvent.current_registrations || 0)} places disponibles` : 
    'Places illimitées';

  console.log('Test 1 - Places limitées:');
  console.log(`   place_type: ${limitedEvent.place_type}`);
  console.log(`   max_capacity: ${limitedEvent.max_capacity}`);
  console.log(`   current_registrations: ${limitedEvent.current_registrations}`);
  console.log(`   Affichage: ${limitedDisplay}`);
  console.log('');

  // Test 2: Événement avec places illimitées
  const unlimitedEvent = {
    place_type: 'unlimited',
    max_capacity: null,
    current_registrations: 0
  };

  const unlimitedDisplay = unlimitedEvent.place_type === 'limited' && unlimitedEvent.max_capacity ? 
    `${unlimitedEvent.max_capacity - (unlimitedEvent.current_registrations || 0)} places disponibles` : 
    'Places illimitées';

  console.log('Test 2 - Places illimitées:');
  console.log(`   place_type: ${unlimitedEvent.place_type}`);
  console.log(`   max_capacity: ${unlimitedEvent.max_capacity}`);
  console.log(`   current_registrations: ${unlimitedEvent.current_registrations}`);
  console.log(`   Affichage: ${unlimitedDisplay}`);
  console.log('');

  // Test 3: Événement avec places limitées mais sans max_capacity
  const limitedNoCapacityEvent = {
    place_type: 'limited',
    max_capacity: null,
    current_registrations: 0
  };

  const limitedNoCapacityDisplay = limitedNoCapacityEvent.place_type === 'limited' && limitedNoCapacityEvent.max_capacity ? 
    `${limitedNoCapacityEvent.max_capacity - (limitedNoCapacityEvent.current_registrations || 0)} places disponibles` : 
    'Places illimitées';

  console.log('Test 3 - Places limitées sans capacité:');
  console.log(`   place_type: ${limitedNoCapacityEvent.place_type}`);
  console.log(`   max_capacity: ${limitedNoCapacityEvent.max_capacity}`);
  console.log(`   current_registrations: ${limitedNoCapacityEvent.current_registrations}`);
  console.log(`   Affichage: ${limitedNoCapacityDisplay}`);
  console.log('');

  console.log('✅ Test terminé!');
  console.log('📝 Résumé:');
  console.log('   - Places limitées avec capacité: Affiche le nombre de places disponibles');
  console.log('   - Places illimitées: Affiche "Places illimitées"');
  console.log('   - Places limitées sans capacité: Affiche "Places illimitées" (fallback)');
};

// Exécuter le test
testCapacityDisplay();














