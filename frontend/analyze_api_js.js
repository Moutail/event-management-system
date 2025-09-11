#!/usr/bin/env node

/**
 * Script spécialisé pour analyser le fichier api.js
 * Extrait toutes les définitions d'API et les appels
 */

const fs = require('fs');
const path = require('path');

class APIAnalyzer {
  constructor() {
    this.apiDefinitions = new Map();
    this.results = {
      timestamp: new Date().toISOString(),
      total_definitions: 0,
      by_method: {},
      definitions: [],
      summary: {}
    };
  }

  /**
   * Analyse le fichier api.js
   */
  analyzeAPIFile(filePath = 'src/services/api.js') {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      
      console.log(`📁 Analyse du fichier: ${filePath}`);
      console.log(`📄 ${lines.length} lignes à analyser`);
      
      lines.forEach((line, index) => {
        this.analyzeLine(line, filePath, index + 1);
      });
      
    } catch (error) {
      console.error(`❌ Erreur lors de l'analyse de ${filePath}: ${error.message}`);
    }
  }

  /**
   * Analyse une ligne de code
   */
  analyzeLine(line, filePath, lineNumber) {
    // Ignorer les commentaires et lignes vides
    if (line.trim().startsWith('//') || line.trim().startsWith('/*') || line.trim() === '') {
      return;
    }

    // Chercher les définitions d'API
    this.findAPIDefinitions(line, filePath, lineNumber);
  }

  /**
   * Trouve les définitions d'API
   */
  findAPIDefinitions(line, filePath, lineNumber) {
    // Patterns pour les définitions d'API
    const patterns = [
      // getEvents: (params = {}) => api.get('/events/', { params }),
      /(\w+):\s*\([^)]*\)\s*=>\s*api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
      // getEventById: (id) => api.get(`/events/${id}/`),
      /(\w+):\s*\([^)]*\)\s*=>\s*api\.(get|post|put|patch|delete)\s*\(\s*`([^`]+)`/g,
      // createEvent: (eventData) => { ... api.post('/events/', ...) }
      /(\w+):\s*\([^)]*\)\s*=>\s*\{[^}]*api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/g,
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

    // Analyser les définitions d'API plus complexes
    this.analyzeComplexDefinitions(line, filePath, lineNumber);
  }

  /**
   * Analyse les définitions d'API complexes
   */
  analyzeComplexDefinitions(line, filePath, lineNumber) {
    // Chercher les objets d'API (eventAPI, authAPI, etc.)
    if (line.includes('export const') && line.includes('API')) {
      const apiName = line.match(/export\s+const\s+(\w+API)/);
      if (apiName) {
        console.log(`🔍 Objet API trouvé: ${apiName[1]}`);
      }
    }

    // Chercher les méthodes dans les objets API
    if (line.includes('api.') && (line.includes('get(') || line.includes('post(') || line.includes('put(') || line.includes('patch(') || line.includes('delete('))) {
      // Extraire la méthode et l'URL
      const methodMatch = line.match(/api\.(get|post|put|patch|delete)\s*\(\s*['"`]([^'"`]+)['"`]/);
      if (methodMatch) {
        const method = methodMatch[1].toUpperCase();
        const url = methodMatch[2];
        
        if (url && url.startsWith('/api/')) {
          // Extraire le nom de la méthode
          const methodNameMatch = line.match(/(\w+):\s*\([^)]*\)\s*=>/);
          const methodName = methodNameMatch ? methodNameMatch[1] : 'unknown';
          
          this.apiDefinitions.set(methodName, {
            method: method,
            url: url,
            file: filePath,
            line: lineNumber,
            code: line.trim()
          });
        }
      }
    }
  }

  /**
   * Génère les statistiques
   */
  generateStatistics() {
    this.results.total_definitions = this.apiDefinitions.size;
    
    // Convertir en array
    this.results.definitions = Array.from(this.apiDefinitions.values());
    
    // Statistiques par méthode
    this.results.by_method = {};
    this.results.definitions.forEach(def => {
      if (!this.results.by_method[def.method]) {
        this.results.by_method[def.method] = 0;
      }
      this.results.by_method[def.method]++;
    });
    
    // Résumé
    this.results.summary = {
      total_definitions: this.results.total_definitions,
      most_used_method: this.getMostUsedMethod(),
      unique_urls: new Set(this.results.definitions.map(d => d.url)).size
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
    console.log('📊 RÉSUMÉ DE L\'ANALYSE DU FICHIER API.JS');
    console.log('='.repeat(80));
    
    console.log(`\n📋 Statistiques Générales:`);
    console.log(`   Total de définitions: ${this.results.summary.total_definitions}`);
    console.log(`   URLs uniques: ${this.results.summary.unique_urls}`);
    console.log(`   Méthode la plus utilisée: ${this.results.summary.most_used_method}`);
    
    console.log(`\n📊 Méthodes HTTP:`);
    Object.entries(this.results.by_method)
      .sort(([,a], [,b]) => b - a)
      .forEach(([method, count]) => {
        console.log(`   ${method}: ${count} définitions`);
      });
    
    console.log(`\n🔧 Définitions d'API trouvées:`);
    this.results.definitions
      .sort((a, b) => a.method.localeCompare(b.method))
      .forEach(def => {
        console.log(`   ${def.method} ${def.url}`);
        console.log(`      Ligne ${def.line}: ${def.code.split('=>')[0].trim()}`);
      });
    
    console.log('='.repeat(80));
  }

  /**
   * Sauvegarde le rapport
   */
  saveReport(filename = null) {
    if (!filename) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      filename = `api_definitions_analysis_${timestamp}.json`;
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
      filename = `api_definitions_${timestamp}.csv`;
    }
    
    try {
      const csvContent = [
        'Method,URL,Line,Code',
        ...this.results.definitions.map(def => 
          `${def.method},${def.url},${def.line},"${def.code}"`
        )
      ].join('\n');
      
      fs.writeFileSync(filename, csvContent, 'utf8');
      console.log(`📄 Définitions d'API exportées dans: ${filename}`);
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
    console.log('🚀 Démarrage de l\'analyse du fichier api.js...');
    console.log('='.repeat(80));
    
    this.analyzeAPIFile();
    this.generateStatistics();
    this.printSummary();
    
    const reportFile = this.saveReport();
    const csvFile = this.exportToCSV();
    
    if (reportFile) {
      console.log(`\n📄 Rapport détaillé disponible dans: ${reportFile}`);
    }
    
    if (csvFile) {
      console.log(`📄 Liste des définitions disponible dans: ${csvFile}`);
    }
    
    return this.results;
  }
}

/**
 * Fonction principale
 */
function main() {
  const analyzer = new APIAnalyzer();
  const results = analyzer.run();
  return results;
}

// Exécuter si le script est appelé directement
if (require.main === module) {
  main();
}

module.exports = APIAnalyzer;
