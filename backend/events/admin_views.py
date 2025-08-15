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

from .models import Event, EventRegistration, UserProfile, RefundRequest
from .permissions import IsSuperAdmin, super_admin_required
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
            total_revenue = EventRegistration.objects.filter(
                payment_status='paid'
            ).exclude(
                refund_request__status='processed'
            ).aggregate(total=Sum('price_paid')).get('total') or 0
            
            # Remboursements
            total_refunds = RefundRequest.objects.filter(status='processed').count()
            total_refund_amount = RefundRequest.objects.filter(
                status='processed'
            ).aggregate(total=Sum('refund_amount')).get('total') or 0
            
            # Statistiques de modération
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
            
            # Statistiques sur 30 derniers jours
            thirty_days_ago = timezone.now() - timedelta(days=30)
            new_users_30d = User.objects.filter(date_joined__gte=thirty_days_ago).count()
            new_events_30d = Event.objects.filter(created_at__gte=thirty_days_ago).count()
            new_registrations_30d = EventRegistration.objects.filter(
                registered_at__gte=thirty_days_ago
            ).count()
            
            # Top organisateurs (par nombre d'événements)
            top_organizers = User.objects.filter(
                events_organized__isnull=False
            ).annotate(
                event_count=Count('events_organized')
            ).order_by('-event_count')[:5]
            
            # Événements les plus populaires
            popular_events = Event.objects.filter(
                status='published'
            ).annotate(
                registration_count=Count('registrations')
            ).order_by('-registration_count')[:5]
            
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
            user_id = request.data.get('user_id')
            action = request.data.get('action')  # 'suspend', 'activate', 'change_role', 'delete'
            new_role = request.data.get('new_role')
            reason = request.data.get('reason', '')
            
            if not user_id or not action:
                return Response(
                    {'error': 'user_id et action sont requis'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                target_user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Utilisateur non trouvé'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Empêcher l'auto-gestion
            if target_user == request.user:
                return Response(
                    {'error': 'Vous ne pouvez pas vous gérer vous-même'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Actions de gestion
            if action == 'suspend':
                target_user.is_active = False
                message = f"Utilisateur suspendu par {request.user.username}: {reason}"
            elif action == 'activate':
                target_user.is_active = True
                message = f"Utilisateur activé par {request.user.username}"
            elif action == 'change_role':
                if not new_role or new_role not in ['super_admin', 'organizer', 'participant', 'guest']:
                    return Response(
                        {'error': 'Nouveau rôle invalide'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Créer le profil s'il n'existe pas
                profile, created = UserProfile.objects.get_or_create(
                    user=target_user,
                    defaults={'role': new_role}
                )
                if not created:
                    profile.role = new_role
                    profile.save()
                message = f"Rôle changé vers {new_role} par {request.user.username}"
            elif action == 'delete':
                # Attention: suppression définitive
                username = target_user.username
                target_user.delete()
                return Response({
                    'message': f"Utilisateur {username} supprimé définitivement par {request.user.username}"
                })
            else:
                return Response(
                    {'error': 'Action non valide'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            target_user.save()
            
            return Response({
                'message': message,
                'user_status': {
                    'is_active': target_user.is_active,
                    'role': getattr(target_user.profile, 'role', 'unknown') if hasattr(target_user, 'profile') else 'no_profile'
                }
            })
            
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
            ).exclude(
                refund_request__status='processed'
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
        ).exclude(
            refund_request__status='processed'
        ).aggregate(total=Sum('price_paid')).get('total') or 0
        
        revenue_60d = EventRegistration.objects.filter(
            registered_at__gte=sixty_days_ago,
            payment_status='paid'
        ).exclude(
            refund_request__status='processed'
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


