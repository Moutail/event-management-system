// Test des règles de timing des événements
const testEventTimingRules = () => {
  console.log('🧪 Test des règles de timing des événements');
  console.log('=' * 60);

  const now = new Date();
  
  // Test 1: Événement à venir (plus de 12h)
  const futureEvent = {
    start_date: new Date(now.getTime() + (24 * 60 * 60 * 1000)), // +24h
    end_date: new Date(now.getTime() + (26 * 60 * 60 * 1000)),   // +26h
    status: 'published'
  };

  const canRegisterFuture = futureEvent.status === 'published' && new Date(futureEvent.end_date) >= now;
  const canCancelFuture = (() => {
    const eventStart = new Date(futureEvent.start_date);
    const hoursUntilEvent = (eventStart - now) / (1000 * 60 * 60);
    return hoursUntilEvent > 12;
  })();

  console.log('Test 1 - Événement à venir (+24h):');
  console.log(`   Status: ${futureEvent.status}`);
  console.log(`   Début: ${futureEvent.start_date.toLocaleString()}`);
  console.log(`   Fin: ${futureEvent.end_date.toLocaleString()}`);
  console.log(`   Peut s'inscrire: ${canRegisterFuture ? '✅ Oui' : '❌ Non'}`);
  console.log(`   Peut annuler: ${canCancelFuture ? '✅ Oui' : '❌ Non'}`);
  console.log('');

  // Test 2: Événement bientôt (moins de 12h)
  const soonEvent = {
    start_date: new Date(now.getTime() + (6 * 60 * 60 * 1000)),  // +6h
    end_date: new Date(now.getTime() + (8 * 60 * 60 * 1000)),    // +8h
    status: 'published'
  };

  const canRegisterSoon = soonEvent.status === 'published' && new Date(soonEvent.end_date) >= now;
  const canCancelSoon = (() => {
    const eventStart = new Date(soonEvent.start_date);
    const hoursUntilEvent = (eventStart - now) / (1000 * 60 * 60);
    return hoursUntilEvent > 12;
  })();

  console.log('Test 2 - Événement bientôt (+6h):');
  console.log(`   Status: ${soonEvent.status}`);
  console.log(`   Début: ${soonEvent.start_date.toLocaleString()}`);
  console.log(`   Fin: ${soonEvent.end_date.toLocaleString()}`);
  console.log(`   Peut s'inscrire: ${canRegisterSoon ? '✅ Oui' : '❌ Non'}`);
  console.log(`   Peut annuler: ${canCancelSoon ? '✅ Oui' : '❌ Non'}`);
  console.log('');

  // Test 3: Événement en cours
  const ongoingEvent = {
    start_date: new Date(now.getTime() - (1 * 60 * 60 * 1000)),  // -1h (commencé)
    end_date: new Date(now.getTime() + (1 * 60 * 60 * 1000)),    // +1h (pas fini)
    status: 'published'
  };

  const canRegisterOngoing = ongoingEvent.status === 'published' && new Date(ongoingEvent.end_date) >= now;
  const canCancelOngoing = (() => {
    const eventStart = new Date(ongoingEvent.start_date);
    const hoursUntilEvent = (eventStart - now) / (1000 * 60 * 60);
    return hoursUntilEvent > 12;
  })();

  console.log('Test 3 - Événement en cours:');
  console.log(`   Status: ${ongoingEvent.status}`);
  console.log(`   Début: ${ongoingEvent.start_date.toLocaleString()}`);
  console.log(`   Fin: ${ongoingEvent.end_date.toLocaleString()}`);
  console.log(`   Peut s'inscrire: ${canRegisterOngoing ? '✅ Oui' : '❌ Non'}`);
  console.log(`   Peut annuler: ${canCancelOngoing ? '✅ Oui' : '❌ Non'}`);
  console.log('');

  // Test 4: Événement terminé
  const finishedEvent = {
    start_date: new Date(now.getTime() - (3 * 60 * 60 * 1000)),  // -3h (commencé)
    end_date: new Date(now.getTime() - (1 * 60 * 60 * 1000)),    // -1h (fini)
    status: 'published'
  };

  const canRegisterFinished = finishedEvent.status === 'published' && new Date(finishedEvent.end_date) >= now;
  const canCancelFinished = (() => {
    const eventStart = new Date(finishedEvent.start_date);
    const hoursUntilEvent = (eventStart - now) / (1000 * 60 * 60);
    return hoursUntilEvent > 12;
  })();

  console.log('Test 4 - Événement terminé:');
  console.log(`   Status: ${finishedEvent.status}`);
  console.log(`   Début: ${finishedEvent.start_date.toLocaleString()}`);
  console.log(`   Fin: ${finishedEvent.end_date.toLocaleString()}`);
  console.log(`   Peut s'inscrire: ${canRegisterFinished ? '✅ Oui' : '❌ Non'}`);
  console.log(`   Peut annuler: ${canCancelFinished ? '✅ Oui' : '❌ Non'}`);
  console.log('');

  console.log('✅ Test terminé!');
  console.log('📝 Règles appliquées:');
  console.log('   1. Inscription possible jusqu\'à la fin de l\'événement');
  console.log('   2. Annulation impossible moins de 12h avant le début');
  console.log('   3. Bouton "S\'inscrire" grisé si événement terminé');
  console.log('   4. Bouton "Annuler" désactivé si < 12h avant début');
};

// Exécuter le test
testEventTimingRules();

















