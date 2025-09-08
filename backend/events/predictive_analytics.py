"""
🎯 ANALYTICS PRÉDICTIFS AVANCÉS
Service d'intelligence artificielle pour la prédiction et l'optimisation des événements

Fonctionnalités :
- Prédiction du taux de remplissage des événements
- Optimisation des prix basée sur l'analyse du marché
- Détection des tendances émergentes
"""

import logging
# import numpy as np  # Commenté pour déploiement Render
# import pandas as pd  # Commenté pour déploiement Render
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from django.db.models import Q, Count, Avg, Sum, F, Min, Max, StdDev
from django.utils import timezone
from django.conf import settings
# from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier  # Commenté pour déploiement Render
# from sklearn.preprocessing import StandardScaler, LabelEncoder  # Commenté pour déploiement Render
# from sklearn.model_selection import train_test_split  # Commenté pour déploiement Render
# from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score  # Commenté pour déploiement Render
# import joblib  # Commenté pour déploiement Render
import os
import json

logger = logging.getLogger(__name__)

class PredictiveAnalyticsService:
    """
    Service d'analytics prédictifs utilisant le machine learning
    pour optimiser la gestion des événements
    """
    
    def __init__(self):
        self.models_dir = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        
    def ensure_models_directory(self):
        """Crée le répertoire pour sauvegarder les modèles ML"""
        if self.models_dir is None:
            from django.conf import settings
            self.models_dir = os.path.join(settings.BASE_DIR, 'ml_models')
        
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
    
    def prepare_event_features(self, event_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prépare les features pour l'entraînement des modèles ML
        
        Features utilisées :
        - Caractéristiques de l'événement (prix, capacité, durée, etc.)
        - Données temporelles (jour de la semaine, mois, saison)
        - Données géographiques (ville, pays)
        - Données de l'organisateur (réputation, historique)
        - Données de catégorie et tags
        """
        features = []
        targets = []
        
        for event in event_data:
            # Features de base
            price = float(event.get('price', 0))
            max_capacity = int(event.get('max_capacity', 10))
            duration_hours = float(event.get('duration_hours', 2))
            organizer_events_count = int(event.get('organizer_events_count', 0))
            organizer_avg_rating = float(event.get('organizer_avg_rating', 0))
            days_until_event = int(event.get('days_until_event', 0))
            category_popularity = int(event.get('category_popularity', 5))
            tags_count = int(event.get('tags_count', 0))
            
            feature_vector = [
                price, max_capacity, duration_hours, organizer_events_count,
                organizer_avg_rating, days_until_event, category_popularity, tags_count
            ]
            
            # Features temporelles
            if event.get('start_date') and hasattr(event['start_date'], 'weekday'):
                start_date = event['start_date']
                weekday = start_date.weekday()
                month = start_date.month
                hour = start_date.hour
                winter = int(month in [12, 1, 2])
                spring = int(month in [3, 4, 5])
                summer = int(month in [6, 7, 8])
                autumn = int(month in [9, 10, 11])
                feature_vector.extend([weekday, month, hour, winter, spring, summer, autumn])
            else:
                # Valeurs par défaut pour août (été)
                feature_vector.extend([0, 8, 12, 0, 0, 1, 0])
            
            # Features géographiques (encodage simple mais sécurisé)
            city = str(event.get('city', '')).strip()
            country = str(event.get('country', '')).strip()
            category = str(event.get('category', '')).strip()
            
            city_encoding = abs(hash(city)) % 1000 if city else 0
            country_encoding = abs(hash(country)) % 100 if country else 0
            category_encoding = abs(hash(category)) % 50 if category else 0
            
            feature_vector.extend([city_encoding, country_encoding, category_encoding])
            
            # Features de prix relatif
            avg_price_similar_events = float(event.get('avg_price_similar_events', price))
            price_ratio = price / max(avg_price_similar_events, 1.0) if avg_price_similar_events > 0 else 1.0
            feature_vector.append(price_ratio)
            
            # Target : taux de remplissage (0-1)
            fill_rate = event.get('fill_rate', 0)
            if isinstance(fill_rate, (int, float)):
                # Normaliser le taux de remplissage entre 0 et 1
                if fill_rate > 1:
                    target = min(1.0, fill_rate / max_capacity)  # Si c'est un nombre absolu
                else:
                    target = min(1.0, max(0.0, float(fill_rate)))  # Si c'est déjà un ratio
            else:
                target = 0.0
            
            features.append(feature_vector)
            targets.append(target)
        
        return np.array(features), np.array(targets)
    
    def train_fill_rate_predictor(self, force_retrain: bool = False) -> Dict:
        """
        Entraîne le modèle de prédiction du taux de remplissage
        
        Returns:
            Dict avec métriques de performance et statut
        """
        try:
            self.ensure_models_directory()
            model_path = os.path.join(self.models_dir, 'fill_rate_predictor.joblib')
            
            # Vérifier si le modèle existe et est récent
            if not force_retrain and os.path.exists(model_path):
                model_age = timezone.now() - datetime.fromtimestamp(os.path.getmtime(model_path), tz=timezone.utc)
                if model_age.days < 7:  # Retraîner si plus d'une semaine
                    logger.info("Modèle de prédiction de remplissage déjà à jour")
                    return {'status': 'up_to_date', 'message': 'Modèle déjà entraîné et à jour'}
            
            # Récupérer les données d'entraînement
            from .models import Event, EventRegistration, UserProfile
            
            # Événements passés avec données de remplissage
            past_events = Event.objects.filter(
                start_date__lt=timezone.now(),
                status='published'
            ).annotate(
                total_registrations=Count('registrations'),
                fill_rate=F('total_registrations') / F('max_capacity'),
                organizer_events_count=Count('organizer__events_organized'),
                days_until_event=F('start_date') - F('created_at'),
                tags_count=Count('tags')
            ).values(
                'id', 'price', 'max_capacity', 'start_date',
                'location', 'category__name', 'fill_rate',
                'organizer_events_count',
                'days_until_event', 'tags_count'
            )
            
            if len(past_events) < 50:
                return {
                    'status': 'insufficient_data',
                    'message': f'Données insuffisantes pour l\'entraînement: {len(past_events)} événements (minimum: 50)'
                }
            
            # Préparation des features
            event_list = list(past_events)
            
            for i, event in enumerate(event_list):
                # Nettoyage et conversion des données
                event['duration_hours'] = 2  # Valeur par défaut
                event['organizer_avg_rating'] = 0  # Valeur par défaut
                
                # Conversion sécurisée de days_until_event
                days_until_event = event.get('days_until_event')
                if isinstance(days_until_event, timedelta):
                    event['days_until_event'] = days_until_event.days
                else:
                    event['days_until_event'] = 0
                
                event['category_popularity'] = 5  # Valeur par défaut
                event['tags_count'] = int(event.get('tags_count', 0))
                event['avg_price_similar_events'] = float(event.get('price', 0))  # Utiliser le prix de l'événement
                event['city'] = event.get('location', '').split(',')[0] if event.get('location') else ''
                event['country'] = event.get('location', '').split(',')[-1].strip() if event.get('location') else ''
                event['category'] = event.get('category__name', '') or 'Unknown'
                
                # Nettoyage des valeurs None
                if event.get('max_capacity') is None:
                    event['max_capacity'] = 10  # Valeur par défaut
                if event.get('fill_rate') is None:
                    event['fill_rate'] = 0.0  # Valeur par défaut
            
            X, y = self.prepare_event_features(event_list)
            
            # Division train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Standardisation des features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Entraînement du modèle
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_train_scaled, y_train)
            
            # Évaluation
            y_pred = model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Sauvegarde du modèle et du scaler
            model_data = {
                'model': model,
                'scaler': self.scaler,
                'feature_names': [
                    'price', 'max_capacity', 'duration_hours', 'organizer_events_count',
                    'organizer_avg_rating', 'days_until_event', 'category_popularity',
                    'tags_count', 'weekday', 'month', 'hour', 'winter', 'spring',
                    'summer', 'autumn', 'city_encoding', 'country_encoding',
                    'category_encoding', 'price_ratio'
                ]
            }
            
            joblib.dump(model_data, model_path)
            
            logger.info(f"Modèle de prédiction entraîné avec succès. MAE: {mae:.4f}, R²: {r2:.4f}")
            
            return {
                'status': 'success',
                'message': 'Modèle entraîné avec succès',
                'metrics': {
                    'mae': round(mae, 4),
                    'r2': round(r2, 4),
                    'training_samples': len(X_train),
                    'test_samples': len(X_test)
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'entraînement du modèle: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur lors de l\'entraînement: {str(e)}'
            }
    
    def predict_event_fill_rate(self, event_data: Dict) -> Dict:
        """
        Prédit le taux de remplissage d'un événement
        
        Args:
            event_data: Données de l'événement
            
        Returns:
            Dict avec prédiction et confiance
        """
        try:
            self.ensure_models_directory()
            model_path = os.path.join(self.models_dir, 'fill_rate_predictor.joblib')
            
            if not os.path.exists(model_path):
                # Entraîner le modèle si nécessaire
                train_result = self.train_fill_rate_predictor()
                if train_result['status'] != 'success':
                    return {
                        'status': 'error',
                        'message': 'Modèle non disponible',
                        'prediction': None,
                        'confidence': 0
                    }
            
            # Charger le modèle
            model_data = joblib.load(model_path)
            model = model_data['model']
            scaler = model_data['scaler']
            
            # Préparer les features de l'événement
            features, _ = self.prepare_event_features([event_data])
            features_scaled = scaler.transform(features)
            
            # Prédiction
            prediction = model.predict(features_scaled)[0]
            prediction = max(0.0, min(1.0, prediction))  # Clamp entre 0 et 1
            
            # Calcul de la confiance (basé sur la variance des prédictions des arbres)
            predictions_trees = [tree.predict(features_scaled)[0] for tree in model.estimators_]
            confidence = 1.0 - (np.std(predictions_trees) / max(np.mean(predictions_trees), 0.1))
            confidence = max(0.1, min(1.0, confidence))
            
            return {
                'status': 'success',
                'prediction': round(prediction, 4),
                'confidence': round(confidence, 4),
                'predicted_registrations': int(prediction * event_data.get('max_capacity', 0)),
                'message': f'Prédiction: {prediction*100:.1f}% de remplissage'
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur lors de la prédiction: {str(e)}',
                'prediction': None,
                'confidence': 0
            }
    
    def optimize_event_pricing(self, event_data: Dict, target_fill_rate: float = 0.8) -> Dict:
        """
        Optimise le prix d'un événement pour atteindre le taux de remplissage cible
        
        Args:
            event_data: Données de l'événement
            target_fill_rate: Taux de remplissage cible (0-1)
            
        Returns:
            Dict avec prix optimisé et recommandations
        """
        try:
            current_price = float(event_data.get('price', 0))
            if current_price <= 0:
                return {
                    'status': 'error',
                    'message': 'Prix actuel invalide pour l\'optimisation'
                }
            
            # Analyse de la sensibilité au prix
            price_variations = np.linspace(current_price * 0.5, current_price * 2.0, 20)
            predictions = []
            
            for price in price_variations:
                test_data = event_data.copy()
                test_data['price'] = price
                
                # Prédire le taux de remplissage pour ce prix
                prediction_result = self.predict_event_fill_rate(test_data)
                if prediction_result['status'] == 'success':
                    predictions.append({
                        'price': price,
                        'fill_rate': prediction_result['prediction'],
                        'revenue': price * event_data.get('max_capacity', 0) * prediction_result['prediction']
                    })
            
            if not predictions:
                return {
                    'status': 'error',
                    'message': 'Impossible de générer des prédictions de prix'
                }
            
            # Trouver le prix optimal
            predictions_df = pd.DataFrame(predictions)
            
            # Prix pour le taux de remplissage cible
            target_prices = predictions_df[
                predictions_df['fill_rate'] >= target_fill_rate
            ]
            
            if len(target_prices) > 0:
                # Prix optimal basé sur le revenu maximum
                optimal_price = target_prices.loc[target_prices['revenue'].idxmax(), 'price']
                optimal_fill_rate = target_prices.loc[target_prices['revenue'].idxmax(), 'fill_rate']
                optimal_revenue = target_prices.loc[target_prices['revenue'].idxmax(), 'revenue']
            else:
                # Si pas de prix atteint le taux cible, prendre le meilleur compromis
                optimal_price = predictions_df.loc[predictions_df['revenue'].idxmax(), 'price']
                optimal_fill_rate = predictions_df.loc[predictions_df['revenue'].idxmax(), 'fill_rate']
                optimal_revenue = predictions_df.loc[predictions_df['revenue'].idxmax(), 'revenue']
            
            # Analyse de la concurrence
            market_analysis = self.analyze_market_competition(event_data)
            
            # Recommandations
            recommendations = []
            if optimal_price < current_price:
                recommendations.append("💡 Réduire le prix pour augmenter le taux de remplissage")
            elif optimal_price > current_price:
                recommendations.append("💰 Augmenter le prix pour maximiser les revenus")
            
            if market_analysis.get('status') == 'success':
                if market_analysis['price_position'] == 'high':
                    recommendations.append("⚠️ Prix plus élevé que la concurrence - risque de faible remplissage")
                elif market_analysis['price_position'] == 'low':
                    recommendations.append("✅ Prix compétitif par rapport à la concurrence")
            
            return {
                'status': 'success',
                'current_price': current_price,
                'optimal_price': round(optimal_price, 2),
                'price_change_percent': round(((optimal_price - current_price) / current_price) * 100, 1),
                'target_fill_rate': target_fill_rate,
                'predicted_fill_rate': round(optimal_fill_rate, 4),
                'predicted_revenue': round(optimal_revenue, 2),
                'revenue_improvement': round(((optimal_revenue - (current_price * event_data.get('max_capacity', 0) * 0.5)) / (current_price * event_data.get('max_capacity', 0) * 0.5)) * 100, 1),
                'market_analysis': market_analysis,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation des prix: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur lors de l\'optimisation: {str(e)}'
            }
    
    def analyze_market_competition(self, event_data: Dict) -> Dict:
        """
        Analyse la concurrence sur le marché pour un événement
        
        Args:
            event_data: Données de l'événement
            
        Returns:
            Dict avec analyse de la concurrence
        """
        try:
            from .models import Event
            
            # Événements similaires (même catégorie, période proche)
            similar_events = Event.objects.filter(
                category__name=event_data.get('category'),
                start_date__gte=timezone.now() - timedelta(days=30),
                start_date__lte=timezone.now() + timedelta(days=90),
                status='published'
            ).exclude(id=event_data.get('id')).values('price', 'max_capacity')
            
            if not similar_events:
                return {
                    'status': 'success',
                    'competition_level': 'low',
                    'price_position': 'unknown',
                    'avg_market_price': 0,
                    'price_percentile': 50
                }
            
            # Statistiques de prix
            prices = [float(event['price']) for event in similar_events]
            avg_market_price = np.mean(prices)
            current_price = float(event_data.get('price', 0))
            
            # Position de prix
            if current_price < avg_market_price * 0.8:
                price_position = 'low'
            elif current_price > avg_market_price * 1.2:
                price_position = 'high'
            else:
                price_position = 'competitive'
            
            # Percentile de prix
            price_percentile = np.percentile(prices, current_price)
            
            # Niveau de concurrence
            competition_level = 'high' if len(similar_events) > 10 else 'medium' if len(similar_events) > 5 else 'low'
            
            return {
                'status': 'success',
                'competition_level': competition_level,
                'price_position': price_position,
                'avg_market_price': round(avg_market_price, 2),
                'price_percentile': round(price_percentile, 1),
                'similar_events_count': len(similar_events),
                'price_range': {
                    'min': round(min(prices), 2),
                    'max': round(max(prices), 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de la concurrence: {str(e)}")
            return {
                'status': 'error',
                'competition_level': 'unknown',
                'price_position': 'unknown',
                'avg_market_price': 0,
                'price_percentile': 50
            }
    
    def detect_emerging_trends(self, days_back: int = 90) -> Dict:
        """
        Détecte les tendances émergentes dans les événements
        
        Args:
            days_back: Nombre de jours à analyser
            
        Returns:
            Dict avec tendances détectées
        """
        try:
            from .models import Event, EventRegistration, Category, Tag
            
            end_date = timezone.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Tendances par catégorie - CORRIGÉ avec distinct=True
            category_trends = Category.objects.annotate(
                recent_events=Count('event', filter=Q(event__created_at__gte=start_date), distinct=True),
                total_events=Count('event', distinct=True),
                recent_registrations=Count('event__registrations', filter=Q(event__registrations__registered_at__gte=start_date), distinct=True),
                avg_price=Avg('event__price'),
                avg_fill_rate=Avg('event__registrations') / F('event__max_capacity')
            ).filter(recent_events__gt=0).order_by('-recent_events')[:10]
            
            # Tendances par tags - CORRIGÉ avec distinct=True
            tag_trends = Tag.objects.annotate(
                recent_usage=Count('event', filter=Q(event__created_at__gte=start_date), distinct=True),
                total_usage=Count('event', distinct=True),
                growth_rate=(F('recent_usage') * 100.0) / F('total_usage')
            ).filter(recent_usage__gt=0).order_by('-growth_rate')[:10]
            
            # Tendances temporelles
            temporal_trends = []
            for i in range(0, days_back, 7):  # Par semaine
                week_start = start_date + timedelta(days=i)
                week_end = week_start + timedelta(days=7)
                
                week_events = Event.objects.filter(
                    created_at__gte=week_start,
                    created_at__lt=week_end
                ).count()
                
                week_registrations = EventRegistration.objects.filter(
                    registered_at__gte=week_start,
                    registered_at__lt=week_end
                ).count()
                
                temporal_trends.append({
                    'week': week_start.strftime('%Y-%m-%d'),
                    'events_created': week_events,
                    'registrations': week_registrations
                })
            
            # Tendances de prix
            price_trends = Event.objects.filter(
                created_at__gte=start_date
            ).aggregate(
                avg_price=Avg('price'),
                min_price=Min('price'),
                max_price=Max('price'),
                price_std=StdDev('price')
            )
            
            # Détection de tendances émergentes
            emerging_trends = []
            
            # Catégories en forte croissance
            for category in category_trends:
                if category.recent_events > 0 and category.total_events > 0:
                    growth_rate = (category.recent_events / category.total_events) * 100
                    if growth_rate > 20:  # Croissance > 20%
                        emerging_trends.append({
                            'type': 'category_growth',
                            'name': category.name,
                            'growth_rate': round(growth_rate, 1),
                            'recent_events': category.recent_events,
                            'avg_price': round(float(category.avg_price or 0), 2),
                            'avg_fill_rate': round(float(category.avg_fill_rate or 0), 4)
                        })
            
            # Tags émergents
            for tag in tag_trends:
                if tag.growth_rate > 30:  # Croissance > 30%
                    emerging_trends.append({
                        'type': 'tag_emerging',
                        'name': tag.name,
                        'growth_rate': round(tag.growth_rate, 1),
                        'recent_usage': tag.recent_usage,
                        'total_usage': tag.total_usage
                    })
            
            # Tendances de prix
            if price_trends['avg_price']:
                price_trends_clean = {
                    'avg_price': round(float(price_trends['avg_price']), 2),
                    'min_price': round(float(price_trends['min_price'] or 0), 2),
                    'max_price': round(float(price_trends['max_price'] or 0), 2),
                    'price_volatility': round(float(price_trends['price_std'] or 0), 2)
                }
            else:
                price_trends_clean = {}
            
            return {
                'status': 'success',
                'analysis_period': f'{days_back} jours',
                'emerging_trends': emerging_trends,
                'category_trends': self.validate_category_data(category_trends),
                'tag_trends': [
                    {
                        'name': tag.name,
                        'recent_usage': tag.recent_usage,
                        'total_usage': tag.total_usage,
                        'growth_rate': round(tag.growth_rate, 1)
                    }
                    for tag in tag_trends
                ],
                'temporal_trends': temporal_trends,
                'price_trends': price_trends_clean,
                'insights': self._generate_trend_insights(emerging_trends, category_trends, tag_trends)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection des tendances: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur lors de la détection des tendances: {str(e)}'
            }
    
    def _generate_trend_insights(self, emerging_trends: List, category_trends: List, tag_trends: List) -> List[str]:
        """Génère des insights basés sur les tendances détectées"""
        insights = []
        
        # Insights sur les catégories
        if category_trends:
            top_category = category_trends[0]
            insights.append(f"🔥 {top_category.name} est la catégorie la plus active avec {top_category.recent_events} événements récents")
        
        # Insights sur les tags
        if tag_trends:
            top_tag = tag_trends[0]
            insights.append(f"🚀 Le tag '{top_tag.name}' connaît une croissance de {top_tag.growth_rate:.1f}%")
        
        # Insights sur les tendances émergentes
        if emerging_trends:
            category_trends_count = len([t for t in emerging_trends if t['type'] == 'category_growth'])
            tag_trends_count = len([t for t in emerging_trends if t['type'] == 'tag_emerging'])
            
            if category_trends_count > 0:
                insights.append(f"📈 {category_trends_count} catégorie(s) en forte croissance détectée(s)")
            
            if tag_trends_count > 0:
                insights.append(f"🏷️ {tag_trends_count} tag(s) émergent(s) identifié(s)")
        
        return insights
    
    def get_predictive_insights(self, event_id: int = None) -> Dict:
        """
        Génère des insights prédictifs globaux ou pour un événement spécifique
        
        Args:
            event_id: ID de l'événement (optionnel)
            
        Returns:
            Dict avec insights prédictifs
        """
        try:
            
            insights = {
                'status': 'success',
                'timestamp': timezone.now().isoformat(),
                'global_insights': [],
                'event_specific_insights': [],
                'recommendations': []
            }
            
            # Insights globaux
            trends = self.detect_emerging_trends()
            
            if trends['status'] == 'success':
                insights['global_insights'].extend(trends['insights'])
                
                # Recommandations basées sur les tendances
                if trends['category_trends']:
                    top_category = trends['category_trends'][0]
                    insights['recommendations'].append(
                        f"💡 Concentrez-vous sur la catégorie '{top_category['name']}' qui connaît une croissance de {top_category['growth_rate']}%"
                    )
                
                if trends['tag_trends']:
                    top_tag = trends['tag_trends'][0]
                    insights['recommendations'].append(
                        f"🏷️ Utilisez le tag '{top_tag['name']}' pour améliorer la visibilité de vos événements"
                    )
            
            # Insights spécifiques à un événement
            if event_id:
                from .models import Event
                try:
                    event = Event.objects.get(id=event_id)
                    
                    event_data = {
                        'id': event.id,
                        'price': float(event.price),
                        'max_capacity': event.max_capacity or 100,
                        'category': event.category.name if event.category else '',
                        'city': event.location.split(',')[0] if event.location else '',
                        'country': event.location.split(',')[-1].strip() if event.location else '',
                        'start_date': event.start_date,
                        'duration_hours': 2,
                        'organizer_events_count': event.organizer.events_organized.count() if event.organizer else 0,
                        'organizer_avg_rating': getattr(event.organizer.profile, 'rating', 0) if event.organizer and hasattr(event.organizer, 'profile') else 0,
                        'tags_count': event.tags.count()
                    }
                    
                    # Prédiction de remplissage
                    fill_prediction = self.predict_event_fill_rate(event_data)
                    
                    if fill_prediction['status'] == 'success':
                        insights['event_specific_insights'].append(
                            f"🎯 Taux de remplissage prédit: {fill_prediction['prediction']*100:.1f}% (confiance: {fill_prediction['confidence']*100:.1f}%)"
                        )
                    
                    # Optimisation des prix
                    price_optimization = self.optimize_event_pricing(event_data)
                    
                    if price_optimization['status'] == 'success':
                        insights['event_specific_insights'].append(
                            f"💰 Prix optimal suggéré: {price_optimization['optimal_price']}€ (changement: {price_optimization['price_change_percent']}%)"
                        )
                        
                        if price_optimization['recommendations']:
                            insights['recommendations'].extend(price_optimization['recommendations'])
                    
                    # Analyse de la concurrence
                    market_analysis = self.analyze_market_competition(event_data)
                    
                    if market_analysis.get('status') == 'success' and market_analysis.get('competition_level') != 'unknown':
                        insights['event_specific_insights'].append(
                            f"🏆 Niveau de concurrence: {market_analysis['competition_level']} (prix: {market_analysis['price_position']})"
                        )
                
                except Event.DoesNotExist:
                    insights['event_specific_insights'].append("❌ Événement non trouvé")
            return insights
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des insights: {str(e)}")
            return {
                'status': 'error',
                'message': f'Erreur lors de la génération des insights: {str(e)}'
            }

    def validate_category_data(self, category_trends: List) -> List:
        """
        Valide et corrige les données des catégories pour éviter les anomalies
        """
        validated_trends = []
        
        for cat in category_trends:
            # Vérifier que les comptages sont raisonnables
            recent_events = min(cat.recent_events, 1000) if cat.recent_events else 0
            total_events = min(cat.total_events, 1000) if cat.total_events else 0
            
            # S'assurer que recent_events <= total_events
            if recent_events > total_events:
                recent_events = total_events
            
            # Calculer le taux de croissance de manière sécurisée
            if total_events > 0:
                growth_rate = (recent_events / total_events) * 100
            else:
                growth_rate = 0.0
            
            validated_trends.append({
                'name': cat.name,
                'recent_events': recent_events,
                'total_events': total_events,
                'growth_rate': round(growth_rate, 1),
                'avg_price': round(float(cat.avg_price or 0), 2),
                'avg_fill_rate': round(float(cat.avg_fill_rate or 0), 4)
            })
        
        return validated_trends

def get_predictive_service():
    """Retourne une instance du service d'analytics prédictifs"""
    return PredictiveAnalyticsService()

# Instance globale du service (pour compatibilité)
predictive_service = None
