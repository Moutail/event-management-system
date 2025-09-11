/**
 * Script de test des endpoints frontend
 * Compare les URLs appelées par le frontend avec celles du backend
 */

import { EndpointAnalyzer, analyzeEndpoints, testEndpoint } from './src/utils/endpointAnalyzer.js';

class FrontendEndpointTester {
  constructor() {
    this.analyzer = new EndpointAnalyzer();
    this.results = {
      timestamp: new Date().toISOString(),
      frontend_analysis: {},
      backend_comparison: {},
      test_results: {},
      recommendations: []
    };
  }

  /**
   * Exécute tous les tests frontend
   */
  async runTests() {
    console.log('🚀 Démarrage du test des endpoints frontend...');
    console.log('='.repeat(80));

    // 1. Analyser les endpoints du frontend
    console.log('\n1️⃣ Analyse des endpoints frontend...');
    await this.analyzeFrontendEndpoints();

    // 2. Tester la connectivité avec le backend
    console.log('\n2️⃣ Test de connectivité avec le backend...');
    await this.testBackendConnectivity();

    // 3. Comparer avec les endpoints du backend
    console.log('\n3️⃣ Comparaison avec les endpoints backend...');
    await this.compareWithBackend();

    // 4. Générer des recommandations
    console.log('\n4️⃣ Génération des recommandations...');
    this.generateRecommendations();

    // 5. Afficher le résumé
    console.log('\n5️⃣ Résumé des tests...');
    this.printSummary();

    return this.results;
  }

  /**
   * Analyse les endpoints du frontend
   */
  async analyzeFrontendEndpoints() {
    try {
      const analysis = this.analyzer.analyze();
      this.results.frontend_analysis = analysis;

      console.log(`   ✅ ${analysis.total} endpoints frontend analysés`);
      console.log(`   ✅ Méthodes HTTP: ${Object.keys(analysis.byMethod).join(', ')}`);
      console.log(`   ✅ Catégories: ${Object.keys(analysis.byCategory).join(', ')}`);

    } catch (error) {
      console.error('   ❌ Erreur lors de l\'analyse frontend:', error);
      this.results.frontend_analysis = { error: error.message };
    }
  }

  /**
   * Teste la connectivité avec le backend
   */
  async testBackendConnectivity() {
    try {
      const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      console.log(`   Test de connectivité avec: ${baseURL}`);

      // Endpoints principaux à tester
      const mainEndpoints = [
        'GET /health/',
        'GET /events/',
        'GET /categories/',
        'GET /tags/',
        'GET /registrations/',
        'GET /admin/analytics/',
        'GET /streaming/platforms/',
        'GET /ai/info/'
      ];

      const testResults = {};

      for (const endpoint of mainEndpoints) {
        console.log(`   Test de ${endpoint}...`);
        const result = await testEndpoint(endpoint, baseURL);
        testResults[endpoint] = result;

        if (result.success) {
          console.log(`     ✅ ${endpoint} - Status: ${result.status}`);
        } else {
          console.log(`     ❌ ${endpoint} - Status: ${result.status} - Erreur: ${result.error || 'Unknown'}`);
        }
      }

      this.results.test_results = testResults;

      const successful = Object.values(testResults).filter(r => r.success).length;
      const total = Object.keys(testResults).length;

      console.log(`   ✅ ${successful}/${total} endpoints principaux accessibles`);

    } catch (error) {
      console.error('   ❌ Erreur lors du test de connectivité:', error);
      this.results.test_results = { error: error.message };
    }
  }

