#!/usr/bin/env node

/**
 * Script amélioré pour trouver tous les appels API dans le frontend
 * Version qui analyse aussi les définitions d'API dans api.js
 */

const fs = require('fs');
const path = require('path');

class EnhancedAPIFinder {
  constructor() {
    this.apiCalls = new Map();
    this.apiDefinitions = new Map();
    this.results = {
      timestamp: new Date().toISOString(),
      total_calls: 0,
      unique_urls: 0,
      calls: [],
      definitions: [],
      by_method: {},
      by_file: {},
      summary: {}
    };
  }

  /**
   * Trouve tous les fichiers JavaScript/JSX de manière récursive
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
   * Analyse un fichier pour trouver les appels API
   */
  analyzeFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      
      // Analyser les définitions d'API dans api.js
      if (filePath.includes('api.js')) {
        this.analyzeAPIDefinitions(content, filePath);
      }
      
      // Analyser chaque ligne
      lines.forEach((line, index) => {
        this.analyzeLine(line, filePath, index + 1);
      });
      
    } catch (error) {
      console.warn(`⚠️  Erreur lors de l'analyse de ${filePath}: ${error.message}`);
    }
  }

  /**
   * Analyse les définitions d'API dans api.js
   */
  analyzeAPIDefinitions(content, filePath) {
    // Patterns pour les définitions d'API
    const patterns = [
      // getEvents: () => api.get('/events/')
      /(\w+):\s*\([^)]*\)\s*=>\s*api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // getEvents: (params = {}) => api.get('/events/', { params })
      /(\w+):\s*\([^)]*\)\s*=>\s*api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // createEvent: (eventData) => { ... api.post('/events/', ...) }
      /(\w+):\s*\([^)]*\)\s*=>\s*\{[^}]*api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g
    ];

    patterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(content)) !== null) {
        const methodName = match[1];
        const method = match[2];
        const url = match[3];
        
        if (url && url.startsWith('/api/')) {
          this.apiDefinitions.set(methodName, {
            method: method.toUpperCase(),
            url: url,
            file: filePath
          });
        }
      }
    });

    // Analyser les définitions d'API plus complexes
    this.analyzeComplexAPIDefinitions(content, filePath);
  }

  /**
   * Analyse les définitions d'API complexes
   */
  analyzeComplexAPIDefinitions(content, filePath) {
    // Chercher les objets d'API (eventAPI, authAPI, etc.)
    const apiObjects = content.match(/export\s+const\s+(\w+API)\s*=\s*\{[^}]+\}/g);
    
    if (apiObjects) {
      apiObjects.forEach(apiObject => {
        const apiName = apiObject.match(/export\s+const\s+(\w+API)/)[1];
        
        // Extraire les méthodes de cet objet API
        const methods = apiObject.match(/(\w+):\s*\([^)]*\)\s*=>[^,}]+/g);
        
        if (methods) {
          methods.forEach(method => {
            const methodName = method.match(/(\w+):/)[1];
            
            // Chercher l'URL dans la méthode
            const urlMatch = method.match(/['"`]([^'"`]*\/api\/[^'"`]*)['"`]/);
            if (urlMatch) {
              const url = urlMatch[1];
              const methodType = this.extractMethodType(method);
              
              this.apiDefinitions.set(`${apiName}.${methodName}`, {
                method: methodType,
                url: url,
                file: filePath,
                api: apiName
              });
            }
          });
        }
      });
    }
  }

  /**
   * Extrait le type de méthode HTTP d'une définition
   */
  extractMethodType(method) {
    if (method.includes('api.get')) return 'GET';
    if (method.includes('api.post')) return 'POST';
    if (method.includes('api.put')) return 'PUT';
    if (method.includes('api.patch')) return 'PATCH';
    if (method.includes('api.delete')) return 'DELETE';
    return 'GET';
  }

  /**
   * Analyse une ligne de code
   */
  analyzeLine(line, filePath, lineNumber) {
    // Ignorer les commentaires
    if (line.trim().startsWith('//') || line.trim().startsWith('/*')) {
      return;
    }

    // Patterns pour trouver les appels API
    const patterns = [
      // axios.get('/api/...')
      /axios\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // api.get('/api/...')
      /api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // fetch('/api/...')
      /fetch\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // fetch('/api/...', { method: 'POST' })
      /fetch\s*\(\s*['"`]([^'"`]+)['"`]\s*,\s*\{[^}]*method\s*:\s*['"`]([^'"`]+)['"`]/g,
      // axios({ method: 'GET', url: '/api/...' })
      /axios\s*\(\s*\{[^}]*url\s*:\s*['"`]([^'"`]+)['"`]/g,
      // api({ method: 'GET', url: '/api/...' })
      /api\s*\(\s*\{[^}]*url\s*:\s*['"`]([^'"`]+)['"`]/g,
      // eventAPI.getEvents()
      /(\w+API)\.(\w+)\s*\(/g
    ];

    patterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(line)) !== null) {
        if (pattern.source.includes('API')) {
          // C'est un appel d'API (eventAPI.getEvents())
          const apiName = match[1];
          const methodName = match[2];
          const key = `${apiName}.${methodName}`;
          
          if (this.apiDefinitions.has(key)) {
            const definition = this.apiDefinitions.get(key);
            this.addAPICall(definition.url, definition.method, filePath, lineNumber, line.trim(), 'api_call');
          }
        } else {
          // C'est un appel direct
          const method = match[1] || 'GET';
          const url = match[2] || match[1];
          
          if (url && (url.startsWith('/api/') || url.startsWith('api/'))) {
            const normalizedUrl = url.startsWith('api/') ? `/${url}` : url;
            const normalizedMethod = method.toUpperCase();
            
            this.addAPICall(normalizedUrl, normalizedMethod, filePath, lineNumber, line.trim(), 'direct_call');
          }
        }
      }
    });
  }

  /**
   * Ajoute un appel API à la collection
   */
  addAPICall(url, method, filePath, lineNumber, code, type) {
    const key = `${method}:${url}`;
    
    if (!this.apiCalls.has(key)) {
      this.apiCalls.set(key, {
        url: url,
        method: method,
        count: 0,
        type: type,
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
    this.results.unique_urls = this.apiCalls.size;
    
    // Convertir en array et calculer le total
    this.results.calls = Array.from(this.apiCalls.values()).map(call => {
      this.results.total_calls += call.count;
      return call;
    });
    
    // Ajouter les définitions d'API
    this.results.definitions = Array.from(this.apiDefinitions.values());
    
    // Statistiques par méthode
    this.results.by_method = {};
    this.results.calls.forEach(call => {
      if (!this.results.by_method[call.method]) {
        this.results.by_method[call.method] = 0;
      }
      this.results.by_method[call.method] += call.count;
    });
    
    // Statistiques par fichier
    this.results.by_file = {};
    this.results.calls.forEach(call => {
      call.files.forEach(file => {
        if (!this.results.by_file[file.file]) {
          this.results.by_file[file.file] = 0;
        }
        this.results.by_file[file.file]++;
      });
    });
    
    // Résumé
    this.results.summary = {
      total_files_analyzed: this.findJSFiles().length,
      total_api_calls: this.results.total_calls,
      unique_endpoints: this.results.unique_urls,
      api_definitions: this.apiDefinitions.size,
      most_used_method: this.getMostUsedMethod(),
      most_used_file: this.getMostUsedFile()
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
   * Trouve le fichier le plus utilisé
   */
  getMostUsedFile() {
    let maxCount = 0;
    let mostUsed = '';
    
    Object.entries(this.results.by_file).forEach(([file, count]) => {
      if (count > maxCount) {
        maxCount = count;
        mostUsed = file;
      }
    });
    
    return mostUsed;
  }

  /**
   * Affiche le résumé
   */
  printSummary() {
    console.log('\n' + '='.repeat(80));
    console.log('📊 RÉSUMÉ DE L\'ANALYSE DES APPELS API');
    console.log('='.repeat(80));
    
    console.log(`\n📋 Statistiques Générales:`);
    console.log(`   Fichiers analysés: ${this.results.summary.total_files_analyzed}`);
    console.log(`   Total d'appels API: ${this.results.summary.total_api_calls}`);
    console.log(`   Endpoints uniques: ${this.results.summary.unique_endpoints}`);
    console.log(`   Définitions d'API: ${this.results.summary.api_definitions}`);
    
    console.log(`\n📊 Méthodes HTTP:`);
    Object.entries(this.results.by_method)
      .sort(([,a], [,b]) => b - a)
      .forEach(([method, count]) => {
        console.log(`   ${method}: ${count} appels`);
      });
    
    console.log(`\n📁 Fichiers les plus actifs:`);
    Object.entries(this.results.by_file)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10)
      .forEach(([file, count]) => {
        console.log(`   ${file}: ${count} appels`);
      });
    
    console.log(`\n🎯 Endpoints les plus utilisés:`);
    this.results.calls
      .sort((a, b) => b.count - a.count)
      .slice(0, 15)
      .forEach(call => {
        console.log(`   ${call.method} ${call.url} (${call.count} fois)`);
      });
    
    console.log(`\n🔧 Définitions d'API trouvées:`);
    this.results.definitions
      .slice(0, 10)
      .forEach(def => {
        console.log(`   ${def.method} ${def.url}`);
      });
    
    console.log('='.repeat(80));
  }

  /**
   * Affiche les détails des appels
   */
  printDetails() {
    console.log('\n📋 DÉTAILS DES APPELS API:');
    console.log('='.repeat(80));
    
    this.results.calls
      .sort((a, b) => b.count - a.count)
      .forEach(call => {
        console.log(`\n${call.method} ${call.url} (${call.count} fois) - ${call.type}`);
        call.files.forEach(file => {
          console.log(`  📁 ${file.file}:${file.line}`);
          console.log(`     ${file.code}`);
        });
      });
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
        'URL,Method,Type,Count,Files',
        ...this.results.calls.map(call => 
          `${call.url},${call.method},${call.type},${call.count},"${call.files.map(f => f.file).join('; ')}"`
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
   * Exécute l'analyse
   */
  run(showDetails = false) {
    console.log('🚀 Démarrage de l\'analyse des appels API...');
    console.log('='.repeat(80));
    
    const files = this.findJSFiles();
    console.log(`📁 ${files.length} fichiers JavaScript/JSX trouvés`);
    
    files.forEach(file => {
      this.analyzeFile(file);
    });
    
    this.generateStatistics();
    this.printSummary();
    
    if (showDetails) {
      this.printDetails();
    }
    
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
function main() {
  const args = process.argv.slice(2);
  const showDetails = args.includes('--details') || args.includes('-d');
  
  const finder = new EnhancedAPIFinder();
  const results = finder.run(showDetails);
  return results;
}

// Exécuter si le script est appelé directement
if (require.main === module) {
  main();
}

module.exports = EnhancedAPIFinder;
