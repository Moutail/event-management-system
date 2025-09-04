"""
Vues spécifiques pour l'administration Super Admin
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import os
from django.conf import settings

from .models import Event, EventRegistration, UserProfile, RefundRequest
from .permissions import IsSuperAdmin, IsOrganizerOrSuperAdmin, super_admin_required
from .serializers import EventSerializer, EventListSerializer


class SuperAdminViewSet(viewsets.ViewSet):
    """
    ViewSet pour les fonctionnalités Super Admin
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    @action(detail=False, methods=['get'])
    def global_stats(self, request):
        """Statistiques globales de la plateforme"""
        try:
            # Statistiques générales
            total_users = User.objects.count()
            total_organizers = UserProfile.objects.filter(role='organizer').count()
            total_participants = UserProfile.objects.filter(role='participant').count()
            total_events = Event.objects.count()
            published_events = Event.objects.filter(status='published').count()
            pending_events = Event.objects.filter(status='draft').count()
            total_registrations = EventRegistration.objects.count()
            confirmed_registrations = EventRegistration.objects.filter(
                status__in=['confirmed', 'attended']
            ).count()
            
            # Revenus globaux (excluant les remboursements traités)
            try:
                total_revenue = EventRegistration.objects.filter(
                    payment_status='paid'
                ).exclude(
                    refund_request__status='processed'
                ).aggregate(total=Sum('price_paid')).get('total') or 0
            except Exception as e:
                # Si la relation refund_request n'existe pas, calculer sans exclusion
                total_revenue = EventRegistration.objects.filter(
                    payment_status='paid'
                ).aggregate(total=Sum('price_paid')).get('total') or 0
            
            # Remboursements
            total_refunds = RefundRequest.objects.filter(status='processed').count()
            total_refund_amount = RefundRequest.objects.filter(
                status='processed'
            ).aggregate(total=Sum('refund_amount')).get('total') or 0
            
            # Statistiques sur 30 derniers jours
            thirty_days_ago = timezone.now() - timedelta(days=30)
            
            # Statistiques de modération
            try:
                from .models import EventHistory
                moderation_actions = EventHistory.objects.count()
                recent_moderations = EventHistory.objects.filter(
                    created_at__gte=thirty_days_ago
                ).count()
                
                # Répartition des actions de modération
                moderation_breakdown = {}
                for action in ['approve', 'reject', 'suspend', 'publish']:
                    count = EventHistory.objects.filter(action=action).count()
                    moderation_breakdown[action] = count
            except Exception as e:
                # Si EventHistory n'existe pas encore, utiliser des valeurs par défaut
                moderation_actions = 0
                recent_moderations = 0
                moderation_breakdown = {
                    'approve': 0,
                    'reject': 0,
                    'suspend': 0,
                    'publish': 0
                }
            new_users_30d = User.objects.filter(date_joined__gte=thirty_days_ago).count()
            new_events_30d = Event.objects.filter(created_at__gte=thirty_days_ago).count()
            new_registrations_30d = EventRegistration.objects.filter(
                registered_at__gte=thirty_days_ago
            ).count()
            
            # Top organisateurs (par nombre d'événements)
            try:
                top_organizers = User.objects.filter(
                    events_organized__isnull=False
                ).annotate(
                    event_count=Count('events_organized')
                ).order_by('-event_count')[:5]
            except Exception as e:
                top_organizers = []
            
            # Événements les plus populaires
            try:
                popular_events = Event.objects.filter(
                    status='published'
                ).annotate(
                    registration_count=Count('registrations')
                ).order_by('-registration_count')[:5]
            except Exception as e:
                popular_events = []
            
            return Response({
                'general_stats': {
                    'total_users': total_users,
                    'total_organizers': total_organizers,
                    'total_participants': total_participants,
                    'total_events': total_events,
                    'published_events': published_events,
                    'pending_events': pending_events,
                    'total_registrations': total_registrations,
                    'confirmed_registrations': confirmed_registrations,
                    'total_revenue': float(total_revenue),
                    'total_refunds': total_refunds,
                    'total_refund_amount': float(total_refund_amount),
                    'active_users': total_users,  # Pour l'instant, tous les utilisateurs
                },
                'moderation_stats': {
                    'total_actions': moderation_actions,
                    'recent_actions': recent_moderations,
                    'breakdown': moderation_breakdown
                },
                'recent_activity': {
                    'new_users_30d': new_users_30d,
                    'new_events_30d': new_events_30d,
                    'new_registrations_30d': new_registrations_30d,
                },
                'top_organizers': [
                    {
                        'id': user.id,
                        'username': user.username,
                        'full_name': f"{user.first_name} {user.last_name}".strip(),
                        'event_count': user.event_count,
                        'email': user.email,
                    }
                    for user in top_organizers
                ],
                'popular_events': [
                    {
                        'id': event.id,
                        'title': event.title,
                        'organizer': event.organizer.username,
                        'registration_count': event.registration_count,
                        'start_date': event.start_date,
                    }
                    for event in popular_events
                ]
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors du calcul des statistiques: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def all_events(self, request):
        """Récupérer tous les événements de la plateforme"""
        try:
            events = Event.objects.all().order_by('-created_at')
            
            # Filtrage optionnel
            status_filter = request.query_params.get('status')
            organizer_filter = request.query_params.get('organizer')
            
            if status_filter:
                events = events.filter(status=status_filter)
            if organizer_filter:
                events = events.filter(organizer__username__icontains=organizer_filter)
            
            # Pagination
            page_size = int(request.query_params.get('page_size', 20))
            page = int(request.query_params.get('page', 1))
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            total_count = events.count()
            events_page = events[start_idx:end_idx]
            
            serializer = EventListSerializer(events_page, many=True)
            
            return Response({
                'results': serializer.data,
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size,
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des événements: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def all_users(self, request):
        """Récupérer tous les utilisateurs de la plateforme"""
        try:
            users = User.objects.all().order_by('-date_joined')
            
            # Filtrage optionnel
            role_filter = request.query_params.get('role')
            search = request.query_params.get('search')
            
            if role_filter:
                users = users.filter(profile__role=role_filter)
            if search:
                users = users.filter(
                    Q(username__icontains=search) |
                    Q(email__icontains=search) |
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search)
                )
            
            # Pagination
            page_size = int(request.query_params.get('page_size', 20))
            page = int(request.query_params.get('page', 1))
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            total_count = users.count()
            users_page = users[start_idx:end_idx]
            
            users_data = []
            for user in users_page:
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'date_joined': user.date_joined,
                    'last_login': user.last_login,
                    'is_active': user.is_active,
                    'is_staff': user.is_staff,
                    'role': getattr(user.profile, 'role', 'unknown') if hasattr(user, 'profile') else 'no_profile',
                    'phone': getattr(user.profile, 'phone', '') if hasattr(user, 'profile') else '',
                }
                
                # Statistiques supplémentaires selon le rôle
                try:
                    profile = user.profile
                    if profile.role == 'organizer':
                        user_data['events_count'] = user.events_organized.count()
                        user_data['total_revenue'] = user.events_organized.aggregate(
                            revenue=Sum('registrations__price_paid')
                        ).get('revenue') or 0
                    elif profile.role == 'participant':
                        user_data['registrations_count'] = user.registrations.count()
                        user_data['events_attended'] = user.registrations.filter(
                            status='attended'
                        ).count()
                except UserProfile.DoesNotExist:
                    # L'utilisateur n'a pas de profil, utiliser des valeurs par défaut
                    user_data['events_count'] = 0
                    user_data['total_revenue'] = 0
                    user_data['registrations_count'] = 0
                    user_data['events_attended'] = 0
                
                users_data.append(user_data)
            
            return Response({
                'results': users_data,
                'total_count': total_count,
                'page': page,
                'page_size': page_size,
                'total_pages': (total_count + page_size - 1) // page_size,
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des utilisateurs: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def moderate_event(self, request):
        """Modérer un événement (approuver/rejeter/suspendre)"""
        try:
            event_id = request.data.get('event_id')
            action = request.data.get('action')  # 'approve', 'reject', 'suspend', 'publish'
            reason = request.data.get('reason', '')
            
            if not event_id or not action:
                return Response(
                    {'error': 'event_id et action sont requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                return Response(
                    {'error': 'Événement non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Actions de modération
            if action == 'approve':
                event.status = 'published'
                message = f"Événement approuvé par {request.user.username}"
            elif action == 'reject':
                event.status = 'cancelled'
                message = f"Événement rejeté par {request.user.username}: {reason}"
            elif action == 'suspend':
                event.status = 'draft'
                message = f"Événement suspendu par {request.user.username}: {reason}"
            elif action == 'publish':
                event.status = 'published'
                message = f"Événement publié par {request.user.username}"
            else:
                return Response(
                    {'error': 'Action non valide'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            event.save()
            
            # Enregistrer l'action dans l'historique
            from .models import EventHistory
            EventHistory.objects.create(
                event=event,
                action=action,
                field_name='status',
                old_value=event.status,
                new_value=event.status,
                user=request.user
            )
            
            return Response({
                'message': message,
                'event_status': event.status,
                'event_id': event.id,
                'action_performed': action,
                'timestamp': timezone.now()
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la modération: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def bulk_moderate_events(self, request):
        """Modérer plusieurs événements en lot"""
        try:
            event_ids = request.data.get('event_ids', [])
            action = request.data.get('action')  # 'approve', 'reject', 'suspend'
            reason = request.data.get('reason', '')
            
            if not event_ids or not action:
                return Response(
                    {'error': 'event_ids et action sont requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if action not in ['approve', 'reject', 'suspend']:
                return Response(
                    {'error': 'Action non valide'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            results = []
            for event_id in event_ids:
                try:
                    event = Event.objects.get(id=event_id)
                    
                    # Actions de modération
                    if action == 'approve':
                        event.status = 'published'
                        message = f"Événement approuvé par {request.user.username}"
                    elif action == 'reject':
                        event.status = 'cancelled'
                        message = f"Événement rejeté par {request.user.username}: {reason}"
                    elif action == 'suspend':
                        event.status = 'draft'
                        message = f"Événement suspendu par {request.user.username}: {reason}"
                    
                    event.save()
                    
                    # Enregistrer l'action dans l'historique
                    EventHistory.objects.create(
                        event=event,
                        action=action,
                        field_name='status',
                        old_value=event.status,
                        new_value=event.status,
                        user=request.user
                    )
                    
                    results.append({
                        'event_id': event.id,
                        'title': event.title,
                        'status': 'success',
                        'message': message
                    })
                    
                except Event.DoesNotExist:
                    results.append({
                        'event_id': event_id,
                        'status': 'error',
                        'message': 'Événement non trouvé'
                    })
                except Exception as e:
                    results.append({
                        'event_id': event_id,
                        'status': 'error',
                        'message': f'Erreur: {str(e)}'
                    })
            
            success_count = len([r for r in results if r['status'] == 'success'])
            error_count = len([r for r in results if r['status'] == 'error'])
            
            return Response({
                'message': f'Modération en lot terminée: {success_count} succès, {error_count} erreurs',
                'results': results,
                'summary': {
                    'total': len(event_ids),
                    'success': success_count,
                    'errors': error_count
                }
            })
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la modération en lot: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def event_history(self, request, pk=None):
        """Récupérer l'historique de modération d'un événement"""
        try:
            event = Event.objects.get(id=pk)
            history = event.history.all().order_by('-created_at')
            
            history_data = []
            for h in history:
                history_data.append({
                    'id': h.id,
                    'action': h.action,
                    'field_name': h.field_name,
                    'old_value': h.old_value,
                    'new_value': h.new_value,
                    'user': {
                        'id': h.user.id,
                        'username': h.user.username,
                        'first_name': h.user.first_name,
                        'last_name': h.user.last_name,
                    } if h.user else None,
                    'created_at': h.created_at,
                })
            
            return Response(history_data)
            
        except Event.DoesNotExist:
            return Response(
                {'error': 'Événement non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération de l\'historique: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def manage_user(self, request):
        """Gérer un utilisateur (suspendre/activer/changer rôle)"""
        try:
            # 🔧 DEBUG: Log des données reçues
            print(f"🔍 DEBUG: manage_user - Données reçues: {request.data}")
            print(f"🔍 DEBUG: manage_user - Utilisateur connecté: {request.user.username}")
            
            user_id = request.data.get('user_id')
            action = request.data.get('action')  # 'suspend', 'activate', 'change_role', 'delete'
            new_role = request.data.get('new_role')
            reason = request.data.get('reason', '')
            
            print(f"🔍 DEBUG: manage_user - user_id: {user_id}, action: {action}, new_role: {new_role}")
            
            # 🔧 DEBUG: Lister tous les utilisateurs disponibles
            all_users = User.objects.all()
            print(f"🔍 DEBUG: Utilisateurs disponibles: {[f'{u.id}:{u.username}' for u in all_users]}")
            
            if not user_id or not action:
                print(f"❌ DEBUG: Données manquantes - user_id: {user_id}, action: {action}")
                return Response(
                    {'error': 'user_id et action sont requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                print(f"🔍 DEBUG: Recherche de l'utilisateur avec ID: {user_id}")
                target_user = User.objects.get(id=user_id)
                print(f"✅ DEBUG: Utilisateur trouvé: {target_user.username}")
            except User.DoesNotExist:
                print(f"❌ DEBUG: Utilisateur avec ID {user_id} non trouvé")
                return Response(
                    {'error': 'Utilisateur non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                print(f"❌ DEBUG: Erreur lors de la recherche: {e}")
                return Response(
                    {'error': f'Erreur lors de la recherche: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Empêcher l'auto-gestion
            if target_user == request.user:
                return Response(
                    {'error': 'Vous ne pouvez pas vous gérer vous-même'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Actions de gestion
            print(f"🔍 DEBUG: Action demandée: {action}")
            
            if action == 'suspend':
                print(f"🔍 DEBUG: Suspension de l'utilisateur")
                target_user.is_active = False
                message = f"Utilisateur suspendu par {request.user.username}: {reason}"
            elif action == 'activate':
                print(f"🔍 DEBUG: Activation de l'utilisateur")
                target_user.is_active = True
                message = f"Utilisateur activé par {request.user.username}"
            elif action == 'change_role':
                print(f"🔍 DEBUG: Changement de rôle vers: {new_role}")
                
                if not new_role or new_role not in ['super_admin', 'organizer', 'participant', 'guest']:
                    print(f"❌ DEBUG: Rôle invalide: {new_role}")
                    return Response(
                        {'error': 'Nouveau rôle invalide'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                print(f"🔍 DEBUG: Rôle valide, modification des permissions Django")
                
                # 🔧 NOUVEAU: Modifier les vraies permissions Django
                if new_role == 'super_admin':
                    target_user.is_superuser = True
                    target_user.is_staff = True
                    print(f"🔧 DEBUG: {target_user.username} devient super admin")
                elif new_role == 'organizer':
                    target_user.is_superuser = False
                    target_user.is_staff = True
                    print(f"🔧 DEBUG: {target_user.username} devient organizer (staff)")
                else:
                    target_user.is_superuser = False
                    target_user.is_staff = False
                    print(f"🔧 DEBUG: {target_user.username} devient {new_role}")
                
                print(f"🔍 DEBUG: Création/modification du profil UserProfile")
                
                # Créer le profil s'il n'existe pas
                try:
                    profile, created = UserProfile.objects.get_or_create(
                        user=target_user,
                        defaults={'role': new_role}
                    )
                    if not created:
                        profile.role = new_role
                        profile.save()
                    print(f"✅ DEBUG: Profil UserProfile mis à jour: {profile.role}")
                except Exception as e:
                    print(f"❌ DEBUG: Erreur lors de la création/modification du profil: {e}")
                    return Response(
                        {'error': f'Erreur lors de la création du profil: {str(e)}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                message = f"Rôle changé vers {new_role} par {request.user.username}"
                print(f"✅ DEBUG: Message de succès: {message}")
            elif action == 'delete':
                # Attention: suppression définitive
                username = target_user.username
                target_user.delete()
                return Response({
                    'message': f"Utilisateur {username} supprimé définitivement par {request.user.username}"
                })
            else:
                print(f"❌ DEBUG: Action non valide: {action}")
                return Response(
                    {'error': 'Action non valide'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"🔍 DEBUG: Sauvegarde de l'utilisateur...")
            target_user.save()
            print(f"✅ DEBUG: Utilisateur sauvegardé avec succès")
            
            print(f"🔍 DEBUG: Préparation de la réponse...")
            response_data = {
                'message': message,
                'user_status': {
                    'is_active': target_user.is_active,
                    'role': getattr(target_user.profile, 'role', 'unknown') if hasattr(target_user, 'profile') else 'no_profile'
                }
            }
            print(f"✅ DEBUG: Réponse préparée: {response_data}")
            
            print(f"🔍 DEBUG: Envoi de la réponse...")
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la gestion utilisateur: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =====================================
# VUES FONCTION SUPPLÉMENTAIRES
# =====================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def platform_analytics(request):
    """Analytics avancées de la plateforme"""
    try:
        # Analyse temporelle (7 derniers jours)
        seven_days_ago = timezone.now() - timedelta(days=7)
        daily_stats = []
        
        for i in range(7):
            date = seven_days_ago + timedelta(days=i)
            day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            new_users = User.objects.filter(
                date_joined__gte=day_start,
                date_joined__lt=day_end
            ).count()
            
            new_events = Event.objects.filter(
                created_at__gte=day_start,
                created_at__lt=day_end
            ).count()
            
            new_registrations = EventRegistration.objects.filter(
                registered_at__gte=day_start,
                registered_at__lt=day_end
            ).count()
            
            daily_revenue = EventRegistration.objects.filter(
                registered_at__gte=day_start,
                registered_at__lt=day_end,
                payment_status='paid'
            ).aggregate(total=Sum('price_paid')).get('total') or 0
            
            daily_stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'new_users': new_users,
                'new_events': new_events,
                'new_registrations': new_registrations,
                'revenue': float(daily_revenue),
            })
        
        # Répartition des rôles
        role_distribution = {}
        for role_key, role_name in UserProfile.ROLE_CHOICES:
            count = UserProfile.objects.filter(role=role_key).count()
            role_distribution[role_key] = {
                'name': role_name,
                'count': count
            }
        
        # Top 10 événements par revenus
        top_revenue_events = Event.objects.annotate(
            total_revenue=Sum('registrations__price_paid')
        ).filter(
            total_revenue__gt=0
        ).order_by('-total_revenue')[:10]
        
        top_revenue_data = [
            {
                'id': event.id,
                'title': event.title,
                'organizer': event.organizer.username,
                'total_revenue': float(event.total_revenue or 0),
                'start_date': event.start_date,
            }
            for event in top_revenue_events
        ]
        
        # Statistiques de croissance (30 derniers jours)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        sixty_days_ago = timezone.now() - timedelta(days=60)
        
        # Croissance des utilisateurs
        users_30d = User.objects.filter(date_joined__gte=thirty_days_ago).count()
        users_60d = User.objects.filter(date_joined__gte=sixty_days_ago).count()
        users_growth = ((users_30d - (users_60d - users_30d)) / max(users_60d - users_30d, 1)) * 100 if users_60d > users_30d else 0
        
        # Croissance des événements
        events_30d = Event.objects.filter(created_at__gte=thirty_days_ago).count()
        events_60d = Event.objects.filter(created_at__gte=sixty_days_ago).count()
        events_growth = ((events_30d - (events_60d - events_30d)) / max(events_60d - events_30d, 1)) * 100 if events_60d > events_30d else 0
        
        # Croissance des revenus
        revenue_30d = EventRegistration.objects.filter(
            registered_at__gte=thirty_days_ago,
            payment_status='paid'
        ).aggregate(total=Sum('price_paid')).get('total') or 0
        
        revenue_60d = EventRegistration.objects.filter(
            registered_at__gte=sixty_days_ago,
            payment_status='paid'
        ).aggregate(total=Sum('price_paid')).get('total') or 0
        
        revenue_growth = ((revenue_30d - (revenue_60d - revenue_30d)) / max(revenue_60d - revenue_30d, 1)) * 100 if revenue_60d > revenue_30d else 0
        
        # Statistiques des remboursements
        pending_refunds = RefundRequest.objects.filter(status='pending').count()
        approved_refunds = RefundRequest.objects.filter(status='approved').count()
        rejected_refunds = RefundRequest.objects.filter(status='rejected').count()
        total_refund_amount = RefundRequest.objects.filter(
            status='approved'
        ).aggregate(total=Sum('refund_amount')).get('total') or 0
        
        # Performance des organisateurs
        top_organizers = User.objects.filter(
            events_organized__isnull=False
        ).annotate(
            event_count=Count('events_organized'),
            total_revenue=Sum('events_organized__registrations__price_paid')
        ).filter(
            event_count__gt=0
        ).order_by('-total_revenue')[:5]
        
        top_organizers_data = [
            {
                'id': user.id,
                'username': user.username,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'event_count': user.event_count,
                'total_revenue': float(user.total_revenue or 0),
                'email': user.email,
            }
            for user in top_organizers
        ]
        
        # Statistiques des événements par statut
        event_status_stats = {}
        for status_choice in Event.STATUS_CHOICES:
            status_key = status_choice[0]
            status_name = status_choice[1]
            count = Event.objects.filter(status=status_key).count()
            event_status_stats[status_key] = {
                'name': status_name,
                'count': count
            }
        
        # Statistiques des inscriptions par statut
        registration_status_stats = {}
        for status_choice in EventRegistration.STATUS_CHOICES:
            status_key = status_choice[0]
            status_name = status_choice[1]
            count = EventRegistration.objects.filter(status=status_key).count()
            registration_status_stats[status_key] = {
                'name': status_name,
                'count': count
            }
        
        return Response({
            'daily_stats': daily_stats,
            'role_distribution': role_distribution,
            'top_revenue_events': top_revenue_data,
            'top_organizers': top_organizers_data,
            'growth_metrics': {
                'users_growth': round(users_growth, 2),
                'events_growth': round(events_growth, 2),
                'revenue_growth': round(revenue_growth, 2)
            },
            'refund_stats': {
                'pending_refunds': pending_refunds,
                'approved_refunds': approved_refunds,
                'rejected_refunds': rejected_refunds,
                'total_refund_amount': float(total_refund_amount)
            },
            'event_status_stats': event_status_stats,
            'registration_status_stats': registration_status_stats,
            'summary': {
                'total_platform_users': User.objects.count(),
                'active_organizers': User.objects.filter(
                    profile__role='organizer',
                    is_active=True
                ).count(),
                'published_events': Event.objects.filter(status='published').count(),
                'this_month_revenue': float(revenue_30d),
                'total_events_this_month': events_30d,
                'new_users_this_month': users_30d
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors du calcul des analytics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def pending_moderation(request):
    """Récupérer les éléments en attente de modération"""
    try:
        # Événements en attente
        pending_events = Event.objects.filter(
            status='draft'
        ).select_related('organizer').order_by('-created_at')[:10]
        
        # Remboursements en attente
        pending_refunds = RefundRequest.objects.filter(
            status='pending'
        ).select_related('registration__event', 'registration__user').order_by('-created_at')[:10]
        
        events_data = [
            {
                'id': event.id,
                'title': event.title,
                'organizer': event.organizer.username,
                'organizer_email': event.organizer.email,
                'created_at': event.created_at,
                'start_date': event.start_date,
                'price': float(event.price),
            }
            for event in pending_events
        ]
        
        refunds_data = [
            {
                'id': refund.id,
                'event_title': refund.registration.event.title,
                'user': refund.registration.user.username,
                'amount': float(refund.refund_amount),
                'created_at': refund.created_at,
                'reason': refund.reason,
            }
            for refund in pending_refunds
        ]
        
        return Response({
            'pending_events': events_data,
            'pending_refunds': refunds_data,
            'counts': {
                'events': len(events_data),
                'refunds': len(refunds_data),
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la récupération des éléments en attente: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_refunds_list(request):
    """Liste des remboursements pour l'administration"""
    try:
        refunds = RefundRequest.objects.select_related(
            'registration__user',
            'registration__event',
            'processed_by'
        ).order_by('-created_at')
        
        # Filtrage
        status_filter = request.query_params.get('status')
        search = request.query_params.get('search')
        
        if status_filter:
            refunds = refunds.filter(status=status_filter)
        
        if search:
            refunds = refunds.filter(
                Q(registration__user__username__icontains=search) |
                Q(registration__user__email__icontains=search) |
                Q(registration__event__title__icontains=search) |
                Q(reason__icontains=search)
            )
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        total_count = refunds.count()
        refunds_page = refunds[start_idx:end_idx]
        
        refunds_data = []
        for refund in refunds_page:
            # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
            user_info = None
            if refund.registration.user:
                # Utilisateur connecté
                user_info = {
                    'id': refund.registration.user.id,
                    'username': refund.registration.user.username,
                    'email': refund.registration.user.email,
                    'first_name': refund.registration.user.first_name,
                    'last_name': refund.registration.user.last_name,
                    'is_guest': False
                }
            else:
                # Invité
                user_info = {
                    'id': None,
                    'username': refund.registration.guest_full_name or 'Invité',
                    'email': refund.registration.guest_email or 'Email inconnu',
                    'first_name': refund.registration.guest_full_name or 'Invité',
                    'last_name': '',
                    'is_guest': True
                }
            
            refund_data = {
                'id': refund.id,
                'status': refund.status,
                'reason': refund.reason,
                'amount_paid': float(refund.amount_paid),
                'refund_percentage': refund.refund_percentage,
                'refund_amount': float(refund.refund_amount),
                'created_at': refund.created_at,
                'expires_at': refund.expires_at,
                'processed_at': refund.processed_at,
                'stripe_refund_id': refund.stripe_refund_id,
                'user': user_info,  # 🎯 CORRECTION : Utiliser user_info au lieu de registration.user
                'event': {
                    'id': refund.registration.event.id,
                    'title': refund.registration.event.title,
                    'start_date': refund.registration.event.start_date,
                    'location': refund.registration.event.location,
                    'organizer': {
                        'username': refund.registration.event.organizer.username,
                    }
                },
                'processed_by': {
                    'id': refund.processed_by.id,
                    'username': refund.processed_by.username,
                    'email': refund.processed_by.email,
                } if refund.processed_by else None
            }
            refunds_data.append(refund_data)
        
        return Response({
            'results': refunds_data,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la récupération des remboursements: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_process_refund(request):
    """Traiter un remboursement (approuver/rejeter/traiter)"""
    try:
        refund_id = request.data.get('refund_id')
        action = request.data.get('action')  # 'approve', 'reject', 'process'
        reason = request.data.get('reason', '')
        
        if not refund_id or not action:
            return Response(
                {'error': 'refund_id et action sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            refund = RefundRequest.objects.get(id=refund_id)
        except RefundRequest.DoesNotExist:
            return Response(
                {'error': 'Remboursement non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Actions de traitement
        if action == 'approve':
            if refund.status != 'pending':
                return Response(
                    {'error': 'Seuls les remboursements en attente peuvent être approuvés'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            refund.status = 'approved'
            message = f"Remboursement approuvé par {request.user.username}"
            
        elif action == 'reject':
            if refund.status != 'pending':
                return Response(
                    {'error': 'Seuls les remboursements en attente peuvent être rejetés'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            refund.status = 'rejected'
            message = f"Remboursement rejeté par {request.user.username}: {reason}"
            
        elif action == 'process':
            if refund.status != 'approved':
                return Response(
                    {'error': 'Seuls les remboursements approuvés peuvent être traités'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            refund.status = 'processed'
            refund.processed_at = timezone.now()
            refund.processed_by = request.user
            message = f"Remboursement traité par {request.user.username}"
            
        else:
            return Response(
                {'error': 'Action non valide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        refund.save()
        
        return Response({
            'message': message,
            'refund_status': refund.status,
            'refund_id': refund.id,
            'action_performed': action,
            'timestamp': timezone.now()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors du traitement: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_bulk_process_refunds(request):
    """Traiter plusieurs remboursements en lot"""
    try:
        refund_ids = request.data.get('refund_ids', [])
        action = request.data.get('action')  # 'approve', 'reject'
        reason = request.data.get('reason', '')
        
        if not refund_ids or not action:
            return Response(
                {'error': 'refund_ids et action sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action not in ['approve', 'reject']:
            return Response(
                {'error': 'Action non valide'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = []
        for refund_id in refund_ids:
            try:
                refund = RefundRequest.objects.get(id=refund_id)
                
                # Vérifier que le remboursement peut être traité
                if refund.status != 'pending':
                    results.append({
                        'refund_id': refund.id,
                        'status': 'error',
                        'message': f'Statut invalide: {refund.status}'
                    })
                    continue
                
                # Actions de traitement
                if action == 'approve':
                    refund.status = 'approved'
                    message = f"Remboursement approuvé par {request.user.username}"
                elif action == 'reject':
                    refund.status = 'rejected'
                    message = f"Remboursement rejeté par {request.user.username}: {reason}"
                
                refund.save()
                
                results.append({
                    'refund_id': refund.id,
                    'status': 'success',
                    'message': message
                })
                
            except RefundRequest.DoesNotExist:
                results.append({
                    'refund_id': refund_id,
                    'status': 'error',
                    'message': 'Remboursement non trouvé'
                })
            except Exception as e:
                results.append({
                    'refund_id': refund_id,
                    'status': 'error',
                    'message': f'Erreur: {str(e)}'
                })
        
        success_count = len([r for r in results if r['status'] == 'success'])
        error_count = len([r for r in results if r['status'] == 'error'])
        
        return Response({
            'message': f'Traitement en lot terminé: {success_count} succès, {error_count} erreurs',
            'results': results,
            'summary': {
                'total': len(refund_ids),
                'success': success_count,
                'errors': error_count
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors du traitement en lot: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def pending_registrations(request):
    """Récupérer les inscriptions en attente de confirmation"""
    try:
        # Inscriptions en attente (pending)
        pending_registrations = EventRegistration.objects.filter(
            status='pending'
        ).select_related(
            'event', 
            'user', 
            'ticket_type'
        ).order_by('-registered_at')
        
        # Filtrage
        event_filter = request.query_params.get('event_id')
        search = request.query_params.get('search')
        
        if event_filter:
            pending_registrations = pending_registrations.filter(event_id=event_filter)
        
        if search:
            pending_registrations = pending_registrations.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(event__title__icontains=search)
            )
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 20))
        page = int(request.query_params.get('page', 1))
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        total_count = pending_registrations.count()
        registrations_page = pending_registrations[start_idx:end_idx]
        
        registrations_data = []
        for registration in registrations_page:
            registration_data = {
                'id': registration.id,
                'event': {
                    'id': registration.event.id,
                    'title': registration.event.title,
                    'start_date': registration.event.start_date,
                    'price': float(registration.event.price),
                },
                'user': {
                    'id': registration.user.id,
                    'username': registration.user.username,
                    'email': registration.user.email,
                    'first_name': registration.user.first_name,
                    'last_name': registration.user.last_name,
                },
                'ticket_type': {
                    'id': registration.ticket_type.id,
                    'name': registration.ticket_type.name,
                } if registration.ticket_type else None,
                'price_paid': float(registration.price_paid),
                'payment_status': registration.payment_status,
                'registered_at': registration.registered_at,
                'notes': registration.notes,
                'special_requirements': registration.special_requirements,
            }
            registrations_data.append(registration_data)
        
        return Response({
            'pending_registrations': registrations_data,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la récupération des inscriptions en attente: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def confirm_registration(request):
    """Confirmer une inscription en attente"""
    try:
        registration_id = request.data.get('registration_id')
        if not registration_id:
            return Response(
                {'error': 'ID d\'inscription requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            registration = EventRegistration.objects.select_related('event', 'ticket_type').get(id=registration_id)
        except EventRegistration.DoesNotExist:
            return Response(
                {'error': 'Inscription non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if registration.status != 'pending':
            return Response(
                {'error': 'Cette inscription n\'est pas en attente de confirmation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier la capacité de l'événement
        event = registration.event
        if event.place_type == 'limited' and event.max_capacity is not None:
            current_confirmed = event.registrations.filter(status__in=['confirmed', 'attended']).count()
            if current_confirmed >= event.max_capacity:
                return Response(
                    {'error': 'L\'événement a atteint sa capacité maximale'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Vérifier la capacité du type de billet
        if registration.ticket_type and registration.ticket_type.quantity is not None:
            if registration.ticket_type.sold_count >= registration.ticket_type.quantity:
                return Response(
                    {'error': 'Ce type de billet n\'est plus disponible'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Confirmer l'inscription
        registration.status = 'confirmed'
        registration.confirmed_at = timezone.now()
        registration.save(update_fields=['status', 'confirmed_at', 'updated_at'])
        
        # Mettre à jour les compteurs
        if event.place_type == 'limited' and event.max_capacity is not None:
            event.current_registrations = (event.current_registrations or 0) + 1
            event.save(update_fields=['current_registrations'])
        
        if registration.ticket_type:
            ticket_type = registration.ticket_type
            ticket_type.sold_count = ticket_type.sold_count + 1
            ticket_type.save(update_fields=['sold_count'])
        
        # Créer un historique
        from .models import EventHistory
        EventHistory.objects.create(
            event=event,
            user=request.user,
            action='registration_confirmed',
            field_name='status',
            old_value='pending',
            new_value='confirmed',
            details=f'Inscription confirmée par {request.user.username}'
        )
        
        return Response({
            'message': 'Inscription confirmée avec succès',
            'registration_id': registration.id,
            'status': 'confirmed'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la confirmation: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def reject_registration(request):
    """Rejeter une inscription en attente"""
    try:
        registration_id = request.data.get('registration_id')
        reason = request.data.get('reason', 'Aucune raison fournie')
        
        if not registration_id:
            return Response(
                {'error': 'ID d\'inscription requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            registration = EventRegistration.objects.select_related('event').get(id=registration_id)
        except EventRegistration.DoesNotExist:
            return Response(
                {'error': 'Inscription non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if registration.status != 'pending':
            return Response(
                {'error': 'Cette inscription n\'est pas en attente de confirmation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rejeter l'inscription
        registration.status = 'cancelled'
        registration.cancelled_at = timezone.now()
        registration.save(update_fields=['status', 'cancelled_at', 'updated_at'])
        
        # Créer un historique
        from .models import EventHistory
        EventHistory.objects.create(
            event=registration.event,
            user=request.user,
            action='registration_rejected',
            field_name='status',
            old_value='pending',
            new_value='cancelled',
            details=f'Inscription rejetée par {request.user.username}. Raison: {reason}'
        )
        
        return Response({
            'message': 'Inscription rejetée avec succès',
            'registration_id': registration.id,
            'status': 'cancelled'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors du rejet: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def bulk_confirm_registrations(request):
    """Confirmer plusieurs inscriptions en attente"""
    try:
        registration_ids = request.data.get('registration_ids', [])
        if not registration_ids:
            return Response(
                {'error': 'Liste d\'IDs d\'inscriptions requise'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = {
            'confirmed': [],
            'failed': [],
            'errors': []
        }
        
        for registration_id in registration_ids:
            try:
                registration = EventRegistration.objects.select_related('event', 'ticket_type').get(id=registration_id)
                
                if registration.status != 'pending':
                    results['failed'].append({
                        'id': registration_id,
                        'error': 'Inscription non en attente'
                    })
                    continue
                
                # Vérifier la capacité
                event = registration.event
                if event.place_type == 'limited' and event.max_capacity is not None:
                    current_confirmed = event.registrations.filter(status__in=['confirmed', 'attended']).count()
                    if current_confirmed >= event.max_capacity:
                        results['failed'].append({
                            'id': registration_id,
                            'error': 'Événement à capacité maximale'
                        })
                        continue
                
                # Vérifier la capacité du type de billet
                if registration.ticket_type and registration.ticket_type.quantity is not None:
                    if registration.ticket_type.sold_count >= registration.ticket_type.quantity:
                        results['failed'].append({
                            'id': registration_id,
                            'error': 'Type de billet indisponible'
                        })
                        continue
                
                # Confirmer
                registration.status = 'confirmed'
                registration.confirmed_at = timezone.now()
                registration.save(update_fields=['status', 'confirmed_at', 'updated_at'])
                
                # Mettre à jour les compteurs
                if event.place_type == 'limited' and event.max_capacity is not None:
                    event.current_registrations = (event.current_registrations or 0) + 1
                    event.save(update_fields=['current_registrations'])
                
                if registration.ticket_type:
                    ticket_type = registration.ticket_type
                    ticket_type.sold_count = ticket_type.sold_count + 1
                    ticket_type.save(update_fields=['sold_count'])
                
                # Créer un historique
                from .models import EventHistory
                EventHistory.objects.create(
                    event=event,
                    user=request.user,
                    action='registration_confirmed_bulk',
                    field_name='status',
                    old_value='pending',
                    new_value='confirmed',
                    details=f'Inscription confirmée en lot par {request.user.username}'
                )
                
                results['confirmed'].append(registration_id)
                
            except EventRegistration.DoesNotExist:
                results['failed'].append({
                    'id': registration_id,
                    'error': 'Inscription non trouvée'
                })
            except Exception as e:
                results['errors'].append({
                    'id': registration_id,
                    'error': str(e)
                })
        
        return Response({
            'message': f'Opération terminée. {len(results["confirmed"])} confirmées, {len(results["failed"])} échouées',
            'results': results
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la confirmation en lot: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =====================================
# ANALYTICS PRÉDICTIFS AVANCÉS
# =====================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def predictive_analytics_dashboard(request):
    """Dashboard des analytics prédictifs avancés"""
    try:
        print("🔍 DEBUG: Début de predictive_analytics_dashboard")
        
        from .predictive_analytics import get_predictive_service
        print("🔍 DEBUG: Import get_predictive_service réussi")
        
        # Récupérer une instance du service
        predictive_service = get_predictive_service()
        print("🔍 DEBUG: Service créé avec succès")
        
        # Récupérer les paramètres
        event_id = request.query_params.get('event_id')
        days_back = int(request.query_params.get('days_back', 90))
        print(f"🔍 DEBUG: Paramètres - event_id: {event_id}, days_back: {days_back}")
        
        # Insights prédictifs
        print("🔍 DEBUG: Appel get_predictive_insights...")
        insights = predictive_service.get_predictive_insights(event_id)
        print("🔍 DEBUG: get_predictive_insights terminé")
        
        # Détection des tendances
        print("🔍 DEBUG: Appel detect_emerging_trends...")
        trends = predictive_service.detect_emerging_trends(days_back)
        print("🔍 DEBUG: detect_emerging_trends terminé")
        
        # Statistiques des modèles ML
        print("🔍 DEBUG: Vérification des modèles ML...")
        model_status = {
            'fill_rate_predictor': 'available' if os.path.exists(os.path.join(settings.BASE_DIR, 'ml_models', 'fill_rate_predictor.joblib')) else 'not_trained',
            'last_training': None
        }
        
        # Vérifier la date du dernier entraînement
        model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'fill_rate_predictor.joblib')
        if os.path.exists(model_path):
            model_age = timezone.now() - datetime.fromtimestamp(os.path.getmtime(model_path), tz=timezone.utc)
            model_status['last_training'] = model_age.days
        
        print("🔍 DEBUG: Préparation de la réponse...")
        return Response({
            'status': 'success',
            'timestamp': timezone.now().isoformat(),
            'insights': insights,
            'trends': trends,
            'model_status': model_status,
            'summary': {
                'total_insights': len(insights.get('global_insights', [])),
                'emerging_trends': len(trends.get('emerging_trends', [])),
                'categories_analyzed': len(trends.get('category_trends', [])),
                'tags_analyzed': len(trends.get('tag_trends', []))
            }
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ ERREUR DÉTAILLÉE: {str(e)}")
        print(f"❌ TRACEBACK: {error_details}")
        return Response(
            {'error': f'Erreur lors du chargement des analytics prédictifs: {str(e)}', 'details': error_details},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def train_ml_models(request):
    """Entraîne ou retraîne les modèles de machine learning"""
    try:
        from .predictive_analytics import get_predictive_service
        
        # Récupérer une instance du service
        predictive_service = get_predictive_service()
        
        force_retrain = request.data.get('force_retrain', False)
        
        # Entraîner le modèle de prédiction de remplissage
        training_result = predictive_service.train_fill_rate_predictor(force_retrain)
        
        return Response({
            'status': 'success',
            'training_result': training_result,
            'message': 'Entraînement des modèles terminé'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'entraînement: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def predict_event_fill_rate(request):
    """Prédit le taux de remplissage d'un événement"""
    try:
        from .predictive_analytics import get_predictive_service
        
        # Récupérer une instance du service
        predictive_service = get_predictive_service()
        
        event_id = request.data.get('event_id')
        if not event_id:
            return Response(
                {'error': 'ID de l\'événement requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer les données de l'événement
        from .models import Event
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {'error': 'Événement non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Préparer les données pour la prédiction
        event_data = {
            'id': event.id,
            'price': float(event.price),
            'max_capacity': event.max_capacity or 100,
            'category': event.category.name if event.category else '',
            'city': event.location.split(',')[0] if event.location else '',
            'country': event.location.split(',')[-1].strip() if event.location else '',
            'start_date': event.start_date,
            'duration_hours': 2,  # Valeur par défaut
            'organizer_events_count': event.organizer.events_organized.count() if event.organizer else 0,
            'organizer_avg_rating': getattr(event.organizer.profile, 'rating', 0) if event.organizer and hasattr(event.organizer, 'profile') else 0,
            'tags_count': event.tags.count()
        }
        
        # Effectuer la prédiction
        prediction_result = predictive_service.predict_event_fill_rate(event_data)
        
        return Response({
            'status': 'success',
            'event_id': event_id,
            'event_title': event.title,
            'prediction': prediction_result
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la prédiction: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def optimize_event_pricing(request):
    """Optimise le prix d'un événement"""
    try:
        from .predictive_analytics import get_predictive_service
        
        # Récupérer une instance du service
        predictive_service = get_predictive_service()
        
        event_id = request.data.get('event_id')
        target_fill_rate = float(request.data.get('target_fill_rate', 0.8))
        
        if not event_id:
            return Response(
                {'error': 'ID de l\'événement requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer les données de l'événement
        from .models import Event
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {'error': 'Événement non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Préparer les données pour l'optimisation
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
        
        # Effectuer l'optimisation des prix
        optimization_result = predictive_service.optimize_event_pricing(event_data, target_fill_rate)
        
        return Response({
            'status': 'success',
            'event_id': event_id,
            'event_title': event.title,
            'optimization': optimization_result
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'optimisation: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsOrganizerOrSuperAdmin])
def generate_event_content(request):
    """Génère automatiquement du contenu pour un événement"""
    try:
        from .content_generator import get_content_generator
        
        # Récupérer le générateur de contenu
        generator = get_content_generator()
        
        # Récupérer les données de la requête
        title = request.data.get('title', '')
        category = request.data.get('category', '')
        location = request.data.get('location', '')
        price = float(request.data.get('price', 0))
        max_capacity = request.data.get('max_capacity')
        if max_capacity:
            max_capacity = int(max_capacity)
        
        if not title or not category or not location:
            return Response(
                {'error': 'Titre, catégorie et lieu sont requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Générer le contenu automatiquement
        description = generator.generate_event_description(
            title=title,
            category=category,
            location=location,
            price=price,
            max_capacity=max_capacity
        )
        
        hashtags = generator.generate_hashtags(
            title=title,
            category=category,
            description=description
        )
        
        visual_suggestions = generator.generate_visual_suggestions(
            category=category,
            title=title,
            description=description
        )
        
        return Response({
            'status': 'success',
            'generated_content': {
                'description': description,
                'hashtags': hashtags,
                'visual_suggestions': visual_suggestions
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la génération de contenu: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def get_emerging_trends(request):
    """Récupère les tendances émergentes"""
    try:
        from .predictive_analytics import get_predictive_service
        
        # Récupérer une instance du service
        predictive_service = get_predictive_service()
        
        days_back = int(request.query_params.get('days_back', 90))
        
        # Détecter les tendances
        trends_result = predictive_service.detect_emerging_trends(days_back)
        
        return Response({
            'status': 'success',
            'trends': trends_result
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la détection des tendances: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def get_market_analysis(request):
    """Analyse la concurrence sur le marché pour un événement"""
    try:
        from .predictive_analytics import get_predictive_service
        
        # Récupérer une instance du service
        predictive_service = get_predictive_service()
        
        event_id = request.query_params.get('event_id')
        if not event_id:
            return Response(
                {'error': 'ID de l\'événement requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer les données de l'événement
        from .models import Event
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {'error': 'Événement non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Préparer les données pour l'analyse
        event_data = {
            'id': event.id,
            'price': float(event.price),
            'max_capacity': event.max_capacity or 100,
            'category': event.category.name if event.category else '',
            'city': event.location.split(',')[0] if event.location else '',
            'country': event.location.split(',')[-1].strip() if event.location else '',
            'start_date': event.start_date
        }
        
        # Effectuer l'analyse de la concurrence
        market_analysis = predictive_service.analyze_market_competition(event_data)
        
        return Response({
            'status': 'success',
            'event_id': event_id,
            'event_title': event.title,
            'market_analysis': market_analysis
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'analyse du marché: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def get_predictive_insights(request):
    """Génère des insights prédictifs"""
    try:
        from .predictive_analytics import get_predictive_service
        
        # Récupérer une instance du service
        predictive_service = get_predictive_service()
        
        event_id = request.query_params.get('event_id')
        
        # Générer les insights
        insights = predictive_service.get_predictive_insights(event_id)
        
        return Response({
            'status': 'success',
            'insights': insights
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la génération des insights: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def pending_organizer_approvals(request):
    """Liste des comptes organisateurs en attente d'approbation"""
    try:
        pending_profiles = UserProfile.objects.filter(
            role='organizer',
            status_approval='pending'
        ).select_related('user').order_by('user__date_joined')
        
        data = []
        for profile in pending_profiles:
            data.append({
                'id': profile.id,
                'user_id': profile.user.id,
                'username': profile.user.username,
                'email': profile.user.email,
                'first_name': profile.user.first_name,
                'last_name': profile.user.last_name,
                'phone': profile.phone,
                'role': profile.role,
                'status_approval': profile.status_approval,
                'date_joined': profile.user.date_joined,
                'rejection_reason': profile.rejection_reason
            })
        
        return Response({
            'pending_approvals': data,
            'count': len(data)
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la récupération des approbations: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def approve_organizer_account(request):
    """Approuver un compte organisateur"""
    try:
        profile_id = request.data.get('profile_id')
        if not profile_id:
            return Response(
                {'error': 'ID du profil requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            profile = UserProfile.objects.get(id=profile_id, role='organizer')
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Profil organisateur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if profile.status_approval != 'pending':
            return Response(
                {'error': 'Ce compte n\'est pas en attente d\'approbation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Approuver le compte
        profile.status_approval = 'approved'
        profile.approved_by = request.user
        profile.save()
        
        # Envoyer un email de confirmation
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = 'Votre compte organisateur a été approuvé !'
            message_body = f"""
            Bonjour {profile.user.first_name},

            Excellente nouvelle ! Votre compte organisateur a été approuvé par un administrateur.

            Vous pouvez maintenant vous connecter et commencer à créer et gérer vos événements.

            Détails du compte :
            - Nom d'utilisateur : {profile.user.username}
            - Email : {profile.user.email}
            - Rôle : Organisateur

            Connectez-vous dès maintenant sur EventManager !

            L'équipe EventManager
            """
            
            send_mail(
                subject,
                message_body,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@eventmanager.com'),
                [profile.user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email d'approbation: {e}")
        
        return Response({
            'message': f'Compte de {profile.user.username} approuvé avec succès',
            'profile': {
                'id': profile.id,
                'username': profile.user.username,
                'email': profile.user.email,
                'status_approval': profile.status_approval,
                'approval_date': profile.approval_date
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'approbation: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def reject_organizer_account(request):
    """Rejeter un compte organisateur"""
    try:
        profile_id = request.data.get('profile_id')
        rejection_reason = request.data.get('rejection_reason', '')
        
        if not profile_id:
            return Response(
                {'error': 'ID du profil requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            profile = UserProfile.objects.get(id=profile_id, role='organizer')
        except UserProfile.DoesNotExist:
            return Response(
                {'error': 'Profil organisateur non trouvé'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if profile.status_approval != 'pending':
            return Response(
                {'error': 'Ce compte n\'est pas en attente d\'approbation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rejeter le compte
        profile.status_approval = 'rejected'
        profile.rejection_reason = rejection_reason
        profile.save()
        
        # Envoyer un email de rejet
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = 'Votre demande de compte organisateur'
            message_body = f"""
            Bonjour {profile.user.first_name},

            Nous avons examiné votre demande de compte organisateur et regrettons de vous informer qu'elle n'a pas été approuvée.

            Raison du rejet :
            {rejection_reason if rejection_reason else 'Aucune raison spécifiée'}

            Si vous pensez qu'il s'agit d'une erreur ou si vous souhaitez plus d'informations, 
            n'hésitez pas à nous contacter.

            Vous pouvez toujours créer un compte participant pour participer aux événements.

            L'équipe EventManager
            """
            
            send_mail(
                subject,
                message_body,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@eventmanager.com'),
                [profile.user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email de rejet: {e}")
        
        return Response({
            'message': f'Compte de {profile.user.username} rejeté',
            'profile': {
                'id': profile.id,
                'username': profile.user.username,
                'email': profile.user.email,
                'status_approval': profile.status_approval,
                'rejection_reason': profile.rejection_reason
            }
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors du rejet: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