  /**
   * Compare avec les endpoints du backend
   */
  async compareWithBackend() {
    try {
      // Simuler les endpoints du backend (en réalité, ceci viendrait d'une API)
      const mockBackendEndpoints = [
        { pattern: 'api/events/', name: 'event-list' },
        { pattern: 'api/events/<int:pk>/', name: 'event-detail' },
        { pattern: 'api/categories/', name: 'category-list' },
        { pattern: 'api/tags/', name: 'tag-list' },
        { pattern: 'api/registrations/', name: 'registration-list' },
        { pattern: 'api/auth/token/', name: 'token_obtain_pair' },
        { pattern: 'api/auth/register/', name: 'register' },
        { pattern: 'api/admin/analytics/', name: 'admin_analytics' },
        { pattern: 'api/streaming/platforms/', name: 'list_platforms' },
        { pattern: 'api/ai/info/', name: 'ai_info' },
        { pattern: 'health/', name: 'health_check' }
      ];

      const comparison = this.analyzer.compareWithBackend(mockBackendEndpoints);
      this.results.backend_comparison = comparison;

      console.log(`   ✅ ${comparison.missingInBackend} endpoints frontend manquants dans le backend`);
      console.log(`   ✅ ${comparison.extraInBackend} endpoints backend non utilisés par le frontend`);

      if (comparison.missingInBackend > 0) {
        console.log('   ⚠️  Endpoints frontend manquants dans le backend:');
        comparison.missingInBackend.forEach(endpoint => {
          console.log(`     - ${endpoint}`);
        });
      }

    } catch (error) {
      console.error('   ❌ Erreur lors de la comparaison backend:', error);
      this.results.backend_comparison = { error: error.message };
    }
  }

  /**
   * Génère des recommandations
   */
  generateRecommendations() {
    const recommendations = [];

    // Recommandations basées sur l'analyse frontend
    if (this.results.frontend_analysis && this.results.frontend_analysis.byMethod) {
      const methods = this.results.frontend_analysis.byMethod;
      const total = this.results.frontend_analysis.total;

      if (methods.GET && methods.GET > total * 0.7) {
        recommendations.push({
          type: 'info',
          message: 'Le frontend utilise principalement des requêtes GET',
          action: 'Considérer l\'implémentation de la mise en cache pour optimiser les performances'
        });
      }

      if (methods.POST && methods.POST > total * 0.3) {
        recommendations.push({
          type: 'warning',
          message: 'Beaucoup de requêtes POST détectées',
          action: 'Vérifier que les validations côté client et serveur sont appropriées'
        });
      }
    }

    // Recommandations basées sur les tests de connectivité
    if (this.results.test_results && typeof this.results.test_results === 'object') {
      const testResults = Object.values(this.results.test_results);
      const successful = testResults.filter(r => r.success).length;
      const total = testResults.length;

      if (total > 0) {
        const successRate = (successful / total) * 100;

        if (successRate < 80) {
          recommendations.push({
            type: 'error',
            message: `Taux de succès faible: ${successRate.toFixed(1)}%`,
            action: 'Vérifier la configuration du backend et les URLs d\'API'
          });
        } else if (successRate < 95) {
          recommendations.push({
            type: 'warning',
            message: `Taux de succès moyen: ${successRate.toFixed(1)}%`,
            action: 'Investigator les endpoints en échec et corriger les problèmes'
          });
        }
      }
    }

    // Recommandations basées sur la comparaison backend
    if (this.results.backend_comparison) {
      const comparison = this.results.backend_comparison;

      if (comparison.missingInBackend > 0) {
        recommendations.push({
          type: 'warning',
          message: `${comparison.missingInBackend} endpoints frontend manquants dans le backend`,
          action: 'Implémenter les endpoints manquants côté backend ou les retirer du frontend'
        });
      }

      if (comparison.extraInBackend > 0) {
        recommendations.push({
          type: 'info',
          message: `${comparison.extraInBackend} endpoints backend non utilisés`,
          action: 'Considérer l\'ajout de ces endpoints au frontend ou leur suppression'
        });
      }
    }

    this.results.recommendations = recommendations;
    console.log(`   ✅ ${recommendations.length} recommandations générées`);
  }

