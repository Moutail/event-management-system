#!/usr/bin/env node

/**
 * Script simple pour trouver tous les appels API dans le frontend
 * Utilise des expressions régulières pour analyser le code source
 */

const fs = require('fs');
const path = require('path');
const glob = require('glob');

class SimpleAPIFinder {
  constructor() {
    this.apiCalls = new Map();
    this.axiosCalls = [];
    this.fetchCalls = [];
    this.imports = [];
    this.results = {
      timestamp: new Date().toISOString(),
      total_calls: 0,
      unique_urls: 0,
      by_method: {},
      by_file: {},
      calls: [],
      imports: [],
      summary: {}
    };
  }

  /**
   * Trouve tous les fichiers JavaScript/JSX
   */
  findJSFiles() {
    const patterns = [
      'src/**/*.js',
      'src/**/*.jsx',
      'src/**/*.ts',
      'src/**/*.tsx'
    ];

    let files = [];
    patterns.forEach(pattern => {
      files = files.concat(glob.sync(pattern, { cwd: process.cwd() }));
    });

    return files;
  }

  /**
   * Analyse un fichier pour trouver les appels API
   */
  analyzeFile(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      
      // Analyser chaque ligne
      lines.forEach((line, index) => {
        this.analyzeLine(line, filePath, index + 1);
      });
      
    } catch (error) {
      console.warn(`⚠️  Erreur lors de l'analyse de ${filePath}: ${error.message}`);
    }
  }

  /**
   * Analyse une ligne de code
   */
  analyzeLine(line, filePath, lineNumber) {
    // Ignorer les commentaires
    if (line.trim().startsWith('//') || line.trim().startsWith('/*')) {
      return;
    }

    // Trouver les imports
    this.findImports(line, filePath, lineNumber);
    
    // Trouver les appels axios
    this.findAxiosCalls(line, filePath, lineNumber);
    
    // Trouver les appels fetch
    this.findFetchCalls(line, filePath, lineNumber);
    
    // Trouver les appels d'API (eventAPI, authAPI, etc.)
    this.findAPICalls(line, filePath, lineNumber);
  }

  /**
   * Trouve les imports d'API
   */
  findImports(line, filePath, lineNumber) {
    const importPatterns = [
      /import\s+.*\s+from\s+['"][^'"]*api['"]/g,
      /import\s+.*\s+from\s+['"]axios['"]/g,
      /import\s+.*\s+from\s+['"]\.\/services\/api['"]/g
    ];

    importPatterns.forEach(pattern => {
      const matches = line.match(pattern);
      if (matches) {
        matches.forEach(match => {
          this.imports.push({
            file: filePath,
            line: lineNumber,
            import: match.trim()
          });
        });
      }
    });
  }

  /**
   * Trouve les appels axios
   */
  findAxiosCalls(line, filePath, lineNumber) {
    const axiosPatterns = [
      // axios.get('/api/...')
      /axios\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // api.get('/api/...')
      /api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // axios({ method: 'GET', url: '/api/...' })
      /axios\s*\(\s*\{[^}]*url\s*:\s*['"`]([^'"`]+)['"`]/g,
      // api({ method: 'GET', url: '/api/...' })
      /api\s*\(\s*\{[^}]*url\s*:\s*['"`]([^'"`]+)['"`]/g
    ];

    axiosPatterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(line)) !== null) {
        const method = match[1] || 'GET';
        const url = match[2] || match[1];
        
        if (url && (url.startsWith('/api/') || url.startsWith('api/'))) {
          const normalizedUrl = url.startsWith('api/') ? `/${url}` : url;
          
          this.axiosCalls.push({
            file: filePath,
            line: lineNumber,
            method: method.toUpperCase(),
            url: normalizedUrl,
            code: line.trim()
          });
          
          this.addAPICall(normalizedUrl, method.toUpperCase(), filePath, lineNumber, 'axios');
        }
      }
    });
  }

  /**
   * Trouve les appels fetch
   */
  findFetchCalls(line, filePath, lineNumber) {
    const fetchPatterns = [
      // fetch('/api/...')
      /fetch\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // fetch('/api/...', { method: 'POST' })
      /fetch\s*\(\s*['"`]([^'"`]+)['"`]\s*,\s*\{[^}]*method\s*:\s*['"`]([^'"`]+)['"`]/g
    ];

    fetchPatterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(line)) !== null) {
        const url = match[1];
        const method = match[2] || 'GET';
        
        if (url && (url.startsWith('/api/') || url.startsWith('api/'))) {
          const normalizedUrl = url.startsWith('api/') ? `/${url}` : url;
          
          this.fetchCalls.push({
            file: filePath,
            line: lineNumber,
            method: method.toUpperCase(),
            url: normalizedUrl,
            code: line.trim()
          });
          
          this.addAPICall(normalizedUrl, method.toUpperCase(), filePath, lineNumber, 'fetch');
        }
      }
    });
  }

  /**
   * Trouve les appels d'API (eventAPI, authAPI, etc.)
   */
  findAPICalls(line, filePath, lineNumber) {
    const apiPatterns = [
      // eventAPI.getEvents()
      /(\w+API)\.(\w+)\s*\(/g,
      // authAPI.login(credentials)
      /(\w+API)\.(\w+)\s*\([^)]*\)/g
    ];

    apiPatterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(line)) !== null) {
        const apiName = match[1];
        const methodName = match[2];
        
        this.addAPICall(`${apiName}.${methodName}`, 'API', filePath, lineNumber, 'api');
      }
    });
  }

  /**
   * Ajoute un appel API à la collection
   */
  addAPICall(url, method, filePath, lineNumber, type) {
    const key = `${method}:${url}`;
    
    if (!this.apiCalls.has(key)) {
      this.apiCalls.set(key, {
        url: url,
        method: method,
        type: type,
        count: 0,
        files: []
      });
    }
    
    const apiCall = this.apiCalls.get(key);
    apiCall.count++;
    apiCall.files.push({
      file: filePath,
      line: lineNumber
    });
  }

  /**
   * Génère les statistiques
   */
  generateStatistics() {
    this.results.total_calls = this.axiosCalls.length + this.fetchCalls.length;
    this.results.unique_urls = this.apiCalls.size;
    
    // Statistiques par méthode
    this.results.by_method = {};
    Array.from(this.apiCalls.values()).forEach(call => {
      if (!this.results.by_method[call.method]) {
        this.results.by_method[call.method] = 0;
      }
      this.results.by_method[call.method]++;
    });
    
    // Statistiques par fichier
    this.results.by_file = {};
    [...this.axiosCalls, ...this.fetchCalls].forEach(call => {
      if (!this.results.by_file[call.file]) {
        this.results.by_file[call.file] = 0;
      }
      this.results.by_file[call.file]++;
    });
    
    // Liste des appels
    this.results.calls = Array.from(this.apiCalls.values()).map(call => ({
      url: call.url,
      method: call.method,
      type: call.type,
      count: call.count,
      files: call.files
    }));
    
    // Liste des imports
    this.results.imports = this.imports;
    
    // Résumé
    this.results.summary = {
      total_files_analyzed: this.findJSFiles().length,
      total_api_calls: this.results.total_calls,
      unique_endpoints: this.results.unique_urls,
      axios_calls: this.axiosCalls.length,
      fetch_calls: this.fetchCalls.length,
      api_calls: Array.from(this.apiCalls.values()).filter(call => call.type === 'api').length,
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
    
    console.log(`\n🔧 Types d'Appels:`);
    console.log(`   Appels axios: ${this.results.summary.axios_calls}`);
    console.log(`   Appels fetch: ${this.results.summary.fetch_calls}`);
    console.log(`   Appels API: ${this.results.summary.api_calls}`);
    
    console.log(`\n📊 Méthodes HTTP:`);
    Object.entries(this.results.by_method).forEach(([method, count]) => {
      console.log(`   ${method}: ${count}`);
    });
    
    console.log(`\n📁 Fichiers les plus actifs:`);
    Object.entries(this.results.by_file)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 5)
      .forEach(([file, count]) => {
        console.log(`   ${file}: ${count} appels`);
      });
    
    console.log(`\n🎯 Endpoints les plus utilisés:`);
    this.results.calls
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)
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
  run() {
    console.log('🚀 Démarrage de l\'analyse des appels API...');
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
      console.log(`📄 Liste des appels API disponible dans: ${csvFile}`);
    }
    
    return this.results;
  }
}

/**
 * Fonction principale
 */
function main() {
  const finder = new SimpleAPIFinder();
  const results = finder.run();
  return results;
}

// Exécuter si le script est appelé directement
if (require.main === module) {
  main();
}

module.exports = SimpleAPIFinder;
