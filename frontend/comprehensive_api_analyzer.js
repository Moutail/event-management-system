#!/usr/bin/env node

/**
 * Analyseur complet des appels API
 * Version qui utilise une approche différente pour extraire les informations
 */

const fs = require('fs');
const path = require('path');

class ComprehensiveAPIAnalyzer {
  constructor() {
    this.apiDefinitions = new Map();
    this.apiCalls = new Map();
    this.results = {
      timestamp: new Date().toISOString(),
      total_definitions: 0,
      total_calls: 0,
      definitions: [],
      calls: [],
      by_method: {},
      by_file: {},
      summary: {}
    };
  }

  /**
   * Trouve tous les fichiers JavaScript/JSX
   */
  findJSFiles(dir = 'src') {
    const files = [];
    
    try {
      const items = fs.readdirSync(dir);
      
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          files.push(...this.findJSFiles(fullPath));
        } else if (item.match(/\.(js|jsx|ts|tsx)$/)) {
          files.push(fullPath);
        }
      }
    } catch (error) {
      // Ignorer les erreurs de lecture de répertoire
    }
    
    return files;
  }

  /**
   * Analyse un fichier
   */
  analyzeFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      
      if (filePath.includes('api.js')) {
        this.analyzeAPIDefinitions(content, filePath);
      } else {
        this.analyzeAPICalls(content, filePath);
      }
      
    } catch (error) {
      console.warn(`⚠️  Erreur lors de l'analyse de ${filePath}: ${error.message}`);
    }
  }

  /**
   * Analyse les définitions d'API dans api.js
   */
  analyzeAPIDefinitions(content, filePath) {
    const lines = content.split('\n');
    
    lines.forEach((line, index) => {
      // Chercher les définitions d'API
      if (line.includes('api.') && (line.includes('get(') || line.includes('post(') || line.includes('put(') || line.includes('patch(') || line.includes('delete('))) {
        this.extractAPIDefinition(line, filePath, index + 1);
      }
    });
  }

  /**
   * Extrait une définition d'API
   */
  extractAPIDefinition(line, filePath, lineNumber) {
    // Chercher les patterns d'API
    const patterns = [
      // getEvents: (params = {}) => api.get('/events/', { params }),
      /(\w+):\s*\([^)]*\)\s*=>\s*api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // getEventById: (id) => api.get(`/events/${id}/`),
      /(\w+):\s*\([^)]*\)\s*=>\s*api\.(get|post|put|patch|delete)\s*\(\s*`([^`]+)`/g,
      // refreshToken: (refresh) => api.post('/auth/token/refresh/', { refresh }),
      /(\w+):\s*\([^)]*\)\s*=>\s*api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g
    ];

    patterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(line)) !== null) {
        const methodName = match[1];
        const method = match[2];
        const url = match[3];
        
        if (url && url.startsWith('/api/')) {
          this.apiDefinitions.set(methodName, {
            method: method.toUpperCase(),
            url: url,
            file: filePath,
            line: lineNumber,
            code: line.trim()
          });
        }
      }
    });
  }

  /**
   * Analyse les appels d'API dans les autres fichiers
   */
  analyzeAPICalls(content, filePath) {
    const lines = content.split('\n');
    
    lines.forEach((line, index) => {
      // Ignorer les commentaires
      if (line.trim().startsWith('//') || line.trim().startsWith('/*')) {
        return;
      }

      // Chercher les appels d'API
      this.findAPICalls(line, filePath, index + 1);
    });
  }

  /**
   * Trouve les appels d'API
   */
  findAPICalls(line, filePath, lineNumber) {
    // Patterns pour les appels d'API
    const patterns = [
      // axios.get('/api/...')
      /axios\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // api.get('/api/...')
      /api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // fetch('/api/...')
      /fetch\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // fetch('/api/...', { method: 'POST' })
      /fetch\s*\(\s*['"`]([^'"`]+)['"`]\s*,\s*\{[^}]*method\s*:\s*['"`]([^'"`]+)['"`]/g,
      // Template literals avec variables
      /api\.(get|post|put|patch|delete)\s*\(\s*`([^`]*\/api\/[^`]*)`/g,
      // Appels avec variables dans l'URL
      /api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]*\/api\/[^'"`]*)['"`]/g
    ];

    patterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(line)) !== null) {
        const method = match[1] || 'GET';
        const url = match[2] || match[1];
        
        if (url && (url.startsWith('/api/') || url.startsWith('api/'))) {
          const normalizedUrl = url.startsWith('api/') ? `/${url}` : url;
          const normalizedMethod = method.toUpperCase();
          
          this.addAPICall(normalizedUrl, normalizedMethod, filePath, lineNumber, line.trim());
        }
      }
    });
  }

  /**
   * Ajoute un appel API
   */
  addAPICall(url, method, filePath, lineNumber, code) {
    const key = `${method}:${url}`;
    
    if (!this.apiCalls.has(key)) {
      this.apiCalls.set(key, {
        url: url,
        method: method,
        count: 0,
        files: []
      });
    }
    
    const apiCall = this.apiCalls.get(key);
    apiCall.count++;
    apiCall.files.push({
      file: filePath,
      line: lineNumber,
      code: code
    });
  }

  /**
   * Génère les statistiques
   */
  generateStatistics() {
    this.results.total_definitions = this.apiDefinitions.size;
    this.results.total_calls = Array.from(this.apiCalls.values()).reduce((sum, call) => sum + call.count, 0);
    
    // Convertir en arrays
    this.results.definitions = Array.from(this.apiDefinitions.values());
    this.results.calls = Array.from(this.apiCalls.values());
    
    // Statistiques par méthode
    this.results.by_method = {};
    [...this.results.definitions, ...this.results.calls].forEach(item => {
      const method = item.method;
      if (!this.results.by_method[method]) {
        this.results.by_method[method] = 0;
      }
      this.results.by_method[method]++;
    });
    
    // Résumé
    this.results.summary = {
      total_files_analyzed: this.findJSFiles().length,
      total_definitions: this.results.total_definitions,
      total_calls: this.results.total_calls,
      unique_endpoints: this.results.calls.length,
      most_used_method: this.getMostUsedMethod()
    };
  }

  /**
   * Trouve la méthode la plus utilisée
   */
  getMostUsedMethod() {
    let maxCount = 0;
    let mostUsed = 'GET';
    
    Object.entries(this.results.by_method).forEach(([method, count]) => {
      if (count > maxCount) {
        maxCount = count;
        mostUsed = method;
      }
    });
    
    return mostUsed;
  }

  /**
   * Affiche le résumé
   */
  printSummary() {
    console.log('\n' + '='.repeat(80));
    console.log('📊 RÉSUMÉ DE L\'ANALYSE COMPLÈTE DES APPELS API');
    console.log('='.repeat(80));
    
    console.log(`\n📋 Statistiques Générales:`);
    console.log(`   Fichiers analysés: ${this.results.summary.total_files_analyzed}`);
    console.log(`   Définitions d'API: ${this.results.summary.total_definitions}`);
    console.log(`   Appels d'API: ${this.results.summary.total_calls}`);
    console.log(`   Endpoints uniques: ${this.results.summary.unique_endpoints}`);
    
    console.log(`\n📊 Méthodes HTTP:`);
    Object.entries(this.results.by_method)
      .sort(([,a], [,b]) => b - a)
      .forEach(([method, count]) => {
        console.log(`   ${method}: ${count}`);
      });
    
    console.log(`\n🔧 Définitions d'API trouvées:`);
    this.results.definitions
      .sort((a, b) => a.method.localeCompare(b.method))
      .forEach(def => {
        console.log(`   ${def.method} ${def.url}`);
        console.log(`      Ligne ${def.line}: ${def.code.split('=>')[0].trim()}`);
      });
    
    console.log(`\n🎯 Appels d'API trouvés:`);
    this.results.calls
      .sort((a, b) => b.count - a.count)
      .forEach(call => {
        console.log(`   ${call.method} ${call.url} (${call.count} fois)`);
      });
    
    console.log('='.repeat(80));
  }

  /**
   * Sauvegarde le rapport
   */
  saveReport(filename = null) {
    if (!filename) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      filename = `comprehensive_api_analysis_${timestamp}.json`;
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
      filename = `comprehensive_api_${timestamp}.csv`;
    }
    
    try {
      const csvContent = [
        'Type,Method,URL,Count,Files',
        ...this.results.definitions.map(def => 
          `definition,${def.method},${def.url},1,"${def.file}:${def.line}"`
        ),
        ...this.results.calls.map(call => 
          `call,${call.method},${call.url},${call.count},"${call.files.map(f => f.file).join('; ')}"`
        )
      ].join('\n');
      
      fs.writeFileSync(filename, csvContent, 'utf8');
      console.log(`📄 Analyse exportée dans: ${filename}`);
      return filename;
    } catch (error) {
      console.error('❌ Erreur lors de l\'export CSV:', error);
      return null;
    }
  }

  /**
   * Exécute l'analyse
   */
  run() {
    console.log('🚀 Démarrage de l\'analyse complète des appels API...');
    console.log('='.repeat(80));
    
    const files = this.findJSFiles();
    console.log(`📁 ${files.length} fichiers JavaScript/JSX trouvés`);
    
    files.forEach(file => {
      this.analyzeFile(file);
    });
    
    this.generateStatistics();
    this.printSummary();
    
    const reportFile = this.saveReport();
    const csvFile = this.exportToCSV();
    
    if (reportFile) {
      console.log(`\n📄 Rapport détaillé disponible dans: ${reportFile}`);
    }
    
    if (csvFile) {
      console.log(`📄 Analyse exportée dans: ${csvFile}`);
    }
    
    return this.results;
  }
}

/**
 * Fonction principale
 */
function main() {
  const analyzer = new ComprehensiveAPIAnalyzer();
  const results = analyzer.run();
  return results;
}

// Exécuter si le script est appelé directement
if (require.main === module) {
  main();
}

module.exports = ComprehensiveAPIAnalyzer;