  /**
   * Affiche le résumé des tests
   */
  printSummary() {
    console.log('\n' + '='.repeat(80));
    console.log('📊 RÉSUMÉ DU TEST DES ENDPOINTS FRONTEND');
    console.log('='.repeat(80));

    // Statistiques frontend
    if (this.results.frontend_analysis && this.results.frontend_analysis.total) {
      const analysis = this.results.frontend_analysis;
      console.log(`\n📋 Analyse Frontend:`);
      console.log(`   Total d'endpoints: ${analysis.total}`);
      console.log(`   Méthodes HTTP: ${Object.entries(analysis.byMethod).map(([method, count]) => `${method}(${count})`).join(', ')}`);
      console.log(`   Catégories: ${Object.entries(analysis.byCategory).map(([cat, count]) => `${cat}(${count})`).join(', ')}`);
    }

    // Résultats des tests
    if (this.results.test_results && typeof this.results.test_results === 'object') {
      const testResults = Object.values(this.results.test_results);
      const successful = testResults.filter(r => r.success).length;
      const total = testResults.length;

      console.log(`\n🧪 Tests de Connectivité:`);
      console.log(`   Endpoints testés: ${total}`);
      console.log(`   Succès: ${successful}`);
      console.log(`   Échecs: ${total - successful}`);
      console.log(`   Taux de succès: ${total > 0 ? ((successful / total) * 100).toFixed(1) : 0}%`);
    }

    // Comparaison backend
    if (this.results.backend_comparison) {
      const comparison = this.results.backend_comparison;
      console.log(`\n🔄 Comparaison Backend:`);
      console.log(`   Endpoints manquants dans le backend: ${comparison.missingInBackend || 0}`);
      console.log(`   Endpoints backend non utilisés: ${comparison.extraInBackend || 0}`);
    }

    // Recommandations
    if (this.results.recommendations && this.results.recommendations.length > 0) {
      console.log(`\n💡 Recommandations (${this.results.recommendations.length}):`);
      this.results.recommendations.forEach((rec, index) => {
        console.log(`   ${index + 1}. [${rec.type.toUpperCase()}] ${rec.message}`);
        console.log(`      Action: ${rec.action}`);
      });
    }

    console.log('='.repeat(80));
  }

  /**
   * Sauvegarde le rapport
   */
  saveReport(filename = null) {
    if (!filename) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      filename = `frontend_endpoint_test_report_${timestamp}.json`;
    }

    try {
      const fs = require('fs');
      fs.writeFileSync(filename, JSON.stringify(this.results, null, 2), 'utf8');
      console.log(`📄 Rapport sauvegardé dans: ${filename}`);
      return filename;
    } catch (error) {
      console.error('❌ Erreur lors de la sauvegarde:', error);
      return null;
    }
  }

  /**
   * Exporte les endpoints au format CSV
   */
  exportToCSV(filename = null) {
    if (!filename) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      filename = `frontend_endpoints_${timestamp}.csv`;
    }

    try {
      const csv = this.analyzer.exportToCSV();
      const fs = require('fs');
      fs.writeFileSync(filename, csv, 'utf8');
      console.log(`📄 Endpoints exportés dans: ${filename}`);
      return filename;
    } catch (error) {
      console.error('❌ Erreur lors de l\'export CSV:', error);
      return null;
    }
  }
}

/**
 * Fonction principale pour exécuter les tests
 */
async function main() {
  console.log('🔍 Testeur d\'Endpoints Frontend');
  console.log('='.repeat(80));

  const tester = new FrontendEndpointTester();
  const results = await tester.runTests();

  // Sauvegarder le rapport
  const reportFile = tester.saveReport();
  const csvFile = tester.exportToCSV();

  if (reportFile) {
    console.log(`\n📄 Rapport détaillé disponible dans: ${reportFile}`);
  }

  if (csvFile) {
    console.log(`📄 Liste des endpoints disponible dans: ${csvFile}`);
  }

  return results;
}

// Exécuter si le script est appelé directement
if (require.main === module) {
  main().catch(console.error);
}

export default FrontendEndpointTester;
export { main };
