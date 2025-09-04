// FICHIER DE TEST POUR LE SYSTÈME DE SESSIONS
// À exécuter dans la console du navigateur

console.log('🧪 TEST DU SYSTÈME DE SESSIONS');

// 1. Vérifier l'état initial
console.log('1️⃣ ÉTAT INITIAL:');
console.log('localStorage:', localStorage);
console.log('current_session_id:', localStorage.getItem('current_session_id'));

// 2. Simuler une connexion User A
console.log('\n2️⃣ SIMULATION CONNEXION USER A:');
const userASession = {
  sessionId: 'session_1642851234567_abc123',
  access: 'token_user_a_123',
  refresh: 'refresh_user_a_456',
  user: { id: 1, username: 'userA', role: 'participant' },
  timestamp: Date.now()
};

localStorage.setItem('auth_session_session_1642851234567_abc123', JSON.stringify(userASession));
localStorage.setItem('current_session_id', 'session_1642851234567_abc123');

console.log('Session User A créée:', userASession);
console.log('localStorage après User A:', localStorage);

// 3. Simuler une connexion User B
console.log('\n3️⃣ SIMULATION CONNEXION USER B:');
const userBSession = {
  sessionId: 'session_1642851345678_def456',
  access: 'token_user_b_789',
  refresh: 'refresh_user_b_012',
  user: { id: 2, username: 'userB', role: 'organizer' },
  timestamp: Date.now()
};

localStorage.setItem('auth_session_session_1642851345678_def456', JSON.stringify(userBSession));
localStorage.setItem('current_session_id', 'session_1642851345678_def456');

console.log('Session User B créée:', userBSession);
console.log('localStorage après User B:', localStorage);

// 4. Vérifier que les sessions sont séparées
console.log('\n4️⃣ VÉRIFICATION SÉPARATION DES SESSIONS:');
console.log('Session User A:', localStorage.getItem('auth_session_session_1642851234567_abc123'));
console.log('Session User B:', localStorage.getItem('auth_session_session_1642851345678_def456'));
console.log('Session active:', localStorage.getItem('current_session_id'));

// 5. Simuler un changement de session (User A se reconnecte)
console.log('\n5️⃣ SIMULATION RECONNEXION USER A:');
localStorage.setItem('current_session_id', 'session_1642851234567_abc123');

console.log('Session active après reconnexion User A:', localStorage.getItem('current_session_id'));
console.log('Données User A:', JSON.parse(localStorage.getItem('auth_session_session_1642851234567_abc123')));
console.log('Données User B:', JSON.parse(localStorage.getItem('auth_session_session_1642851345678_def456')));

// 6. Simuler une déconnexion User A
console.log('\n6️⃣ SIMULATION DÉCONNEXION USER A:');
localStorage.removeItem('auth_session_session_1642851234567_abc123');
localStorage.removeItem('current_session_id');

console.log('localStorage après déconnexion User A:', localStorage);
console.log('Session User B toujours présente:', localStorage.getItem('auth_session_session_1642851345678_def456'));

console.log('\n✅ TEST TERMINÉ - Vérifiez la console pour les résultats');













