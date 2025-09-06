// Test de debug des sessions
console.log('🔍 Test de debug des sessions');

// Simulation de l'API response
const mockApiResponse = {
  data: [
    {
      id: 1,
      name: 'Session Matin',
      date: '2025-08-25',
      start_time: '10:00:00',
      end_time: '12:00:00',
      is_active: true,
      is_mandatory: true,
      max_participants: 50,
      current_participants: 30,
      display_order: 1
    },
    {
      id: 2,
      name: 'Session Après-midi',
      date: '2025-08-25',
      start_time: '14:00:00',
      end_time: '16:00:00',
      is_active: true,
      is_mandatory: true,
      max_participants: 50,
      current_participants: 25,
      display_order: 2
    }
  ]
};

console.log('📊 Données simulées de l\'API:');
console.log('   - Nombre total de sessions:', mockApiResponse.data.length);
console.log('   - Sessions:', mockApiResponse.data.map(s => s.name));

// Test du filtrage et tri
const sessionTypes = mockApiResponse.data || [];
console.log('\n🔍 Test du filtrage et tri:');
console.log('   - Total des sessions:', sessionTypes.length);

const activeSessions = sessionTypes.filter(session => session.is_active);
console.log('   - Sessions actives:', activeSessions.length);

const sortedSessions = activeSessions.sort((a, b) => a.display_order - b.display_order);
console.log('   - Sessions triées:', sortedSessions.map(s => s.name));

// Test de l'affichage des participants avec session
const mockParticipant = {
  user: { first_name: 'John', last_name: 'Doe', email: 'john@example.com' },
  ticket_type_name: 'VIP',
  price_paid: 25.00,
  session_type_name: 'Session Matin'
};

console.log('\n👤 Test d\'affichage des participants:');
console.log('   - Participant avec session:', mockParticipant);
console.log('   - Affichage secondaire:', `${mockParticipant.user.email} • ${mockParticipant.ticket_type_name} • $${mockParticipant.price_paid} • Session: ${mockParticipant.session_type_name}`);

// Test sans session
const mockParticipantNoSession = {
  user: { first_name: 'Jane', last_name: 'Smith', email: 'jane@example.com' },
  ticket_type_name: 'Standard',
  price_paid: 15.00,
  session_type_name: null
};

console.log('\n👤 Test participant sans session:');
console.log('   - Participant sans session:', mockParticipantNoSession);
console.log('   - Affichage secondaire:', `${mockParticipantNoSession.user.email} • ${mockParticipantNoSession.ticket_type_name} • $${mockParticipantNoSession.price_paid}${mockParticipantNoSession.session_type_name ? ` • Session: ${mockParticipantNoSession.session_type_name}` : ''}`);

console.log('\n🎯 Debug des sessions terminé !');
console.log('📋 Vérifications à faire dans le navigateur:');
console.log('   1. Ouvrir la console pour voir les logs de debug');
console.log('   2. Vérifier que 2 sessions s\'affichent dans le dropdown');
console.log('   3. Vérifier que la session est visible dans la liste des participants');











