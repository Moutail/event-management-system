#!/usr/bin/env python3
"""
Script de test complet pour tous les endpoints
Utilise le management command check_endpoints.py et génère un rapport détaillé
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire backend au path Python
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')

import django
django.setup()

from django.core.management import call_command
from django.test import Client
from django.urls import get_resolver
from events.management.commands.check_endpoints import Command as CheckEndpointsCommand


class ComprehensiveEndpointTester:
    """Testeur complet des endpoints avec analyse détaillée"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'backend_analysis': {},
            'frontend_comparison': {},
            'recommendations': [],
            'summary': {}
        }
        
    def run_comprehensive_test(self):
        """Exécute tous les tests et analyses"""
        print("🚀 Démarrage du test complet des endpoints...")
        print("=" * 80)
        
        # 1. Test du backend avec le management command
        print("\n1️⃣ Test du backend avec management command...")
        self.test_backend_with_command()
        
        # 2. Analyse des URLs disponibles
        print("\n2️⃣ Analyse des URLs disponibles...")
        self.analyze_available_urls()
        
        # 3. Test de connectivité
        print("\n3️⃣ Test de connectivité...")
        self.test_connectivity()
        
        # 4. Analyse des patterns d'URLs
        print("\n4️⃣ Analyse des patterns d'URLs...")
        self.analyze_url_patterns()
        
        # 5. Génération du rapport final
        print("\n5️⃣ Génération du rapport final...")
        self.generate_final_report()
        
        print("\n✅ Test complet terminé!")
        return self.results
    
    def test_backend_with_command(self):
        """Teste le backend avec le management command"""
        try:
            # Exécuter le management command
            print("   Exécution du management command...")
            
            # Capturer la sortie
            from io import StringIO
            from django.core.management import call_command
            
            output = StringIO()
            call_command('check_endpoints', '--format=json', stdout=output)
            
            # Parser la sortie JSON
            output_str = output.getvalue()
            if output_str.strip():
                try:
                    backend_data = json.loads(output_str)
                    self.results['backend_analysis'] = backend_data
                    print(f"   ✅ {backend_data.get('statistics', {}).get('total_endpoints', 0)} endpoints testés")
                except json.JSONDecodeError:
                    print("   ⚠️  Impossible de parser la sortie JSON du management command")
                    self.results['backend_analysis'] = {'error': 'JSON parsing failed'}
            else:
                print("   ⚠️  Aucune sortie du management command")
                self.results['backend_analysis'] = {'error': 'No output'}
                
        except Exception as e:
            print(f"   ❌ Erreur lors de l'exécution du management command: {e}")
            self.results['backend_analysis'] = {'error': str(e)}
    
    def analyze_available_urls(self):
        """Analyse toutes les URLs disponibles dans l'application"""
        try:
            resolver = get_resolver()
            all_urls = []
            
            def extract_urls(url_patterns, prefix=''):
                for pattern in url_patterns:
                    if hasattr(pattern, 'url_patterns'):
                        extract_urls(pattern.url_patterns, prefix + str(pattern.pattern))
                    else:
                        url_name = getattr(pattern, 'name', None)
                        url_pattern = str(pattern.pattern)
                        full_pattern = prefix + url_pattern
                        
                        clean_pattern = full_pattern.replace('^', '').replace('$', '')
                        if clean_pattern.startswith('//'):
                            clean_pattern = clean_pattern[1:]
                        
                        all_urls.append({
                            'pattern': clean_pattern,
                            'name': url_name,
                            'full_pattern': full_pattern,
                            'view': getattr(pattern, 'callback', None)
                        })
            
            extract_urls(resolver.url_patterns)
            
            # Filtrer les URLs API
            api_urls = [
                url for url in all_urls 
                if url['pattern'].startswith('api/') or url['name']
            ]
            
            self.results['available_urls'] = {
                'total': len(all_urls),
                'api_urls': len(api_urls),
                'urls': api_urls
            }
            
            print(f"   ✅ {len(all_urls)} URLs totales trouvées")
            print(f"   ✅ {len(api_urls)} URLs API trouvées")
            
        except Exception as e:
            print(f"   ❌ Erreur lors de l'analyse des URLs: {e}")
            self.results['available_urls'] = {'error': str(e)}
    
    def test_connectivity(self):
        """Teste la connectivité avec le backend"""
        try:
            client = Client()
            
            # Test des endpoints principaux
            test_endpoints = [
                '/health/',
                '/api/events/',
                '/api/categories/',
                '/api/tags/',
                '/api/registrations/',
                '/api/history/',
                '/admin/analytics/',
                '/admin/moderation/',
                '/admin/system_health/',
                '/streaming/platforms/',
                '/ai/info/',
                '/cron/notifications/',
            ]
            
            connectivity_results = {}
            
            for endpoint in test_endpoints:
                try:
                    response = client.get(endpoint, follow=True)
                    connectivity_results[endpoint] = {
                        'status_code': response.status_code,
                        'success': 200 <= response.status_code < 400,
                        'content_type': response.get('Content-Type', ''),
                        'content_length': len(response.content) if hasattr(response, 'content') else 0
                    }
                except Exception as e:
                    connectivity_results[endpoint] = {
                        'status_code': 0,
                        'success': False,
                        'error': str(e)
                    }
            
            self.results['connectivity'] = connectivity_results
            
            successful = sum(1 for r in connectivity_results.values() if r['success'])
            total = len(connectivity_results)
            
            print(f"   ✅ {successful}/{total} endpoints principaux accessibles")
            
        except Exception as e:
            print(f"   ❌ Erreur lors du test de connectivité: {e}")
            self.results['connectivity'] = {'error': str(e)}
    
    def analyze_url_patterns(self):
        """Analyse les patterns d'URLs pour identifier les problèmes potentiels"""
        try:
            if 'available_urls' not in self.results:
                return
            
            urls = self.results['available_urls']['urls']
            
            # Analyser les patterns
            pattern_analysis = {
                'by_method': {},
                'by_category': {},
                'with_parameters': [],
                'without_names': [],
                'duplicate_patterns': [],
                'complex_patterns': []
            }
            
            for url in urls:
                pattern = url['pattern']
                
                # Analyser les paramètres
                if '<' in pattern and '>' in pattern:
                    pattern_analysis['with_parameters'].append(url)
                
                # URLs sans nom
                if not url['name']:
                    pattern_analysis['without_names'].append(url)
                
                # Patterns complexes
                if pattern.count('/') > 3:
                    pattern_analysis['complex_patterns'].append(url)
            
            # Détecter les patterns dupliqués
            pattern_counts = {}
            for url in urls:
                pattern = url['pattern']
                if pattern in pattern_counts:
                    pattern_counts[pattern].append(url)
                else:
                    pattern_counts[pattern] = [url]
            
            pattern_analysis['duplicate_patterns'] = [
                patterns for patterns in pattern_counts.values() 
                if len(patterns) > 1
            ]
            
            self.results['pattern_analysis'] = pattern_analysis
            
            print(f"   ✅ {len(pattern_analysis['with_parameters'])} URLs avec paramètres")
            print(f"   ✅ {len(pattern_analysis['without_names'])} URLs sans nom")
            print(f"   ✅ {len(pattern_analysis['duplicate_patterns'])} patterns dupliqués")
            
        except Exception as e:
            print(f"   ❌ Erreur lors de l'analyse des patterns: {e}")
            self.results['pattern_analysis'] = {'error': str(e)}
    
    def generate_final_report(self):
        """Génère le rapport final avec recommandations"""
        try:
            # Calculer les statistiques globales
            stats = {
                'total_endpoints': 0,
                'successful_endpoints': 0,
                'failed_endpoints': 0,
                'connectivity_score': 0,
                'pattern_issues': 0
            }
            
            # Statistiques du backend
            if 'backend_analysis' in self.results and 'statistics' in self.results['backend_analysis']:
                backend_stats = self.results['backend_analysis']['statistics']
                stats['total_endpoints'] = backend_stats.get('total_endpoints', 0)
                stats['successful_endpoints'] = backend_stats.get('successful', 0)
                stats['failed_endpoints'] = backend_stats.get('failed', 0)
            
            # Score de connectivité
            if 'connectivity' in self.results:
                connectivity = self.results['connectivity']
                if isinstance(connectivity, dict) and 'error' not in connectivity:
                    successful = sum(1 for r in connectivity.values() if r.get('success', False))
                    total = len(connectivity)
                    stats['connectivity_score'] = (successful / total * 100) if total > 0 else 0
            
            # Problèmes de patterns
            if 'pattern_analysis' in self.results:
                pattern_analysis = self.results['pattern_analysis']
                if isinstance(pattern_analysis, dict) and 'error' not in pattern_analysis:
                    stats['pattern_issues'] = (
                        len(pattern_analysis.get('without_names', [])) +
                        len(pattern_analysis.get('duplicate_patterns', []))
                    )
            
            self.results['summary'] = stats
            
            # Générer des recommandations
            recommendations = []
            
            if stats['connectivity_score'] < 80:
                recommendations.append({
                    'type': 'warning',
                    'message': f"Score de connectivité faible: {stats['connectivity_score']:.1f}%",
                    'action': 'Vérifier la configuration des endpoints et les permissions'
                })
            
            if stats['pattern_issues'] > 0:
                recommendations.append({
                    'type': 'info',
                    'message': f"{stats['pattern_issues']} problèmes de patterns détectés",
                    'action': 'Considérer l\'ajout de noms aux URLs et la résolution des doublons'
                })
            
            if stats['failed_endpoints'] > stats['successful_endpoints']:
                recommendations.append({
                    'type': 'error',
                    'message': f"Plus d'endpoints en échec ({stats['failed_endpoints']}) que de succès ({stats['successful_endpoints']})",
                    'action': 'Réviser la configuration des endpoints et corriger les erreurs'
                })
            
            self.results['recommendations'] = recommendations
            
            print(f"   ✅ Rapport généré avec {len(recommendations)} recommandations")
            
        except Exception as e:
            print(f"   ❌ Erreur lors de la génération du rapport: {e}")
            self.results['error'] = str(e)
    
    def save_report(self, filename=None):
        """Sauvegarde le rapport dans un fichier"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'endpoint_test_report_{timestamp}.json'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            
            print(f"📄 Rapport sauvegardé dans: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return None
    
    def print_summary(self):
        """Affiche un résumé du rapport"""
        print("\n" + "=" * 80)
        print("📊 RÉSUMÉ DU TEST DES ENDPOINTS")
        print("=" * 80)
        
        if 'summary' in self.results:
            stats = self.results['summary']
            print(f"Total d'endpoints: {stats.get('total_endpoints', 0)}")
            print(f"Endpoints fonctionnels: {stats.get('successful_endpoints', 0)}")
            print(f"Endpoints en échec: {stats.get('failed_endpoints', 0)}")
            print(f"Score de connectivité: {stats.get('connectivity_score', 0):.1f}%")
            print(f"Problèmes de patterns: {stats.get('pattern_issues', 0)}")
        
        if 'recommendations' in self.results:
            print(f"\n💡 Recommandations ({len(self.results['recommendations'])}):")
            for i, rec in enumerate(self.results['recommendations'], 1):
                print(f"  {i}. [{rec['type'].upper()}] {rec['message']}")
                print(f"     Action: {rec['action']}")
        
        print("=" * 80)


def main():
    """Fonction principale"""
    print("🔍 Testeur Complet des Endpoints")
    print("=" * 80)
    
    # Créer le testeur
    tester = ComprehensiveEndpointTester()
    
    # Exécuter les tests
    results = tester.run_comprehensive_test()
    
    # Afficher le résumé
    tester.print_summary()
    
    # Sauvegarder le rapport
    report_file = tester.save_report()
    
    if report_file:
        print(f"\n📄 Rapport détaillé disponible dans: {report_file}")
    
    return results


if __name__ == '__main__':
    main()
