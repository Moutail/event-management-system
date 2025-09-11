#!/usr/bin/env node

/**
 * Analyseur d'appels API pour le frontend
 * Trouve tous les appels axios/fetch dans le code et les compare avec le backend
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

class APICallAnalyzer {
  constructor() {
    this.apiCalls = new Set();
    this.axiosCalls = new Set();
    this.fetchCalls = new Set();
    this.importedAPIs = new Set();
    this.backendEndpoints = new Set();
    this.results = {
      timestamp: new Date().toISOString(),
      frontend_calls: [],
      backend_endpoints: [],
      missing_in_backend: [],
      missing_in_frontend: [],
      inconsistencies: [],
      statistics: {}
    };
  }

  /**
   * Analyse tous les fichiers JavaScript/JSX du frontend
   */
  async analyzeFrontend() {
    console.log('🔍 Analyse des appels API dans le frontend...');
    
    // Patterns de fichiers à analyser
    const patterns = [
      'src/**/*.js',
      'src/**/*.jsx',
      'src/**/*.ts',
      'src/**/*.tsx'
    ];

    for (const pattern of patterns) {
      const files = glob.sync(pattern, { cwd: process.cwd() });
      for (const file of files) {
        await this.analyzeFile(file);
      }
    }

    console.log(`✅ ${this.apiCalls.size} appels API uniques trouvés`);
    console.log(`✅ ${this.axiosCalls.size} appels axios trouvés`);
    console.log(`✅ ${this.fetchCalls.size} appels fetch trouvés`);
  }

  /**
   * Analyse un fichier spécifique
   */
  async analyzeFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      
      // Analyser les imports d'API
      this.analyzeImports(content, filePath);
      
      // Analyser les appels axios
      this.analyzeAxiosCalls(content, filePath);
      
      // Analyser les appels fetch
      this.analyzeFetchCalls(content, filePath);
      
      // Analyser les appels via api.js
      this.analyzeAPICalls(content, filePath);
      
    } catch (error) {
      console.warn(`⚠️  Erreur lors de l'analyse de ${filePath}: ${error.message}`);
    }
  }

  /**
   * Analyse les imports d'API
   */
  analyzeImports(content, filePath) {
    // Imports d'api.js
    const apiImports = content.match(/import\s+.*\s+from\s+['"][^'"]*api['"]/g) || [];
    apiImports.forEach(importLine => {
      this.importedAPIs.add({
        file: filePath,
        import: importLine.trim()
      });
    });

    // Imports d'axios
    const axiosImports = content.match(/import\s+.*\s+from\s+['"]axios['"]/g) || [];
    axiosImports.forEach(importLine => {
      this.importedAPIs.add({
        file: filePath,
        import: importLine.trim()
      });
    });
  }

  /**
   * Analyse les appels axios
   */
  analyzeAxiosCalls(content, filePath) {
    // Patterns pour les appels axios
    const patterns = [
      // axios.get('/api/...')
      /axios\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // axios({ method: 'GET', url: '/api/...' })
      /axios\s*\(\s*\{[^}]*url\s*:\s*['"`]([^'"`]+)['"`]/g,
      // api.get('/api/...')
      /api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // api({ method: 'GET', url: '/api/...' })
      /api\s*\(\s*\{[^}]*url\s*:\s*['"`]([^'"`]+)['"`]/g
    ];

    patterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        const method = match[1] || 'GET';
        const url = match[2] || match[1];
        
        if (url && url.startsWith('/api/')) {
          this.axiosCalls.add({
            file: filePath,
            method: method.toUpperCase(),
            url: url,
            line: this.getLineNumber(content, match.index)
          });
          this.apiCalls.add(url);
        }
      }
    });
  }

  /**
   * Analyse les appels fetch
   */
  analyzeFetchCalls(content, filePath) {
    // Patterns pour les appels fetch
    const patterns = [
      // fetch('/api/...')
      /fetch\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // fetch('/api/...', { method: 'POST' })
      /fetch\s*\(\s*['"`]([^'"`]+)['"`]\s*,\s*\{[^}]*method\s*:\s*['"`]([^'"`]+)['"`]/g
    ];

    patterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        const url = match[1];
        const method = match[2] || 'GET';
        
        if (url && url.startsWith('/api/')) {
          this.fetchCalls.add({
            file: filePath,
            method: method.toUpperCase(),
            url: url,
            line: this.getLineNumber(content, match.index)
          });
          this.apiCalls.add(url);
        }
      }
    });
  }

  /**
   * Analyse les appels via api.js (eventAPI, authAPI, etc.)
   */
  analyzeAPICalls(content, filePath) {
    // Patterns pour les appels d'API
    const patterns = [
      // eventAPI.getEvents()
      /(\w+API)\.(\w+)\s*\(/g,
      // authAPI.login(credentials)
      /(\w+API)\.(\w+)\s*\([^)]*\)/g
    ];

    patterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        const apiName = match[1];
        const methodName = match[2];
        
        this.importedAPIs.add({
          file: filePath,
          api: apiName,
          method: methodName,
          line: this.getLineNumber(content, match.index)
        });
      }
    });
  }

  /**
   * Obtient le numéro de ligne d'une position dans le contenu
   */
  getLineNumber(content, position) {
    return content.substring(0, position).split('\n').length;
  }

  /**
   * Charge les endpoints du backend
   */
  async loadBackendEndpoints() {
    console.log('🔍 Chargement des endpoints du backend...');
    
    try {
      // Essayer de charger depuis un fichier de rapport backend
      const reportFiles = glob.sync('**/endpoint_test_report_*.json', { cwd: process.cwd() });
      
      if (reportFiles.length > 0) {
        const latestReport = reportFiles.sort().pop();
        const reportContent = fs.readFileSync(latestReport, 'utf8');
        const report = JSON.parse(reportContent);
        
        if (report.backend_analysis && report.backend_analysis.results) {
          report.backend_analysis.results.forEach(result => {
            if (result.success) {
              this.backendEndpoints.add(result.url);
            }
          });
        }
      }
    } catch (error) {
      console.warn('⚠️  Impossible de charger les endpoints du backend, utilisation des endpoints par défaut');
    }

    // Endpoints par défaut basés sur l'analyse précédente
    const defaultEndpoints = [
      '/api/events/',
      '/api/events/{id}/',
      '/api/categories/',
      '/api/tags/',
      '/api/registrations/',
      '/api/history/',
      '/api/auth/token/',
      '/api/auth/register/',
      '/api/auth/user/',
      '/api/admin/analytics/',
      '/api/admin/moderation/',
      '/api/streaming/platforms/',
      '/api/ai/info/',
      '/health/'
    ];

    defaultEndpoints.forEach(endpoint => {
      this.backendEndpoints.add(endpoint);
    });

    console.log(`✅ ${this.backendEndpoints.size} endpoints backend chargés`);
  }

  /**
   * Compare les appels frontend avec les endpoints backend
   */
  compareWithBackend() {
    console.log('🔄 Comparaison frontend-backend...');
    
    const frontendUrls = Array.from(this.apiCalls);
    const backendUrls = Array.from(this.backendEndpoints);
    
    // URLs du frontend manquantes dans le backend
    const missingInBackend = frontendUrls.filter(frontendUrl => {
      return !backendUrls.some(backendUrl => this.urlsMatch(frontendUrl, backendUrl));
    });
    
    // URLs du backend non utilisées par le frontend
    const missingInFrontend = backendUrls.filter(backendUrl => {
      return !frontendUrls.some(frontendUrl => this.urlsMatch(frontendUrl, backendUrl));
    });
    
    this.results.missing_in_backend = missingInBackend;
    this.results.missing_in_frontend = missingInFrontend;
    
    console.log(`✅ ${missingInBackend.length} URLs frontend manquantes dans le backend`);
    console.log(`✅ ${missingInFrontend.length} URLs backend non utilisées par le frontend`);
  }

  /**
   * Vérifie si deux URLs correspondent (en tenant compte des paramètres)
   */
  urlsMatch(frontendUrl, backendUrl) {
    // Normaliser les URLs
    const normalizeUrl = (url) => {
      return url
        .replace(/\{([^}]+)\}/g, '<\\w+:[^>]+>')
        .replace(/\{id\}/g, '<int:pk>')
        .replace(/\{event_id\}/g, '<int:event_id>')
        .replace(/\{registration_id\}/g, '<int:registration_id>')
        .replace(/\{refund_id\}/g, '<int:refund_id>')
        .replace(/\{platform\}/g, '<str:platform>')
        .replace(/\{format\}/g, '<str:format>');
    };
    
    const normalizedFrontend = normalizeUrl(frontendUrl);
    const normalizedBackend = normalizeUrl(backendUrl);
    
    return normalizedFrontend === normalizedBackend;
  }

  /**
   * Génère les statistiques
   */
  generateStatistics() {
    this.results.statistics = {
      total_api_calls: this.apiCalls.size,
      axios_calls: this.axiosCalls.size,
      fetch_calls: this.fetchCalls.size,
      imported_apis: this.importedAPIs.size,
      backend_endpoints: this.backendEndpoints.size,
      missing_in_backend: this.results.missing_in_backend.length,
      missing_in_frontend: this.results.missing_in_frontend.length,
      coverage_percentage: this.calculateCoverage()
    };
  }

  /**
   * Calcule le pourcentage de couverture
   */
  calculateCoverage() {
    const frontendUrls = Array.from(this.apiCalls);
    const backendUrls = Array.from(this.backendEndpoints);
    
    const matchedUrls = frontendUrls.filter(frontendUrl => {
      return backendUrls.some(backendUrl => this.urlsMatch(frontendUrl, backendUrl));
    });
    
    return frontendUrls.length > 0 ? (matchedUrls.length / frontendUrls.length * 100).toFixed(2) : 0;
  }

  /**
   * Génère le rapport final
   */
  generateReport() {
    console.log('📊 Génération du rapport...');
    
    // Convertir les Sets en Arrays pour le JSON
    this.results.frontend_calls = Array.from(this.apiCalls).map(url => {
      const axiosCall = Array.from(this.axiosCalls).find(call => call.url === url);
      const fetchCall = Array.from(this.fetchCalls).find(call => call.url === url);
      
      return {
        url: url,
        method: axiosCall?.method || fetchCall?.method || 'GET',
        source: axiosCall ? 'axios' : 'fetch',
        files: [
          ...Array.from(this.axiosCalls).filter(call => call.url === url).map(call => ({
            file: call.file,
            line: call.line
          })),
          ...Array.from(this.fetchCalls).filter(call => call.url === url).map(call => ({
            file: call.file,
            line: call.line
          }))
        ]
      };
    });
    
    this.results.backend_endpoints = Array.from(this.backendEndpoints);
    
    // Générer des recommandations
    this.generateRecommendations();
    
    console.log('✅ Rapport généré');
  }

  /**
   * Génère des recommandations
   */
  generateRecommendations() {
    const recommendations = [];
    
    if (this.results.missing_in_backend.length > 0) {
      recommendations.push({
        type: 'warning',
        message: `${this.results.missing_in_backend.length} URLs frontend manquantes dans le backend`,
        action: 'Vérifier que ces endpoints sont implémentés côté backend',
        urls: this.results.missing_in_backend
      });
    }
    
    if (this.results.missing_in_frontend.length > 0) {
      recommendations.push({
        type: 'info',
        message: `${this.results.missing_in_frontend.length} URLs backend non utilisées par le frontend`,
        action: 'Considérer l\'ajout de ces endpoints au frontend ou leur suppression',
        urls: this.results.missing_in_frontend
      });
    }
    
    const coverage = parseFloat(this.results.statistics.coverage_percentage);
    if (coverage < 80) {
      recommendations.push({
        type: 'warning',
        message: `Couverture faible: ${coverage}%`,
        action: 'Améliorer la correspondance entre frontend et backend'
      });
    }
    
    this.results.recommendations = recommendations;
  }

  /**
   * Affiche le résumé
   */
  printSummary() {
    console.log('\n' + '='.repeat(80));
    console.log('📊 RÉSUMÉ DE L\'ANALYSE DES APPELS API');
    console.log('='.repeat(80));
    
    console.log(`\n📋 Statistiques Frontend:`);
    console.log(`   Total d'appels API: ${this.results.statistics.total_api_calls}`);
    console.log(`   Appels axios: ${this.results.statistics.axios_calls}`);
    console.log(`   Appels fetch: ${this.results.statistics.fetch_calls}`);
    console.log(`   APIs importées: ${this.results.statistics.imported_apis}`);
    
    console.log(`\n🔄 Comparaison Backend:`);
    console.log(`   Endpoints backend: ${this.results.statistics.backend_endpoints}`);
    console.log(`   URLs manquantes dans le backend: ${this.results.statistics.missing_in_backend}`);
    console.log(`   URLs backend non utilisées: ${this.results.statistics.missing_in_frontend}`);
    console.log(`   Couverture: ${this.results.statistics.coverage_percentage}%`);
    
    if (this.results.recommendations.length > 0) {
      console.log(`\n💡 Recommandations (${this.results.recommendations.length}):`);
      this.results.recommendations.forEach((rec, index) => {
        console.log(`   ${index + 1}. [${rec.type.toUpperCase()}] ${rec.message}`);
        console.log(`      Action: ${rec.action}`);
        if (rec.urls && rec.urls.length > 0) {
          console.log(`      URLs: ${rec.urls.slice(0, 3).join(', ')}${rec.urls.length > 3 ? '...' : ''}`);
        }
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
      filename = `api_calls_analysis_${timestamp}.json`;
    }
    
    try {
      fs.writeFileSync(filename, JSON.stringify(this.results, null, 2), 'utf8');
      console.log(`📄 Rapport sauvegardé dans: ${filename}`);
      return filename;
    } catch (error) {
      console.error('❌ Erreur lors de la sauvegarde:', error);
      return null;
    }
  }

  /**
   * Exporte en CSV
   */
  exportToCSV(filename = null) {
    if (!filename) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      filename = `api_calls_${timestamp}.csv`;
    }
    
    try {
      const csvContent = [
        'URL,Method,Source,Files',
        ...this.results.frontend_calls.map(call => 
          `${call.url},${call.method},${call.source},"${call.files.map(f => f.file).join('; ')}"`
        )
      ].join('\n');
      
      fs.writeFileSync(filename, csvContent, 'utf8');
      console.log(`📄 Appels API exportés dans: ${filename}`);
      return filename;
    } catch (error) {
      console.error('❌ Erreur lors de l\'export CSV:', error);
      return null;
    }
  }

  /**
   * Exécute l'analyse complète
   */
  async run() {
    console.log('🚀 Démarrage de l\'analyse des appels API...');
    console.log('='.repeat(80));
    
    await this.analyzeFrontend();
    await this.loadBackendEndpoints();
    this.compareWithBackend();
    this.generateStatistics();
    this.generateReport();
    this.printSummary();
    
    const reportFile = this.saveReport();
    const csvFile = this.exportToCSV();
    
    if (reportFile) {
      console.log(`\n📄 Rapport détaillé disponible dans: ${reportFile}`);
    }
    
    if (csvFile) {
      console.log(`📄 Liste des appels API disponible dans: ${csvFile}`);
    }
    
    return this.results;
  }
}

/**
 * Fonction principale
 */
async function main() {
  const analyzer = new APICallAnalyzer();
  const results = await analyzer.run();
  return results;
}

// Exécuter si le script est appelé directement
if (require.main === module) {
  main().catch(console.error);
}

module.exports = APICallAnalyzer;
