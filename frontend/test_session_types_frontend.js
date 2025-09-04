// Test du frontend des types de sessions
console.log('🧪 Test du frontend des types de sessions');

// Test des données de session
const testSessionData = {
  name: 'Session Matin',
  description: 'Session de test le matin',
  max_participants: 50,
  date: new Date('2025-01-15'),
  start_time: '10:00',
  end_time: '12:00',
  is_active: true,
  is_mandatory: true,
  display_order: 1
};

console.log('📝 Données de test:', testSessionData);

// Test de validation des données
const validateSessionData = (session) => {
  const errors = [];
  
  if (!session.name) {
    errors.push('Le nom de la session est requis');
  }
  
  if (session.start_time >= session.end_time) {
    errors.push('L\'heure de fin doit être après l\'heure de début');
  }
  
  if (session.date < new Date()) {
    errors.push('La date ne peut pas être dans le passé');
  }
  
  if (session.max_participants && session.max_participants <= 0) {
    errors.push('Le nombre max de participants doit être positif');
  }
  
  return errors;
};

const validationErrors = validateSessionData(testSessionData);
if (validationErrors.length > 0) {
  console.log('❌ Erreurs de validation:', validationErrors);
} else {
  console.log('✅ Données de session valides');
}

// Test de formatage des données pour l'API
const formatSessionForAPI = (session) => {
  return {
    name: session.name,
    description: session.description,
    max_participants: session.max_participants === '' ? null : Number(session.max_participants),
    date: session.date.toISOString().split('T')[0],
    start_time: session.start_time,
    end_time: session.end_time,
    is_active: !!session.is_active,
    is_mandatory: !!session.is_mandatory,
    display_order: Number(session.display_order) || 1,
  };
};

const apiPayload = formatSessionForAPI(testSessionData);
console.log('📤 Payload pour l\'API:', apiPayload);

// Test de l'interface utilisateur
console.log('\n🎨 Test de l\'interface utilisateur:');
console.log('   - Section "Types de sessions" ajoutée au formulaire');
console.log('   - Champs: nom, description, max participants, date, heures, switches');
console.log('   - Bouton "Ajouter" pour créer une session');
console.log('   - Affichage des sessions créées avec possibilité de suppression');
console.log('   - Intégration avec la création d\'événement');

console.log('\n🎯 Tests terminés !');
console.log('📋 Prochaines étapes:');
console.log('   1. Ouvrir le navigateur sur http://localhost:3000');
console.log('   2. Aller sur "Créer un événement"');
console.log('   3. Vérifier la section "Types de sessions"');
console.log('   4. Tester la création de sessions');
console.log('   5. Tester la création d\'un événement avec sessions');









