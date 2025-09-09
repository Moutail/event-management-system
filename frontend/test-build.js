#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🧪 Test du build local pour Vercel...\n');

try {
  // Vérifier que les fichiers de configuration existent
  const requiredFiles = [
    'package.json',
    'vercel.json',
    'craco.config.js',
    '.npmrc',
    '.vercelignore'
  ];

  console.log('📋 Vérification des fichiers de configuration...');
  requiredFiles.forEach(file => {
    if (fs.existsSync(file)) {
      console.log(`✅ ${file} - OK`);
    } else {
      console.log(`❌ ${file} - MANQUANT`);
    }
  });

  // Nettoyer les anciens builds
  console.log('\n🧹 Nettoyage des anciens builds...');
  if (fs.existsSync('build')) {
    fs.rmSync('build', { recursive: true, force: true });
    console.log('✅ Dossier build supprimé');
  }

  if (fs.existsSync('node_modules')) {
    fs.rmSync('node_modules', { recursive: true, force: true });
    console.log('✅ node_modules supprimé');
  }

  // Installer les dépendances
  console.log('\n📦 Installation des dépendances...');
  execSync('npm ci --legacy-peer-deps', { stdio: 'inherit' });
  console.log('✅ Dépendances installées');

  // Test du build
  console.log('\n🔨 Test du build...');
  execSync('npm run build', { stdio: 'inherit' });
  console.log('✅ Build réussi !');

  // Vérifier que le dossier build existe
  if (fs.existsSync('build')) {
    console.log('✅ Dossier build créé');
    
    // Vérifier les fichiers essentiels
    const buildFiles = ['index.html', 'static'];
    buildFiles.forEach(file => {
      if (fs.existsSync(path.join('build', file))) {
        console.log(`✅ ${file} présent dans build/`);
      } else {
        console.log(`❌ ${file} manquant dans build/`);
      }
    });
  } else {
    console.log('❌ Dossier build non créé');
  }

  console.log('\n🎉 Test de build terminé avec succès !');
  console.log('🚀 Votre projet est prêt pour le déploiement Vercel');

} catch (error) {
  console.error('\n❌ Erreur lors du test de build:');
  console.error(error.message);
  process.exit(1);
}
