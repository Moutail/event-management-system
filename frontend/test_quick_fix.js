// Test rapide des corrections de syntaxe
console.log('🔧 Test des corrections de syntaxe');

// Test de la logique du bouton
const getButtonText = (loading, paymentLoading, pendingReg, isPaid, sessionTypes, sessionTypeId) => {
  if (loading || paymentLoading) return 'Traitement...';
  if (pendingReg && isPaid) return 'Procéder au paiement ci-dessous';
  if (isPaid) return 'Procéder au paiement';
  if (sessionTypes.length > 0 && !sessionTypeId) return 'Sélectionnez une session';
  return 'Confirmer l\'inscription';
};

// Test des scénarios
const testScenarios = [
  { name: 'Chargement', loading: true, paymentLoading: false, pendingReg: false, isPaid: false, sessionTypes: [], sessionTypeId: '' },
  { name: 'Paiement en cours', loading: false, paymentLoading: true, pendingReg: false, isPaid: false, sessionTypes: [], sessionTypeId: '' },
  { name: 'Paiement en attente', loading: false, paymentLoading: false, pendingReg: true, isPaid: true, sessionTypes: [], sessionTypeId: '' },
  { name: 'Événement payant', loading: false, paymentLoading: false, pendingReg: false, isPaid: true, sessionTypes: [], sessionTypeId: '' },
  { name: 'Sessions sans choix', loading: false, paymentLoading: false, pendingReg: false, isPaid: false, sessionTypes: ['session1'], sessionTypeId: '' },
  { name: 'Sessions avec choix', loading: false, paymentLoading: false, pendingReg: false, isPaid: false, sessionTypes: ['session1'], sessionTypeId: 'session1' },
  { name: 'Événement gratuit', loading: false, paymentLoading: false, pendingReg: false, isPaid: false, sessionTypes: [], sessionTypeId: '' }
];

console.log('\n🧪 Test des scénarios:');
testScenarios.forEach(scenario => {
  const buttonText = getButtonText(
    scenario.loading, 
    scenario.paymentLoading, 
    scenario.pendingReg, 
    scenario.isPaid, 
    scenario.sessionTypes, 
    scenario.sessionTypeId
  );
  console.log(`   ${scenario.name}: "${buttonText}"`);
});

// Test de validation des sessions
const validateSessionSelection = (sessionTypes, sessionTypeId) => {
  if (sessionTypes.length > 0 && !sessionTypeId) {
    return false; // Session requise mais non sélectionnée
  }
  return true; // OK
};

console.log('\n✅ Validation des sessions:');
testScenarios.forEach(scenario => {
  const isValid = validateSessionSelection(scenario.sessionTypes, scenario.sessionTypeId);
  console.log(`   ${scenario.name}: ${isValid ? '✅ Valide' : '❌ Invalide'}`);
});

console.log('\n🎯 Corrections terminées !');
console.log('📋 Prochaines étapes:');
console.log('   1. Vérifier que la compilation fonctionne');
console.log('   2. Tester dans le navigateur');
console.log('   3. Créer un événement avec des sessions');
console.log('   4. Tester l\'inscription avec choix de session');









