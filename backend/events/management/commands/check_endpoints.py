"""
Management command pour tester tous les endpoints de l'API
Diagnostic complet des URLs disponibles et de leur fonctionnement
"""

from django.core.management.base import BaseCommand
from django.urls import get_resolver, reverse
from django.test import Client
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection
import json
import time
from urllib.parse import urlparse
from collections import defaultdict


class Command(BaseCommand):
    help = 'Teste tous les endpoints de l\'API et génère un rapport de diagnostic'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='table',
            choices=['table', 'json', 'csv'],
            help='Format de sortie du rapport (table, json, csv)'
        )
        parser.add_argument(
            '--include-auth',
            action='store_true',
            help='Inclure les tests d\'authentification (nécessite un superuser)'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=10,
            help='Timeout en secondes pour chaque requête'
        )
        parser.add_argument(
            '--save-report',
            type=str,
            help='Sauvegarder le rapport dans un fichier'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Démarrage du diagnostic des endpoints...')
        )
        
        # Configuration
        self.format = options['format']
        self.include_auth = options['include_auth']
        self.timeout = options['timeout']
        self.save_report = options['save_report']
        
        # Initialisation
        self.client = Client()
        self.results = []
        self.errors = []
        self.stats = {
            'total_endpoints': 0,
            'successful': 0,
            'failed': 0,
            'auth_required': 0,
            'not_found': 0,
            'server_errors': 0
        }
        
        # Créer un superuser pour les tests d'auth si demandé
        if self.include_auth:
            self.setup_auth_user()
        
        # Collecter toutes les URLs
        self.collect_urls()
        
        # Tester chaque endpoint
        self.test_endpoints()
        
        # Générer le rapport
        self.generate_report()
        
        # Afficher les statistiques
        self.display_stats()

    def setup_auth_user(self):
        """Crée un superuser temporaire pour les tests d'authentification"""
        try:
            self.test_user, created = User.objects.get_or_create(
                username='test_diagnostic',
                defaults={
                    'email': 'test@diagnostic.com',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            if created:
                self.test_user.set_password('test123')
                self.test_user.save()
                self.stdout.write(
                    self.style.WARNING('⚠️  Superuser de test créé: test_diagnostic / test123')
                )
            
            # Se connecter
            self.client.force_login(self.test_user)
            self.stdout.write(
                self.style.SUCCESS('✅ Authentification configurée pour les tests')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de la création du superuser: {e}')
            )
            self.include_auth = False

    def collect_urls(self):
        """Collecte toutes les URLs disponibles dans l'application"""
        self.stdout.write('📋 Collecte des URLs disponibles...')
        
        resolver = get_resolver()
        self.all_urls = []
        
        # Fonction récursive pour extraire toutes les URLs
        def extract_urls(url_patterns, prefix=''):
            for pattern in url_patterns:
                if hasattr(pattern, 'url_patterns'):
                    # C'est un include, continuer récursivement
                    extract_urls(pattern.url_patterns, prefix + str(pattern.pattern))
                else:
                    # C'est une URL finale
                    url_name = getattr(pattern, 'name', None)
                    url_pattern = str(pattern.pattern)
                    full_pattern = prefix + url_pattern
                    
                    # Nettoyer le pattern
                    clean_pattern = full_pattern.replace('^', '').replace('$', '')
                    if clean_pattern.startswith('//'):
                        clean_pattern = clean_pattern[1:]
                    
                    self.all_urls.append({
                        'pattern': clean_pattern,
                        'name': url_name,
                        'full_pattern': full_pattern,
                        'view': getattr(pattern, 'callback', None)
                    })
        
        # Extraire les URLs de l'application events
        try:
            events_urls = resolver.url_patterns
            extract_urls(events_urls)
            
            # Filtrer pour ne garder que les URLs API
            self.api_urls = [
                url for url in self.all_urls 
                if url['pattern'].startswith('api/') or url['name']
            ]
            
            self.stats['total_endpoints'] = len(self.api_urls)
            self.stdout.write(
                self.style.SUCCESS(f'✅ {len(self.api_urls)} endpoints API trouvés')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de la collecte des URLs: {e}')
            )
            self.api_urls = []

    def test_endpoints(self):
        """Teste chaque endpoint avec différentes méthodes"""
        self.stdout.write('🧪 Test des endpoints en cours...')
        
        for i, url_info in enumerate(self.api_urls, 1):
            self.stdout.write(f'  [{i}/{len(self.api_urls)}] Test de {url_info["pattern"]}')
            
            # Tester différentes méthodes HTTP
            methods_to_test = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
            
            for method in methods_to_test:
                result = self.test_single_endpoint(url_info, method)
                if result:
                    self.results.append(result)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Tests terminés: {len(self.results)} requêtes testées')
        )

    def test_single_endpoint(self, url_info, method):
        """Teste un endpoint spécifique avec une méthode HTTP"""
        try:
            # Construire l'URL de test
            test_url = self.build_test_url(url_info['pattern'])
            
            if not test_url:
                return None
            
            # Préparer les données de test
            test_data = self.get_test_data(url_info['pattern'], method)
            
            # Effectuer la requête
            start_time = time.time()
            
            if method == 'GET':
                response = self.client.get(test_url, follow=True)
            elif method == 'POST':
                response = self.client.post(test_url, test_data, follow=True)
            elif method == 'PUT':
                response = self.client.put(test_url, test_data, follow=True)
            elif method == 'PATCH':
                response = self.client.patch(test_url, test_data, follow=True)
            elif method == 'DELETE':
                response = self.client.delete(test_url, follow=True)
            elif method == 'OPTIONS':
                response = self.client.options(test_url, follow=True)
            
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            
            # Analyser la réponse
            status_code = response.status_code
            is_success = 200 <= status_code < 400
            is_auth_required = status_code == 401
            is_not_found = status_code == 404
            is_server_error = status_code >= 500
            
            # Mettre à jour les statistiques
            if is_success:
                self.stats['successful'] += 1
            elif is_auth_required:
                self.stats['auth_required'] += 1
            elif is_not_found:
                self.stats['not_found'] += 1
            elif is_server_error:
                self.stats['server_errors'] += 1
            else:
                self.stats['failed'] += 1
            
            # Extraire les informations de la réponse
            response_info = {
                'url': test_url,
                'method': method,
                'pattern': url_info['pattern'],
                'name': url_info['name'],
                'status_code': status_code,
                'response_time_ms': response_time,
                'success': is_success,
                'auth_required': is_auth_required,
                'not_found': is_not_found,
                'server_error': is_server_error,
                'content_type': response.get('Content-Type', ''),
                'content_length': len(response.content) if hasattr(response, 'content') else 0,
                'error_message': None
            }
            
            # Ajouter des détails d'erreur si nécessaire
            if not is_success:
                try:
                    if hasattr(response, 'content'):
                        content = response.content.decode('utf-8')
                        if content:
                            response_info['error_message'] = content[:200] + '...' if len(content) > 200 else content
                except:
                    pass
            
            return response_info
            
        except Exception as e:
            error_info = {
                'url': url_info['pattern'],
                'method': method,
                'pattern': url_info['pattern'],
                'name': url_info['name'],
                'status_code': 0,
                'response_time_ms': 0,
                'success': False,
                'auth_required': False,
                'not_found': False,
                'server_error': False,
                'content_type': '',
                'content_length': 0,
                'error_message': str(e)
            }
            self.errors.append(error_info)
            return error_info

    def build_test_url(self, pattern):
        """Construit une URL de test valide à partir du pattern"""
        # Nettoyer le pattern
        clean_pattern = pattern.replace('^', '').replace('$', '')
        
        # Remplacer les paramètres par des valeurs de test
        test_pattern = clean_pattern
        test_pattern = test_pattern.replace('<int:pk>', '1')
        test_pattern = test_pattern.replace('<int:id>', '1')
        test_pattern = test_pattern.replace('<int:event_id>', '1')
        test_pattern = test_pattern.replace('<int:registration_id>', '1')
        test_pattern = test_pattern.replace('<int:refund_id>', '1')
        test_pattern = test_pattern.replace('<int:refund_request_id>', '1')
        test_pattern = test_pattern.replace('<str:platform>', 'youtube')
        test_pattern = test_pattern.replace('<str:format>', 'json')
        
        # Ajouter le préfixe / si nécessaire
        if not test_pattern.startswith('/'):
            test_pattern = '/' + test_pattern
        
        return test_pattern

    def get_test_data(self, pattern, method):
        """Génère des données de test appropriées selon l'endpoint"""
        if method in ['GET', 'OPTIONS', 'DELETE']:
            return {}
        
        # Données de test pour différents types d'endpoints
        if 'event' in pattern.lower():
            return {
                'title': 'Test Event',
                'description': 'Test Description',
                'start_date': '2024-12-31T10:00:00Z',
                'end_date': '2024-12-31T18:00:00Z',
                'location': 'Test Location',
                'max_participants': 100,
                'price': 0
            }
        elif 'registration' in pattern.lower():
            return {
                'event': 1,
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'phone': '+1234567890'
            }
        elif 'auth' in pattern.lower():
            if 'login' in pattern.lower() or 'token' in pattern.lower():
                return {
                    'username': 'test_diagnostic',
                    'password': 'test123'
                }
            elif 'register' in pattern.lower():
                return {
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'testpass123',
                    'first_name': 'Test',
                    'last_name': 'User'
                }
        
        return {}

    def generate_report(self):
        """Génère le rapport final"""
        self.stdout.write('\n' + '='*80)
        self.stdout.write('📊 RAPPORT DE DIAGNOSTIC DES ENDPOINTS')
        self.stdout.write('='*80)
        
        if self.format == 'table':
            self.generate_table_report()
        elif self.format == 'json':
            self.generate_json_report()
        elif self.format == 'csv':
            self.generate_csv_report()
        
        # Sauvegarder si demandé
        if self.save_report:
            self.save_report_to_file()

    def generate_table_report(self):
        """Génère un rapport sous forme de tableau"""
        # Trier les résultats par statut
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        # Afficher les succès
        if successful:
            self.stdout.write('\n✅ ENDPOINTS FONCTIONNELS:')
            self.stdout.write('-' * 80)
            self.stdout.write(f"{'URL':<50} {'Method':<8} {'Status':<6} {'Time(ms)':<10}")
            self.stdout.write('-' * 80)
            
            for result in successful[:20]:  # Limiter à 20 pour la lisibilité
                self.stdout.write(
                    f"{result['url']:<50} {result['method']:<8} {result['status_code']:<6} {result['response_time_ms']:<10}"
                )
            
            if len(successful) > 20:
                self.stdout.write(f'... et {len(successful) - 20} autres endpoints fonctionnels')
        
        # Afficher les échecs
        if failed:
            self.stdout.write('\n❌ ENDPOINTS EN ÉCHEC:')
            self.stdout.write('-' * 80)
            self.stdout.write(f"{'URL':<50} {'Method':<8} {'Status':<6} {'Erreur':<20}")
            self.stdout.write('-' * 80)
            
            for result in failed:
                error_type = 'Auth' if result['auth_required'] else 'Not Found' if result['not_found'] else 'Server' if result['server_error'] else 'Other'
                self.stdout.write(
                    f"{result['url']:<50} {result['method']:<8} {result['status_code']:<6} {error_type:<20}"
                )
        
        # Afficher les erreurs d'exception
        if self.errors:
            self.stdout.write('\n💥 ERREURS D\'EXCEPTION:')
            self.stdout.write('-' * 80)
            for error in self.errors:
                self.stdout.write(f"❌ {error['url']} ({error['method']}): {error['error_message']}")

    def generate_json_report(self):
        """Génère un rapport au format JSON"""
        report_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': self.stats,
            'results': self.results,
            'errors': self.errors
        }
        
        self.stdout.write(json.dumps(report_data, indent=2, ensure_ascii=False))

    def generate_csv_report(self):
        """Génère un rapport au format CSV"""
        self.stdout.write('URL,Method,Pattern,Name,Status Code,Response Time (ms),Success,Auth Required,Not Found,Server Error,Content Type,Error Message')
        
        for result in self.results:
            self.stdout.write(
                f"{result['url']},{result['method']},{result['pattern']},{result['name'] or ''},"
                f"{result['status_code']},{result['response_time_ms']},{result['success']},"
                f"{result['auth_required']},{result['not_found']},{result['server_error']},"
                f"{result['content_type']},{result['error_message'] or ''}"
            )

    def save_report_to_file(self):
        """Sauvegarde le rapport dans un fichier"""
        try:
            with open(self.save_report, 'w', encoding='utf-8') as f:
                if self.format == 'json':
                    report_data = {
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'statistics': self.stats,
                        'results': self.results,
                        'errors': self.errors
                    }
                    f.write(json.dumps(report_data, indent=2, ensure_ascii=False))
                else:
                    # Pour table et CSV, on écrit le contenu affiché
                    f.write(f"Rapport de diagnostic des endpoints - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*80 + "\n")
                    f.write(f"Statistiques: {self.stats}\n")
                    f.write("="*80 + "\n")
                    for result in self.results:
                        f.write(f"{result}\n")
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Rapport sauvegardé dans: {self.save_report}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de la sauvegarde: {e}')
            )

    def display_stats(self):
        """Affiche les statistiques finales"""
        self.stdout.write('\n' + '='*80)
        self.stdout.write('📈 STATISTIQUES FINALES')
        self.stdout.write('='*80)
        
        total = self.stats['total_endpoints']
        successful = self.stats['successful']
        failed = self.stats['failed']
        auth_required = self.stats['auth_required']
        not_found = self.stats['not_found']
        server_errors = self.stats['server_errors']
        
        self.stdout.write(f"Total d'endpoints testés: {total}")
        self.stdout.write(f"✅ Succès: {successful} ({successful/total*100:.1f}%)")
        self.stdout.write(f"❌ Échecs: {failed} ({failed/total*100:.1f}%)")
        self.stdout.write(f"🔐 Authentification requise: {auth_required}")
        self.stdout.write(f"🔍 Non trouvé: {not_found}")
        self.stdout.write(f"💥 Erreurs serveur: {server_errors}")
        
        # Score de santé global
        health_score = (successful / total * 100) if total > 0 else 0
        if health_score >= 90:
            status = "🟢 EXCELLENT"
        elif health_score >= 75:
            status = "🟡 BON"
        elif health_score >= 50:
            status = "🟠 MOYEN"
        else:
            status = "🔴 CRITIQUE"
        
        self.stdout.write(f"\n🏆 Score de santé global: {health_score:.1f}% - {status}")
        
        # Recommandations
        self.stdout.write('\n💡 RECOMMANDATIONS:')
        if auth_required > 0:
            self.stdout.write(f"  - {auth_required} endpoints nécessitent une authentification")
        if not_found > 0:
            self.stdout.write(f"  - {not_found} endpoints retournent 404 (vérifier les URLs)")
        if server_errors > 0:
            self.stdout.write(f"  - {server_errors} endpoints ont des erreurs serveur (vérifier les logs)")
        
        self.stdout.write('='*80)
