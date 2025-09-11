#!/usr/bin/env node

/**
 * Extracteur manuel des appels API
 * Version qui lit le fichier api.js et extrait manuellement les informations
 */

const fs = require('fs');
const path = require('path');

class ManualAPIExtractor {
  constructor() {
    this.apiDefinitions = [];
    this.results = {
      timestamp: new Date().toISOString(),
      total_definitions: 0,
      by_method: {},
      definitions: [],
      summary: {}
    };
  }

  /**
   * Extrait les définitions d'API du fichier api.js
   */
  extractAPIDefinitions(filePath = 'src/services/api.js') {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const lines = content.split('\n');
      
      console.log(`📁 Extraction des définitions d'API depuis: ${filePath}`);
      console.log(`📄 ${lines.length} lignes à analyser`);
      
      let currentAPI = null;
      let inAPIObject = false;
      
      lines.forEach((line, index) => {
        const lineNumber = index + 1;
        const trimmedLine = line.trim();
        
        // Détecter le début d'un objet API
        if (trimmedLine.startsWith('export const') && trimmedLine.includes('API')) {
          const apiName = trimmedLine.match(/export\s+const\s+(\w+API)/);
          if (apiName) {
            currentAPI = apiName[1];
            inAPIObject = true;
            console.log(`🔍 Objet API trouvé: ${currentAPI}`);
          }
        }
        
        // Détecter la fin d'un objet API
        if (inAPIObject && trimmedLine === '};') {
          inAPIObject = false;
          currentAPI = null;
        }
        
        // Extraire les définitions d'API
        if (inAPIObject && currentAPI && trimmedLine.includes('api.')) {
          this.extractAPIDefinitionFromLine(trimmedLine, filePath, lineNumber, currentAPI);
        }
      });
      
    } catch (error) {
      console.error(`❌ Erreur lors de l'extraction de ${filePath}: ${error.message}`);
    }
  }

  /**
   * Extrait une définition d'API d'une ligne
   */
  extractAPIDefinitionFromLine(line, filePath, lineNumber, apiName) {
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
          this.apiDefinitions.push({
            api: apiName,
            method: method.toUpperCase(),
            url: url,
            file: filePath,
            line: lineNumber,
            code: line
          });
        }
      }
    });
  }

  /**
   * Génère les statistiques
   */
  generateStatistics() {
    this.results.total_definitions = this.apiDefinitions.length;
    
    // Convertir en array
    this.results.definitions = this.apiDefinitions;
    
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
      unique_urls: new Set(this.results.definitions.map(d => d.url)).size,
      apis: [...new Set(this.results.definitions.map(d => d.api))]
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
    console.log('📊 RÉSUMÉ DE L\'EXTRACTION DES DÉFINITIONS D\'API');
    console.log('='.repeat(80));
    
    console.log(`\n📋 Statistiques Générales:`);
    console.log(`   Total de définitions: ${this.results.summary.total_definitions}`);
    console.log(`   URLs uniques: ${this.results.summary.unique_urls}`);
    console.log(`   Méthode la plus utilisée: ${this.results.summary.most_used_method}`);
    console.log(`   APIs trouvées: ${this.results.summary.apis.join(', ')}`);
    
    console.log(`\n📊 Méthodes HTTP:`);
    Object.entries(this.results.by_method)
      .sort(([,a], [,b]) => b - a)
      .forEach(([method, count]) => {
        console.log(`   ${method}: ${count} définitions`);
      });
    
    console.log(`\n🔧 Définitions d'API par objet:`);
    const groupedByAPI = this.results.definitions.reduce((acc, def) => {
      if (!acc[def.api]) acc[def.api] = [];
      acc[def.api].push(def);
      return acc;
    }, {});
    
    Object.entries(groupedByAPI).forEach(([api, definitions]) => {
      console.log(`\n   ${api}:`);
      definitions.forEach(def => {
        console.log(`     ${def.method} ${def.url}`);
        console.log(`        Ligne ${def.line}: ${def.code.split('=>')[0].trim()}`);
      });
    });
    
    console.log('='.repeat(80));
  }

  /**
   * Sauvegarde le rapport
   */
  saveReport(filename = null) {
    if (!filename) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      filename = `api_definitions_extracted_${timestamp}.json`;
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
      filename = `api_definitions_extracted_${timestamp}.csv`;
    }
    
    try {
      const csvContent = [
        'API,Method,URL,Line,Code',
        ...this.results.definitions.map(def => 
          `${def.api},${def.method},${def.url},${def.line},"${def.code}"`
        )
      ].join('\n');
      
      fs.writeFileSync(filename, csvContent, 'utf8');
      console.log(`📄 Définitions exportées dans: ${filename}`);
      return filename;
    } catch (error) {
      console.error('❌ Erreur lors de l\'export CSV:', error);
      return null;
    }
  }

  /**
   * Exécute l'extraction
   */
  run() {
    console.log('🚀 Démarrage de l\'extraction des définitions d\'API...');
    console.log('='.repeat(80));
    
    this.extractAPIDefinitions();
    this.generateStatistics();
    this.printSummary();
    
    const reportFile = this.saveReport();
    const csvFile = this.exportToCSV();
    
    if (reportFile) {
      console.log(`\n📄 Rapport détaillé disponible dans: ${reportFile}`);
    }
    
    if (csvFile) {
      console.log(`📄 Définitions exportées dans: ${csvFile}`);
    }
    
    return this.results;
  }
}

/**
 * Fonction principale
 */
function main() {
  const extractor = new ManualAPIExtractor();
  const results = extractor.run();
  return results;
}

// Exécuter si le script est appelé directement
if (require.main === module) {
  main();
}

module.exports = ManualAPIExtractor;
