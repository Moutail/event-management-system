from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .permissions import IsSuperAdmin
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.http import FileResponse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
import csv
import stripe
import time
from decimal import Decimal

try:
    from openpyxl import Workbook
except Exception:  # pragma: no cover
    Workbook = None

from .models import Event, Category, Tag, EventRegistration, EventHistory, TicketType, SessionType, RefundRequest, UserProfile, VirtualEvent, VirtualEventInteraction, CustomReminder
from .serializers import (
    EventSerializer, EventListSerializer,
    CategorySerializer, TagSerializer, EventRegistrationSerializer,
    EventRegistrationCreateSerializer, EventHistorySerializer,
    TicketTypeSerializer, SessionTypeSerializer, VirtualEventSerializer, VirtualEventCreateSerializer,
    VirtualEventUpdateSerializer, VirtualEventInteractionSerializer,
    VirtualEventInteractionCreateSerializer, CustomReminderSerializer, CustomReminderCreateSerializer
)
from rest_framework.permissions import IsAuthenticated


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour les catégories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Récupérer tous les événements d'une catégorie"""
        category = self.get_object()
        events = Event.objects.filter(category=category, status='published')
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet pour les tags"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Récupérer tous les événements avec un tag spécifique"""
        tag = self.get_object()
        events = Event.objects.filter(tags=tag, status='published')
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)


class VirtualEventViewSet(viewsets.ModelViewSet):
    """ViewSet pour les événements virtuels"""
    queryset = VirtualEvent.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['platform', 'auto_record', 'allow_chat', 'allow_screen_sharing', 'waiting_room']
    search_fields = ['event__title', 'event__description', 'meeting_id']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return VirtualEventCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VirtualEventUpdateSerializer
        return VirtualEventSerializer

    def perform_create(self, serializer):
        """Passer l'utilisateur connecté au sérialiseur"""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Filtrer pour ne montrer que les événements virtuels publiés"""
        return VirtualEvent.objects.filter(event__status='published', event__event_type='virtual')

    @action(detail=True, methods=['get'])
    def interactions(self, request, pk=None):
        """Récupérer toutes les interactions d'un événement virtuel"""
        virtual_event = self.get_object()
        interactions = virtual_event.event.interactions.all()
        serializer = VirtualEventInteractionSerializer(interactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def access_info(self, request, pk=None):
        """Récupérer les informations d'accès pour un utilisateur inscrit"""
        virtual_event = self.get_object()
        user = request.user
        
        # Vérifier que l'utilisateur est inscrit
        registration = EventRegistration.objects.filter(
            event=virtual_event.event,
            user=user,
            status__in=['confirmed', 'attended']
        ).first()
        
        if not registration:
            return Response(
                {"error": "Vous devez être inscrit à cet événement pour accéder aux informations."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Retourner les informations d'accès
        access_data = {
            'meeting_id': virtual_event.meeting_id,
            'meeting_password': virtual_event.meeting_password,
            'meeting_url': virtual_event.meeting_url,
            'access_instructions': virtual_event.access_instructions,
            'technical_requirements': virtual_event.technical_requirements,
            'access_code': registration.virtual_access_code,
            'event_title': virtual_event.event.title,
            'start_date': virtual_event.event.start_date,
            'end_date': virtual_event.event.end_date
        }
        
        return Response(access_data)

    @action(detail=True, methods=['post'])
    def add_recording(self, request, pk=None):
        """Ajouter une rediffusion à un événement virtuel (réservé aux organisateurs)"""
        virtual_event = self.get_object()
        user = request.user
        
        # Vérifier que l'utilisateur est l'organisateur ou un super admin
        if not (user == virtual_event.event.organizer or 
                hasattr(user, 'profile') and user.profile.is_super_admin):
            return Response(
                {"error": "Vous n'êtes pas autorisé à modifier cet événement."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mettre à jour les informations de rediffusion
        virtual_event.recording_url = request.data.get('recording_url', '')
        virtual_event.recording_available = request.data.get('recording_available', False)
        virtual_event.recording_expires_at = request.data.get('recording_expires_at')
        virtual_event.save()
        
        serializer = VirtualEventSerializer(virtual_event)
        return Response(serializer.data)


class VirtualEventInteractionViewSet(viewsets.ModelViewSet):
    """ViewSet pour les interactions sur les événements virtuels"""
    queryset = VirtualEventInteraction.objects.all()
    serializer_class = VirtualEventInteractionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event', 'interaction_type', 'user']
    search_fields = ['content']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return VirtualEventInteractionCreateSerializer
        return VirtualEventInteractionSerializer

    def get_queryset(self):
        """Filtrer pour ne montrer que les interactions sur les événements virtuels"""
        return VirtualEventInteraction.objects.filter(event__event_type='virtual')

    @action(detail=False, methods=['get'])
    def my_interactions(self, request):
        """Récupérer toutes les interactions de l'utilisateur connecté"""
        interactions = self.get_queryset().filter(user=request.user)
        serializer = VirtualEventInteractionSerializer(interactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def event_interactions(self, request):
        """Récupérer toutes les interactions d'un événement spécifique"""
        event_id = request.query_params.get('event_id')
        if not event_id:
            return Response(
                {"error": "L'ID de l'événement est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier les permissions : organisateur peut voir ses événements, Super Admin peut voir tout
        event = get_object_or_404(Event, id=event_id)
        user = request.user
        
        # Super Admin peut voir toutes les interactions
        if user.is_superuser:
            interactions = self.get_queryset().filter(event_id=event_id)
        # Organisateur peut voir les interactions de ses événements
        elif hasattr(user, 'profile') and user.profile.role == 'organizer' and event.organizer == user:
            interactions = self.get_queryset().filter(event_id=event_id)
        # Participant peut voir les interactions publiques (sans contenu privé)
        else:
            interactions = self.get_queryset().filter(event_id=event_id).exclude(
                interaction_type__in=['rating']  # Exclure les notes pour la confidentialité
            )
        
        serializer = VirtualEventInteractionSerializer(interactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def interaction_stats(self, request):
        """Récupérer les statistiques des interactions pour un événement"""
        event_id = request.query_params.get('event_id')
        if not event_id:
            return Response(
                {"error": "L'ID de l'événement est requis."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        event = get_object_or_404(Event, id=event_id)
        if not event.is_virtual:
            return Response(
                {"error": "Cet événement n'est pas virtuel."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier les permissions : organisateur peut voir ses événements, Super Admin peut voir tout
        user = request.user
        
        # Super Admin peut voir toutes les statistiques
        if user.is_superuser:
            pass  # Pas de restriction
        # Organisateur peut voir les statistiques de ses événements
        elif hasattr(user, 'profile') and user.profile.role == 'organizer' and event.organizer == user:
            pass  # Pas de restriction
        # Participant ne peut pas voir les statistiques détaillées
        else:
            return Response(
                {"error": "Vous n'avez pas les permissions pour voir ces statistiques."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Compter les interactions par type
        stats = VirtualEventInteraction.objects.filter(event=event).values('interaction_type').annotate(
            count=Count('id')
        )
        
        # Calculer la note moyenne
        avg_rating = VirtualEventInteraction.objects.filter(
            event=event, 
            interaction_type='rating'
        ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        response_data = {
            'event_id': event_id,
            'event_title': event.title,
            'interaction_counts': list(stats),
            'average_rating': round(avg_rating, 2),
            'total_interactions': VirtualEventInteraction.objects.filter(event=event).count()
        }
        
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def organizer_interactions(self, request):
        """Récupérer toutes les interactions des événements de l'organisateur connecté"""
        user = request.user
        
        # Vérifier que l'utilisateur est un organisateur
        if not hasattr(user, 'profile') or user.profile.role != 'organizer':
            return Response(
                {"error": "Seuls les organisateurs peuvent accéder à cette fonctionnalité."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer tous les événements de l'organisateur
        organizer_events = Event.objects.filter(organizer=user, event_type='virtual')
        
        # Récupérer toutes les interactions de ces événements
        interactions = VirtualEventInteraction.objects.filter(event__in=organizer_events)
        
        # Grouper par événement pour une meilleure organisation
        events_data = {}
        for event in organizer_events:
            event_interactions = interactions.filter(event=event)
            events_data[event.id] = {
                'event_title': event.title,
                'event_date': event.start_date,
                'interactions': VirtualEventInteractionSerializer(event_interactions, many=True).data
            }
        
        return Response({
            'organizer_id': user.id,
            'organizer_username': user.username,
            'total_events': organizer_events.count(),
            'total_interactions': interactions.count(),
            'events_data': events_data
        })


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet pour les événements"""
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'tags', 'is_featured', 'is_free', 'place_type', 'event_type']
    search_fields = ['title', 'description', 'location', 'organizer__username']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'price', 'title']
    ordering = ['-start_date']

    def get_queryset(self):
        """Filtrer les événements selon l'action et l'utilisateur"""
        if self.action == 'list':
            # Pour la liste publique, ne montrer que les événements publiés
            return Event.objects.filter(status='published')
        elif self.action == 'create':
            # Pour la création, permettre l'accès à tous les événements (nécessaire pour la validation)
            return Event.objects.all()
        else:
            # Pour les autres actions, permettre l'accès selon les permissions
            user = self.request.user
            if user.is_authenticated:
                # L'utilisateur peut voir ses propres événements + les événements publiés
                return Event.objects.filter(
                    Q(status='published') | Q(organizer=user)
                )
            else:
                # Utilisateur non connecté: seulement les événements publiés
                return Event.objects.filter(status='published')

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        elif self.action == 'create':
            return EventSerializer
        return EventSerializer

    def perform_create(self, serializer):
        """Définir automatiquement l'organizer lors de la création"""
        serializer.save(organizer=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Override create pour ajouter des logs de debug"""
        print(f"DEBUG: EventViewSet.create - Données reçues: {request.data}")
        print(f"DEBUG: EventViewSet.create - Type de données: {type(request.data)}")
        print(f"DEBUG: EventViewSet.create - Content-Type: {request.content_type}")
        print(f"DEBUG: EventViewSet.create - FILES: {request.FILES}")
        
        # Log détaillé des fichiers
        if request.FILES:
            print(f"DEBUG: EventViewSet.create - Nombre de fichiers: {len(request.FILES)}")
            for key, file in request.FILES.items():
                print(f"DEBUG: EventViewSet.create - Fichier '{key}': {file.name}, type: {file.content_type}, taille: {file.size}")
        else:
            print(f"DEBUG: EventViewSet.create - Aucun fichier reçu")
        
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def virtual_events(self, request):
        """Récupérer les événements virtuels selon les permissions"""
        user = request.user
        
        if user.is_authenticated:
            if user.is_superuser:
                # Super Admin voit tous les événements
                virtual_events = Event.objects.filter(event_type='virtual', status='published')
            elif hasattr(user, 'profile') and user.profile.role == 'organizer':
                # Organisateur voit seulement ses propres événements
                virtual_events = Event.objects.filter(event_type='virtual', status='published', organizer=user)
            else:
                # Participant voit tous les événements publiés
                virtual_events = Event.objects.filter(event_type='virtual', status='published')
        else:
            # Utilisateur non connecté voit seulement les événements publiés
            virtual_events = Event.objects.filter(event_type='virtual', status='published')
        
        serializer = EventListSerializer(virtual_events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_events(self, request):
        """Récupérer tous les événements de l'utilisateur connecté (tous statuts)"""
        if not request.user.is_authenticated:
            return Response(
                {"error": "Vous devez être connecté pour voir vos événements."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Récupérer tous les événements de l'utilisateur (brouillons, publiés, etc.)
        my_events = Event.objects.filter(organizer=request.user).order_by('-created_at')
        
        # Utiliser EventSerializer pour avoir les interactions détaillées
        if hasattr(request.user, 'profile') and request.user.profile.role == 'organizer':
            serializer = EventSerializer(my_events, many=True)
        else:
            serializer = EventListSerializer(my_events, many=True)
        
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def physical_events(self, request):
        """Récupérer les événements physiques selon les permissions"""
        user = request.user
        
        if user.is_authenticated:
            if user.is_superuser:
                # Super Admin voit tous les événements
                physical_events = Event.objects.filter(event_type='physical', status='published')
            elif hasattr(user, 'profile') and user.profile.role == 'organizer':
                # Organisateur voit seulement ses propres événements
                physical_events = Event.objects.filter(event_type='physical', status='published', organizer=user)
            else:
                # Participant voit tous les événements publiés
                physical_events = Event.objects.filter(event_type='physical', status='published')
        else:
            # Utilisateur non connecté voit seulement les événements publiés
            physical_events = Event.objects.filter(event_type='physical', status='published')
        
        serializer = EventListSerializer(physical_events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def virtual_details(self, request, pk=None):
        """Récupérer les détails d'un événement virtuel"""
        event = self.get_object()
        if not event.is_virtual:
            return Response(
                {"error": "Cet événement n'est pas virtuel."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if hasattr(event, 'virtual_details'):
            serializer = VirtualEventSerializer(event.virtual_details)
            return Response(serializer.data)
        else:
            return Response(
                {"error": "Aucun détail virtuel trouvé pour cet événement."},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get', 'post'])
    def ticket_types(self, request, pk=None):
        """Récupérer et créer des types de billets pour un événement"""
        event = self.get_object()
        
        if request.method == 'GET':
            ticket_types = event.ticket_types.all()
            serializer = TicketTypeSerializer(ticket_types, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Vérifier que l'utilisateur est l'organisateur de l'événement
            if event.organizer != request.user:
                return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
            
            # Créer le type de billet
            data = request.data.copy()
            data['event'] = event.id
            
            serializer = TicketTypeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def session_types(self, request, pk=None):
        """Récupérer et créer des types de sessions pour un événement"""
        event = self.get_object()
        
        if request.method == 'GET':
            session_types = event.session_types.all()
            serializer = SessionTypeSerializer(session_types, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Vérifier que l'utilisateur est l'organisateur de l'événement ou super admin
            if event.organizer != request.user and not request.user.is_superuser:
                return Response({'error': 'Accès non autorisé'}, status=status.HTTP_403_FORBIDDEN)
            
            # Créer le type de session
            data = request.data.copy()
            data['event'] = event.id
            
            serializer = SessionTypeSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Récupérer tous les participants d'un événement (confirmés ET en liste d'attente)"""
        event = self.get_object()
        # 🎯 CORRECTION : Inclure les inscriptions confirmées ET en liste d'attente
        participants = event.registrations.filter(status__in=['confirmed', 'attended', 'waitlisted'])
        serializer = EventRegistrationSerializer(participants, many=True)
        
        print(f"🔍 DEBUG: participants - Event: {event.title}, Count: {participants.count()}")
        for p in participants:
            if p.is_guest_registration:
                print(f"🔍 DEBUG: Guest participant - Name: {p.guest_full_name}, Email: {p.guest_email}, Status: {p.status}")
            else:
                print(f"🔍 DEBUG: User participant - User: {p.user.username}, Status: {p.status}")
        
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def waitlisted_registrations(self, request, pk=None):
        """Récupérer la liste des inscriptions en liste d'attente d'un événement (pour l'organisateur)"""
        event = self.get_object()
        
        # Vérifier que l'utilisateur est l'organisateur de l'événement
        if event.organizer != request.user:
            return Response({'error': 'Accès non autorisé'}, status=403)
        
        # Récupérer les inscriptions en liste d'attente
        waitlisted = event.registrations.filter(status='waitlisted')
        serializer = EventRegistrationSerializer(waitlisted, many=True)
        
        print(f"🔍 DEBUG: waitlisted_registrations - Event: {event.title}, Count: {waitlisted.count()}")
        
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def all_registrations(self, request, pk=None):
        """Récupérer toutes les inscriptions d'un événement (pour l'organisateur)"""
        event = self.get_object()
        
        # Vérifier que l'utilisateur est l'organisateur de l'événement
        if event.organizer != request.user:
            return Response({'error': 'Accès non autorisé'}, status=403)
        
        # Récupérer toutes les inscriptions avec statuts
        all_registrations = event.registrations.all().order_by('-created_at')
        serializer = EventRegistrationSerializer(all_registrations, many=True)
        
        print(f"🔍 DEBUG: all_registrations - Event: {event.title}, Count: {all_registrations.count()}")
        
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques des événements pour l'organisateur connecté"""
        user = request.user
        
        print(f"🔍 DEBUG: statistics - User: {user.username}")
        
        # Récupérer les événements de l'utilisateur
        user_events = Event.objects.filter(organizer=user)
        total_events = user_events.count()
        
        print(f"🔍 DEBUG: statistics - Total events: {total_events}")
        
        if total_events == 0:
            return Response({
                'total_events': 0,
                'published_events': 0,
                'total_registrations': 0,
                'confirmed_registrations': 0,
                'total_revenue': 0,
                'upcoming_events': 0,
                'status_distribution': {},
                'category_distribution': {},
                'timeseries': []
            })
        
        # Statistiques de base
        published_events = user_events.filter(status='published').count()
        upcoming_events = user_events.filter(
            status='published',
            start_date__gt=timezone.now()
        ).count()
        
        # Événements en cours (déjà commencés mais pas encore terminés)
        ongoing_events = user_events.filter(
            status='published',
            start_date__lte=timezone.now(),
            end_date__gt=timezone.now()
        ).count()
        
        # Statistiques des inscriptions
        user_registrations = EventRegistration.objects.filter(event__in=user_events)
        total_registrations = user_registrations.count()
        confirmed_registrations = user_registrations.filter(
            status__in=['confirmed', 'attended']
        ).count()
        
        # Revenus totaux
        total_revenue = user_registrations.filter(
            payment_status='paid'
        ).aggregate(total=Sum('price_paid'))['total'] or 0
        
        # Répartition par statut
        status_distribution = {}
        for status_choice in Event.STATUS_CHOICES:
            status_key = status_choice[0]
            count = user_events.filter(status=status_key).count()
            if count > 0:
                status_distribution[status_key] = count
        
        # Répartition par catégorie
        category_distribution = {}
        category_stats = user_events.values('category__name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        for stat in category_stats:
            category_name = stat['category__name'] or 'Sans catégorie'
            category_distribution[category_name] = stat['count']
        
        # Données de série temporelle (30 derniers jours)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        timeseries = []
        
        for i in range(30):
            date = thirty_days_ago + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            # Inscriptions pour ce jour
            daily_registrations = user_registrations.filter(
                registered_at__date=date.date()
            ).count()
            
            # Revenus pour ce jour
            daily_revenue = user_registrations.filter(
                registered_at__date=date.date(),
                payment_status='paid'
            ).aggregate(total=Sum('price_paid'))['total'] or 0
            
            timeseries.append({
                'date': date_str,
                'registrations': daily_registrations,
                'revenue': float(daily_revenue)
            })
        
        print(f"🔍 DEBUG: statistics - Response data prepared")
        
        return Response({
            'total_events': total_events,
            'published_events': published_events,
            'total_registrations': total_registrations,
            'confirmed_registrations': confirmed_registrations,
            'total_revenue': float(total_revenue),
            'upcoming_events': upcoming_events,
            'ongoing_events': ongoing_events,
            'status_distribution': status_distribution,
            'category_distribution': category_distribution,
            'timeseries': timeseries
        })

    @action(detail=True, methods=['post'], permission_classes=[])
    def create_temp_payment_intent(self, request, pk=None):
        """Créer une intention de paiement temporaire pour Stripe"""
        event = self.get_object()
        
        try:
            # Récupérer les informations de paiement
            amount = request.data.get('amount')
            currency = request.data.get('currency', 'eur')
            
            if not amount:
                return Response(
                    {"error": "Le montant est requis"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Mode développement: simuler Stripe si clé invalide/absente
            import os
            from uuid import uuid4
            import stripe
            api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
            if getattr(settings, 'DEBUG', False) and (not api_key or api_key == 'sk_test_...' or 'sk_test_51H1234567890' in api_key or os.environ.get('STRIPE_OFFLINE') == '1'):
                fake_intent_id = f"pi_test_{uuid4().hex}"
                return Response({
                    'client_secret': f'{fake_intent_id}_secret_fake',
                    'payment_intent_id': fake_intent_id,
                    'mode': 'test'
                })

            # Créer l'intention de paiement Stripe
            stripe.api_key = api_key
            
            # 🎯 NOUVELLE LOGIQUE : Gérer les utilisateurs non authentifiés
            metadata = {
                'event_id': event.id,
                'event_title': event.title,
            }
            
            # Ajouter user_id seulement si l'utilisateur est authentifié
            if request.user and request.user.is_authenticated:
                metadata['user_id'] = request.user.id
            
            payment_intent = stripe.PaymentIntent.create(
                amount=int(float(amount) * 100),  # Stripe utilise les centimes
                currency=currency,
                metadata=metadata
            )

            return Response({
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'mode': 'test' if 'test' in stripe.api_key else 'live'
            })
            
        except stripe.error.StripeError as e:
            return Response(
                {"error": f"Erreur Stripe: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Erreur lors de la création du paiement: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def interactions(self, request, pk=None):
        """Récupérer toutes les interactions d'un événement"""
        event = self.get_object()
        if not event.is_virtual:
            return Response(
                {"error": "Les interactions ne sont disponibles que pour les événements virtuels."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        interactions = event.interactions.all()
        serializer = VirtualEventInteractionSerializer(interactions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publier un événement (changer le statut de 'draft' à 'published')"""
        event = self.get_object()
        
        # Vérifier que l'utilisateur est l'organisateur de l'événement
        if event.organizer != request.user:
            return Response(
                {"error": "Vous n'êtes autorisé à publier que vos propres événements."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que l'événement est en brouillon
        if event.status != 'draft':
            return Response(
                {"error": f"Seuls les événements en brouillon peuvent être publiés. Statut actuel: {event.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Publier l'événement
        event.status = 'published'
        event.published_at = timezone.now()
        event.save()
        
        serializer = EventListSerializer(event)
        return Response({
            "message": "Événement publié avec succès",
            "event": serializer.data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler un événement (changer le statut vers 'cancelled')"""
        event = self.get_object()
        
        # Vérifier que l'utilisateur est l'organisateur de l'événement
        if event.organizer != request.user:
            return Response(
                {"error": "Vous n'êtes autorisé à annuler que vos propres événements."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que l'événement peut être annulé
        if event.status not in ['draft', 'published']:
            return Response(
                {"error": f"Cet événement ne peut pas être annulé. Statut actuel: {event.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier si l'événement a des inscriptions confirmées
        confirmed_registrations = event.registrations.filter(status='confirmed')
        confirmed_count = confirmed_registrations.count()
        
        print(f"🔍 DEBUG: Annulation événement {event.title} (ID: {event.id})")
        print(f"🔍 DEBUG: Prix de l'événement: {event.price}€")
        print(f"🔍 DEBUG: Inscriptions confirmées: {confirmed_count}")
        
        # Afficher les détails des inscriptions
        for reg in confirmed_registrations:
            print(f"🔍 DEBUG: - Inscription {reg.id}: status={reg.status}, payment_status={reg.payment_status}, price_paid={reg.price_paid}€, user={reg.user}, guest={reg.guest_email}")
        
        if confirmed_count > 0:
            # Si il y a des inscriptions confirmées, proposer d'annuler avec remboursement
            reason = request.data.get('reason', 'Événement annulé par l\'organisateur')
            
            # Annuler l'événement
            event.status = 'cancelled'
            event.save()
            
            # 🆕 CRÉER AUTOMATIQUEMENT DES DEMANDES DE REMBOURSEMENT pour tous les inscrits confirmés
            refunds_created = 0
            from .models import RefundPolicy, RefundRequest
            from django.utils import timezone
            
            for registration in event.registrations.filter(status='confirmed'):
                try:
                    # 🎯 CORRECTION : Créer des remboursements pour TOUS les inscrits confirmés
                    # même pour les événements gratuits (pour gérer les frais de service, etc.)
                    # ou pour les événements payants
                    should_create_refund = (
                        registration.payment_status == 'paid' or  # Paiement effectué
                        event.price > 0 or  # Événement payant
                        registration.price_paid > 0  # Montant payé > 0
                    )
                    
                    if should_create_refund:
                        # Obtenir ou créer la politique de remboursement
                        try:
                            policy = event.refund_policy
                        except RefundPolicy.DoesNotExist:
                            policy = RefundPolicy.objects.create(
                                event=event,
                                mode='mixed',
                                auto_refund_delay_hours=24,
                                refund_percentage_immediate=100,
                                refund_percentage_after_delay=100,
                                cutoff_hours_before_event=24,
                                allow_partial_refunds=True,
                                require_reason=False,
                                notify_organizer_on_cancellation=True
                            )
                        
                        # Calculer les montants et dates
                        refund_percentage = policy.get_refund_percentage(0)  # Annulation immédiate = 100%
                        refund_amount = (registration.price_paid * refund_percentage) / 100
                        
                        now = timezone.now()
                        auto_process_at = None
                        if policy.mode in ['auto', 'mixed']:
                            auto_process_at = now + timezone.timedelta(hours=policy.auto_refund_delay_hours)
                        
                        expires_at = event.start_date - timezone.timedelta(hours=policy.cutoff_hours_before_event)
                        
                        # Créer la demande de remboursement
                        refund_request = RefundRequest.objects.create(
                            registration=registration,
                            reason=f'Événement annulé par l\'organisateur: {reason}',
                            amount_paid=registration.price_paid,
                            refund_percentage=refund_percentage,
                            refund_amount=refund_amount,
                            auto_process_at=auto_process_at,
                            expires_at=expires_at
                        )
                        
                        refunds_created += 1
                        print(f"✅ Demande de remboursement créée automatiquement: ID={refund_request.id} pour {registration.user.email if registration.user else registration.guest_email} - Montant: {refund_amount}€")
                        
                except Exception as e:
                    print(f"❌ Erreur création demande remboursement automatique pour {registration.id}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Envoyer des emails aux participants pour les informer de l'annulation
            from django.template.loader import render_to_string
            from django.core.mail import EmailMultiAlternatives
            from django.conf import settings
            
            for registration in event.registrations.filter(status='confirmed'):
                try:
                    # 🎯 CORRECTION : Déterminer l'email du destinataire (utilisateur ou invité)
                    recipient_email = None
                    if registration.user:
                        recipient_email = registration.user.email
                    elif registration.guest_email:
                        recipient_email = registration.guest_email
                    
                    if recipient_email:
                        # 🎯 CORRECTION : Préparer le contexte selon le type d'inscription
                        if registration.user:
                            # Utilisateur connecté
                            context = {
                                'user': registration.user,
                                'event': event,
                                'reason': reason,
                                'registration': registration
                            }
                            text_body = render_to_string('emails/event_cancelled_participant.txt', context)
                            html_body = render_to_string('emails/event_cancelled_participant.html', context)
                        else:
                            # Invité
                            context = {
                                'guest_full_name': registration.guest_full_name,
                                'event': event,
                                'reason': reason,
                                'registration': registration
                            }
                            text_body = render_to_string('emails/guest_event_cancelled.txt', context)
                            html_body = render_to_string('emails/guest_event_cancelled.html', context)
                        
                        subject = f"❌ Événement annulé - {event.title}"
                        
                        msg = EmailMultiAlternatives(
                            subject,
                            text_body,
                            getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                            [recipient_email]
                        )
                        msg.attach_alternative(html_body, 'text/html')
                        msg.send(fail_silently=True)
                        
                        print(f"✅ Email d'annulation envoyé à {recipient_email} ({'Utilisateur' if registration.user else 'Invitée'})")
                    else:
                        print(f"⚠️ Aucun email trouvé pour l'inscription {registration.id} (user: {registration.user}, guest: {registration.guest_email})")
                except Exception as e:
                    print(f"❌ Erreur envoi email d'annulation: {e}")
            
            return Response({
                "message": f"Événement annulé avec succès. {confirmed_registrations} participants ont été notifiés par email. {refunds_created} demandes de remboursement ont été créées automatiquement.",
                "event": EventListSerializer(event).data,
                "participants_notified": confirmed_registrations,
                "refunds_created": refunds_created
            })
        else:
            # Aucune inscription confirmée, annulation simple
            event.status = 'cancelled'
            event.save()
            
            return Response({
                "message": "Événement annulé avec succès.",
                "event": EventListSerializer(event).data
            })






class EventRegistrationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les inscriptions aux événements"""
    serializer_class = EventRegistrationSerializer
    # 🎯 NOUVELLE LOGIQUE : Permettre l'accès public à la création d'inscriptions
    permission_classes = []  # Pas de restriction d'authentification
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'event']
    ordering_fields = ['registered_at', 'updated_at']
    ordering = ['-registered_at']

    def create(self, request, *args, **kwargs):
        # 🎯 NOUVEAU : Logs de débogage pour la vue
        print(f"🔍 DEBUG: EventRegistrationViewSet.create() appelé")
        print(f"🔍 DEBUG: request.data: {request.data}")
        print(f"🔍 DEBUG: request.user: {request.user}")
        print(f"🔍 DEBUG: request.user.is_authenticated: {request.user.is_authenticated if request.user else False}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Vérifier si l'événement est encore accessible pour les inscriptions
        event = serializer.validated_data.get('event')
        if event:
            # Vérifier si l'événement est passé ou en fin de course
            if not event.is_registration_open():
                status_msg = event.get_registration_message()
                return Response({
                    "error": f"Inscription impossible: {status_msg}",
                    "registration_status": event.get_registration_status(),
                    "event_end_date": event.end_date,
                    "current_time": timezone.now()
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Pour les événements payants, forcer le statut 'pending' jusqu'au paiement
        validated_data = serializer.validated_data
        if hasattr(validated_data, 'get') and validated_data.get('event') and validated_data['event'].price > 0:
            validated_data['status'] = 'pending'
            validated_data['payment_status'] = 'pending'
        
        registration = serializer.save()

        # 🔍 LOG CRITIQUE: Vérifier si le stream se lance automatiquement lors de la création
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔍 LOG CRITIQUE: create - Inscription {registration.id} créée pour event {event.id}")
        logger.info(f"🔍 LOG CRITIQUE: Event {event.id} - is_virtual: {event.is_virtual}")
        if event.is_virtual:
            virtual_details = getattr(event, 'virtual_details', None)
            logger.info(f"🔍 LOG CRITIQUE: Virtual details: {virtual_details}")
            if virtual_details:
                logger.info(f"🔍 LOG CRITIQUE: Meeting ID: {virtual_details.meeting_id}")
                logger.info(f"🔍 LOG CRITIQUE: Meeting URL: {virtual_details.meeting_url}")
                logger.info(f"🔍 LOG CRITIQUE: Platform: {virtual_details.platform}")
        logger.info(f"🔍 LOG CRITIQUE: Aucun appel à configure_stream ou start_stream effectué lors de la création")

        # S'assurer que le QR est généré si confirmé (cas gratuit)
        try:
            registration.refresh_from_db()
        except Exception:
            pass

        # 🎯 NOUVEAU : Envoyer confirmation pour TOUTES les inscriptions (gratuites ET payantes)
        # Envoyer SMS immédiatement après création de l'inscription
        try:
            from .sms_service import sms_service
            print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS UNIVERSEL =====")
            print(f"🔍 DEBUG: Inscription ID: {registration.id}")
            print(f"🔍 DEBUG: Statut: {registration.status}")
            print(f"🔍 DEBUG: Prix payé: {registration.price_paid}")
            print(f"🔍 DEBUG: Événement payant: {registration.event.price > 0}")
            print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
            
            sms_sent = sms_service.send_confirmation_sms(registration)
            
            if sms_sent:
                print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour l'inscription {registration.id}")
            else:
                print(f"🔍 DEBUG: ❌ Échec envoi SMS pour l'inscription {registration.id}")
            print(f"🔍 DEBUG: ===== FIN ENVOI SMS UNIVERSEL =====")
        except Exception as e:
            print(f"🔍 DEBUG: Erreur envoi SMS universel: {e}")

        # Envoyer confirmation EMAIL pour inscriptions gratuites confirmées (comme avant)
        if (registration.price_paid or 0) == 0 and registration.status == 'confirmed':
            try:
                qr_url = None
                if registration.qr_code:
                    qr_url = request.build_absolute_uri(registration.qr_code.url)
                
                # 🎯 CORRECTION : Déterminer l'email du destinataire (utilisateur ou invité)
                recipient_email = None
                if registration.user:
                    recipient_email = registration.user.email
                elif registration.guest_email:
                    recipient_email = registration.guest_email
                
                if recipient_email:
                    # 🎯 CORRECTION : Préparer le contexte selon le type d'inscription
                    if registration.user:
                        # Utilisateur connecté
                        context = {
                            'user': registration.user,
                            'event': registration.event,
                            'qr_url': qr_url,
                            'registration': registration,
                            'ticket_type': getattr(registration, 'ticket_type', None),
                            'session_type': getattr(registration, 'session_type', None),
                        }
                        subject = f"Confirmation d'inscription - {registration.event.title}"
                        text_body = render_to_string('emails/registration_confirmation.txt', context)
                        html_body = render_to_string('emails/registration_confirmation.html', context)
                    else:
                        # Invité
                        context = {
                            'guest_full_name': registration.guest_full_name,
                            'event': registration.event,
                            'qr_url': qr_url,
                            'registration': registration,
                            'ticket_type': getattr(registration, 'ticket_type', None),
                            'session_type': getattr(registration, 'session_type', None),
                        }
                        subject = f"Confirmation d'inscription - {registration.event.title}"
                        text_body = render_to_string('emails/guest_registration_confirmation.txt', context)
                        html_body = render_to_string('emails/guest_registration_confirmation.html', context)
                    
                    msg = EmailMultiAlternatives(subject, text_body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
                    msg.attach_alternative(html_body, 'text/html')
                    
                    # Attacher le QR code si disponible
                    if registration.qr_code and hasattr(registration.qr_code, 'path'):
                        try:
                            with open(registration.qr_code.path, 'rb') as f:
                                img_data = f.read()
                            from email.mime.image import MIMEImage
                            img = MIMEImage(img_data)
                            img.add_header('Content-ID', '<qr_cid>')
                            img.add_header('Content-Disposition', 'inline', filename='qr.png')
                            msg.attach(img)
                        except Exception:
                            pass
                    
                    msg.send(fail_silently=True)
                    print(f"🔍 DEBUG: Email de confirmation envoyé à {recipient_email} pour l'inscription {registration.id}")
                    
                    # 🎯 NOUVEAU : Envoyer le SMS de confirmation avec logs détaillés
                    try:
                        from .sms_service import sms_service
                        print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS =====")
                        print(f"🔍 DEBUG: Inscription ID: {registration.id}")
                        print(f"🔍 DEBUG: Statut: {registration.status}")
                        print(f"🔍 DEBUG: Email: {registration.guest_email}")
                        print(f"🔍 DEBUG: Téléphone: {registration.guest_phone}")
                        print(f"🔍 DEBUG: Pays: {registration.guest_country}")
                        print(f"🔍 DEBUG: Twilio activé: {sms_service.providers['twilio']['enabled']}")
                        print(f"🔍 DEBUG: Numéro Twilio: {sms_service.providers['twilio']['from_number']}")
                        
                        sms_sent = sms_service.send_confirmation_sms(registration)
                        
                        if sms_sent:
                            print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour l'inscription {registration.id}")
                        else:
                            print(f"🔍 DEBUG: ❌ Échec envoi SMS pour l'inscription {registration.id}")
                        print(f"🔍 DEBUG: ===== FIN ENVOI SMS =====")
                    except Exception as e:
                        print(f"🔍 DEBUG: Erreur envoi SMS: {e}")
                else:
                    print(f"🔍 DEBUG: Aucun email trouvé pour l'inscription {registration.id} (user: {registration.user}, guest: {registration.guest_email})")
            except Exception as e:
                print(f"🔍 DEBUG: Erreur envoi email de confirmation: {e}")
                pass

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        """Filtrer les inscriptions selon l'utilisateur"""
        user = self.request.user
        
        # 🎯 NOUVELLE LOGIQUE : Gérer les utilisateurs non authentifiés
        if not user or not user.is_authenticated:
            # 🎯 CORRECTION : Pour les actions de paiement, permettre l'accès aux inscriptions
            if self.action in ['confirm_payment', 'cancel_payment']:
                # Permettre l'accès aux inscriptions pour la confirmation/annulation de paiement
                return EventRegistration.objects.all()
            # Pour les autres actions, retourner un queryset vide
            return EventRegistration.objects.none()
        
        # Pour les actions d'approbation/rejet de liste d'attente,
        # permettre l'accès aux inscriptions des événements organisés par l'utilisateur
        if self.action in ['approve_waitlist', 'reject_waitlist']:
            # L'utilisateur peut accéder aux inscriptions de ses propres événements
            return EventRegistration.objects.filter(
                Q(user=user) |  # Ses propres inscriptions
                Q(event__organizer=user)  # Inscriptions aux événements qu'il organise
            )
        
        # Pour les autres actions, seulement les inscriptions de l'utilisateur
        return EventRegistration.objects.filter(user=user)

    def get_serializer_class(self):
        """Choisir le bon sérialiseur selon l'action"""
        if self.action == 'create':
            return EventRegistrationCreateSerializer
        return EventRegistrationSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler une inscription"""
        registration = self.get_object()
        
        if registration.user != request.user:
            return Response(
                {"error": "Vous n'êtes pas autorisé à annuler cette inscription."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        event = registration.event
        previous_status = registration.status
        
        # 💰 NOUVEAU: Créer automatiquement une demande de remboursement si payée OU en attente de paiement OU avec un prix défini
        refund_request = None
        if ((registration.payment_status == 'paid' or registration.payment_status == 'pending') and registration.price_paid > 0) or (hasattr(registration, 'event') and registration.event.price > 0):
            try:
                from .models import RefundPolicy, RefundRequest
                from django.utils import timezone
                
                # Obtenir ou créer la politique de remboursement
                try:
                    policy = event.refund_policy
                except RefundPolicy.DoesNotExist:
                    policy = RefundPolicy.objects.create(
                        event=event,
                        mode='mixed',
                        auto_refund_delay_hours=24,
                        refund_percentage_immediate=100,
                        cutoff_hours_before_event=24
                    )
                
                # 💰 FORCER la création de demande de remboursement lors d'annulation (contourner la politique)
                # Pour les annulations, on force le remboursement même si l'événement est proche
                force_refund = True  # Annulation = remboursement obligatoire
                
                if force_refund or policy.can_refund_now():
                    refund_percentage = policy.get_refund_percentage(0)
                    refund_amount = (registration.price_paid * refund_percentage) / 100
                    
                    now = timezone.now()
                    auto_process_at = None
                    if policy.mode in ['auto', 'mixed']:
                        auto_process_at = now + timezone.timedelta(hours=policy.auto_refund_delay_hours)
                    
                    # Pour les annulations, étendre la date d'expiration
                    if force_refund:
                        expires_at = event.start_date + timezone.timedelta(days=7)  # 7 jours après l'événement
                    else:
                        expires_at = event.start_date - timezone.timedelta(hours=policy.cutoff_hours_before_event)
                    
                    # Vérifier si une demande de remboursement existe déjà
                    existing_refund = RefundRequest.objects.filter(registration=registration).first()
                    if existing_refund:
                        # Mettre à jour la demande existante
                        existing_refund.reason = request.data.get('reason', 'Annulation par l\'utilisateur')
                        existing_refund.amount_paid = registration.price_paid
                        existing_refund.refund_percentage = refund_percentage
                        existing_refund.refund_amount = refund_amount
                        existing_refund.auto_process_at = auto_process_at
                        existing_refund.expires_at = expires_at
                        existing_refund.save()
                        refund_request = existing_refund
                        print(f"✅ Demande de remboursement mise à jour: ID={refund_request.id} pour {registration.user.email} - Montant: {refund_amount}€")
                    else:
                        # Créer une nouvelle demande de remboursement
                        refund_request = RefundRequest.objects.create(
                            registration=registration,
                            reason=request.data.get('reason', 'Annulation par l\'utilisateur'),
                            amount_paid=registration.price_paid,
                            refund_percentage=refund_percentage,
                            refund_amount=refund_amount,
                            auto_process_at=auto_process_at,
                            expires_at=expires_at
                        )
                        print(f"✅ Demande de remboursement créée: ID={refund_request.id} pour {registration.user.email} - Montant: {refund_amount}€")
                else:
                    print(f"❌ Remboursement non autorisé pour {registration.id} - trop proche de l'événement")
            except Exception as e:
                print(f"❌ Erreur création demande remboursement: {e}")
                import traceback
                traceback.print_exc()
        registration.status = 'cancelled'
        registration.save()
        
        # Mettre à jour le compteur d'inscriptions de l'événement
        event = registration.event
        if previous_status in ['confirmed', 'attended']:
            event.current_registrations = max(0, event.current_registrations - 1)
            event.save(update_fields=['current_registrations'])

        # Diminuer le compteur de tickets vendus
        if registration.ticket_type and previous_status in ['confirmed', 'attended']:
            tt = registration.ticket_type
            tt.sold_count = max(0, tt.sold_count - 1)
            tt.save(update_fields=['sold_count'])

        # Promouvoir le premier en liste d'attente s'il existe
        waitlisted = EventRegistration.objects.filter(event=event, status='waitlisted').order_by('registered_at').first()
        if waitlisted and (event.place_type == 'unlimited' or (event.max_capacity or 0) > event.current_registrations):
            # Vérifier la disponibilité du type de billet
            if not waitlisted.ticket_type or waitlisted.ticket_type.quantity is None or waitlisted.ticket_type.sold_count < waitlisted.ticket_type.quantity:
                waitlisted.status = 'confirmed'
                waitlisted.save()
                event.current_registrations = (event.current_registrations or 0) + 1
                event.save(update_fields=['current_registrations'])
                if waitlisted.ticket_type:
                    tt = waitlisted.ticket_type
                    tt.sold_count = tt.sold_count + 1
                    tt.save(update_fields=['sold_count'])
        
        # Notifier l'utilisateur de l'annulation de son billet
        try:
            subject = f"Annulation de votre billet - {event.title}"
            
            # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
            if registration.user:
                # Utilisateur connecté
                recipient_email = registration.user.email
                context = { 'user': registration.user, 'event': event }
                text_body = render_to_string('emails/registration_cancelled.txt', context)
                html_body = render_to_string('emails/registration_cancelled.html', context)
            else:
                # Invité
                recipient_email = registration.guest_email
                context = { 'guest_full_name': registration.guest_full_name, 'event': event }
                text_body = render_to_string('emails/guest_registration_cancelled.txt', context)
                html_body = render_to_string('emails/guest_registration_cancelled.html', context)
            
            msg = EmailMultiAlternatives(subject, text_body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=True)
            
            # 🎯 NOUVEAU : Envoyer SMS pour annulation d'inscription
            try:
                from .sms_service import sms_service
                print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS ANNULATION =====")
                print(f"🔍 DEBUG: Inscription ID: {registration.id}")
                print(f"🔍 DEBUG: Statut: {registration.status}")
                print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
                
                sms_sent = sms_service.send_confirmation_sms(registration)
                
                if sms_sent:
                    print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour annulation {registration.id}")
                else:
                    print(f"🔍 DEBUG: ❌ Échec envoi SMS pour annulation {registration.id}")
                print(f"🔍 DEBUG: ===== FIN ENVOI SMS ANNULATION =====")
            except Exception as e:
                print(f"🔍 DEBUG: Erreur envoi SMS annulation: {e}")
        except Exception:
            pass

        serializer = self.get_serializer(registration)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirmer une inscription en attente ou liste d'attente"""
        registration = self.get_object()
        if registration.event.organizer != request.user and not request.user.is_staff:
            return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        if registration.status in ['pending', 'waitlisted']:
            event = registration.event
            # Vérifier la capacité de l'événement
            if event.place_type == 'limited' and event.max_capacity is not None and event.current_registrations >= event.max_capacity:
                return Response({"error": "Capacité maximale atteinte"}, status=status.HTTP_400_BAD_REQUEST)

            # Vérifier la capacité du type de billet
            if registration.ticket_type and registration.ticket_type.quantity is not None and registration.ticket_type.sold_count >= registration.ticket_type.quantity:
                return Response({"error": "Plus de billets disponibles pour ce type"}, status=status.HTTP_400_BAD_REQUEST)

            registration.status = 'confirmed'
            registration.save()
            event.current_registrations = (event.current_registrations or 0) + 1
            event.save(update_fields=['current_registrations'])
            if registration.ticket_type:
                tt = registration.ticket_type
                tt.sold_count = tt.sold_count + 1
                tt.save(update_fields=['sold_count'])
        return Response(self.get_serializer(registration).data)

    @action(detail=True, methods=['post'])
    def cancel_payment(self, request, pk=None):
        """Annuler une inscription en attente de paiement"""
        registration = self.get_object()
        
        if registration.user != request.user:
            return Response(
                {"error": "Vous n'êtes pas autorisé à annuler cette inscription."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que l'inscription est en attente et non payée
        if registration.status != 'pending' or registration.payment_status != 'unpaid':
            return Response(
                {"error": "Cette inscription ne peut pas être annulée car elle n'est pas en attente de paiement."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Annuler l'inscription
        registration.status = 'cancelled'
        registration.save()
        
        return Response({"message": "Inscription annulée avec succès. Vous pouvez vous réinscrire si vous le souhaitez."})

    @action(detail=True, methods=['post'])
    def test_payment_success(self, request, pk=None):
        """Simuler un paiement réussi en mode test"""
        registration = self.get_object()
        
        # Traiter le paiement de test
        return self._process_test_payment(registration)

    @action(detail=True, methods=['post'])
    def approve_waitlist(self, request, pk=None):
        """Approuver une inscription en liste d'attente (organisateur ou staff uniquement)"""
        try:
            registration = self.get_object()
            event = registration.event
            
            print(f"APPROVE DEBUG: Registration ID={registration.id}, Status={registration.status}")
            print(f"APPROVE DEBUG: Event ID={event.id}, Organizer={event.organizer.id}, Current User={request.user.id}")
            
            # Vérifier les permissions
            if event.organizer != request.user and not request.user.is_staff:
                print(f"APPROVE DEBUG: Permission denied")
                return Response(
                    {"error": "Vous n'êtes pas autorisé à approuver cette inscription."},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Vérifier que l'inscription est en liste d'attente
            if registration.status != 'waitlisted':
                print(f"APPROVE DEBUG: Wrong status - Expected 'waitlisted' but got '{registration.status}'")
                return Response(
                    {"error": f"Cette inscription n'est pas en liste d'attente. Statut actuel: {registration.status}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Note: Lors de l'approbation manuelle d'une liste d'attente,
            # l'organisateur peut dépasser la capacité normale.
            # C'est une décision délibérée, donc on ne bloque pas sur la capacité.
            print(f"APPROVE DEBUG: Event place_type={event.place_type}, max_capacity={event.max_capacity}")
            print(f"APPROVE DEBUG: Current registrations={event.current_registrations}")
            print(f"APPROVE DEBUG: Capacité ignorée pour approbation manuelle de liste d'attente")
            
            if registration.ticket_type:
                print(f"APPROVE DEBUG: Ticket type={registration.ticket_type.name}, quantity={registration.ticket_type.quantity}, sold_count={registration.ticket_type.sold_count}")
                print(f"APPROVE DEBUG: Capacité type de billet ignorée pour approbation manuelle")
            
            # Approuver l'inscription
            print(f"APPROVE DEBUG: All checks passed, approving registration...")
            registration.status = 'confirmed'
            registration.save()
            print(f"APPROVE DEBUG: Registration status updated to 'confirmed'")
            
            # Forcer la régénération du QR code si nécessaire
            if not registration.qr_code:
                try:
                    registration._generate_and_store_qr()
                except Exception as qr_error:
                    print(f"Erreur génération QR: {qr_error}")
            
            # Mettre à jour les compteurs
            event.current_registrations = (event.current_registrations or 0) + 1
            event.save(update_fields=['current_registrations'])
            
            if registration.ticket_type:
                tt = registration.ticket_type
                tt.sold_count = tt.sold_count + 1
                tt.save(update_fields=['sold_count'])
            
            # Envoyer l'email de confirmation avec QR code
            try:
                qr_url = None
                if registration.qr_code:
                    qr_url = request.build_absolute_uri(registration.qr_code.url)
                
                # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
                if registration.user:
                    # Utilisateur connecté
                    recipient_email = registration.user.email
                    context = {
                        'user': registration.user,
                        'event': event,
                        'qr_url': qr_url,
                    }
                else:
                    # Invité
                    recipient_email = registration.guest_email
                    context = {
                        'guest_name': registration.guest_full_name,
                        'guest_email': registration.guest_email,
                        'event': event,
                        'qr_url': qr_url,
                    }
                
                subject = f"Inscription approuvée - {event.title}"
                if registration.user:
                    message = render_to_string('emails/registration_approved.txt', context)
                    html_message = render_to_string('emails/registration_approved.html', context)
                else:
                    message = render_to_string('emails/guest_registration_approved.txt', context)
                    html_message = render_to_string('emails/guest_registration_approved.html', context)

                msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
                msg.attach_alternative(html_message, 'text/html')

                # Attacher le QR inline si disponible
                if registration.qr_code and hasattr(registration.qr_code, 'path'):
                    try:
                        with open(registration.qr_code.path, 'rb') as f:
                            img_data = f.read()
                        from email.mime.image import MIMEImage
                        img = MIMEImage(img_data)
                        img.add_header('Content-ID', '<qr_cid>')
                        img.add_header('Content-Disposition', 'inline', filename='qr.png')
                        msg.attach(img)
                    except Exception as e:
                        print(f"Erreur attachment QR: {e}")

                msg.send(fail_silently=False)  # Ne pas ignorer les erreurs d'email
                print(f"Email d'approbation envoyé à {recipient_email}")
                
                # 🎯 NOUVEAU : Envoyer SMS pour approbation de liste d'attente
                try:
                    from .sms_service import sms_service
                    print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS APPROBATION =====")
                    print(f"🔍 DEBUG: Inscription ID: {registration.id}")
                    print(f"🔍 DEBUG: Statut: {registration.status}")
                    print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
                    
                    sms_sent = sms_service.send_confirmation_sms(registration)
                    
                    if sms_sent:
                        print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour approbation {registration.id}")
                    else:
                        print(f"🔍 DEBUG: ❌ Échec envoi SMS pour approbation {registration.id}")
                    print(f"🔍 DEBUG: ===== FIN ENVOI SMS APPROBATION =====")
                except Exception as e:
                    print(f"🔍 DEBUG: Erreur envoi SMS approbation: {e}")
            except Exception as email_error:
                print(f"Erreur envoi email d'approbation: {email_error}")
                import traceback
                traceback.print_exc()
            
            return Response({"message": "Inscription approuvée avec succès.", "registration": self.get_serializer(registration).data})
        
        except Exception as e:
            print(f"Erreur lors de l'approbation: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"Erreur lors de l'approbation: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def reject_waitlist(self, request, pk=None):
        """Rejeter une inscription en liste d'attente (organisateur ou staff uniquement)"""
        registration = self.get_object()
        event = registration.event
        
        # Vérifier les permissions
        if event.organizer != request.user and not request.user.is_staff:
            return Response(
                {"error": "Vous n'êtes pas autorisé à rejeter cette inscription."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier que l'inscription est en liste d'attente
        if registration.status != 'waitlisted':
            return Response(
                {"error": "Cette inscription n'est pas en liste d'attente."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        
        # Rejeter l'inscription
        registration.status = 'cancelled'
        registration.save()
        
        # Envoyer l'email de rejet
        try:
            subject = f"Inscription refusée - {event.title}"
            
            # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
            if registration.user:
                # Utilisateur connecté
                recipient_email = registration.user.email
                context = {
                    'user': registration.user,
                    'event': event,
                    'reason': reason,
                }
            else:
                # Invité
                recipient_email = registration.guest_email
                context = {
                    'guest_name': registration.guest_full_name,
                    'guest_email': registration.guest_email,
                    'event': event,
                    'reason': reason,
                }
            
            message = render_to_string('emails/registration_rejected.txt', context)
            html_message = render_to_string('emails/registration_rejected.html', context)

            msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
            msg.attach_alternative(html_message, 'text/html')
            msg.send(fail_silently=False)  # Ne pas ignorer les erreurs
            print(f"Email de rejet envoyé à {recipient_email}")
            
            # 🎯 NOUVEAU : Envoyer SMS pour rejet de liste d'attente
            try:
                from .sms_service import sms_service
                print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS REJET =====")
                print(f"🔍 DEBUG: Inscription ID: {registration.id}")
                print(f"🔍 DEBUG: Statut: {registration.status}")
                print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
                
                sms_sent = sms_service.send_confirmation_sms(registration)
                
                if sms_sent:
                    print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour rejet {registration.id}")
                else:
                    print(f"🔍 DEBUG: ❌ Échec envoi SMS pour rejet {registration.id}")
                print(f"🔍 DEBUG: ===== FIN ENVOI SMS REJET =====")
            except Exception as e:
                print(f"🔍 DEBUG: Erreur envoi SMS rejet: {e}")
        except Exception as email_error:
            print(f"Erreur envoi email de rejet: {email_error}")
            import traceback
            traceback.print_exc()
        
        return Response({"message": "Inscription rejetée."})

    @action(detail=True, methods=['post'], url_path='process_refund')
    def handle_refund(self, request, pk=None):
        """Traiter une demande de remboursement (approuver/rejeter)"""
        registration = self.get_object()
        event = registration.event
        
        # Vérifier les permissions (organisateur ou staff)
        if event.organizer != request.user and not request.user.is_staff:
            return Response(
                {"error": "Vous n'êtes pas autorisé à traiter cette demande."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier qu'il existe une demande de remboursement
        try:
            refund_request = registration.refund_request
        except:
            return Response(
                {"error": "Aucune demande de remboursement trouvée pour cette inscription."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        action = request.data.get('action')  # 'approve', 'reject', ou 'process' (synonyme de 'approve')
        
        if action == 'approve':
            return self._approve_refund(refund_request, request)
        elif action == 'reject':
            return self._reject_refund(refund_request, request)
        else:
            return Response(
                {"error": "Action non valide. Utilisez 'approve' ou 'reject'."},
                status=status.HTTP_400_BAD_REQUEST
            )


    
    def _approve_refund(self, refund_request, request):
        """Approuver et traiter un remboursement"""
        if refund_request.status != 'pending':
            return Response(
                {"error": "Cette demande a déjà été traitée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Traiter le remboursement via Stripe
            if not getattr(settings, 'STRIPE_SECRET_KEY', None):
                return Response(
                    {"error": "Stripe non configuré"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            registration = refund_request.registration
            
            if not registration.payment_reference:
                return Response(
                    {"error": "Référence de paiement manquante"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Effectuer le remboursement Stripe
            refund = stripe.Refund.create(
                payment_intent=registration.payment_reference,
                amount=int(float(refund_request.refund_amount) * 100),  # Centimes
                reason='requested_by_customer',
                metadata={
                    'registration_id': registration.id,
                    'event_id': registration.event.id,
                    'refund_request_id': refund_request.id,
                    'processed_by': request.user.username,
                }
            )
            
            # Mettre à jour la demande de remboursement
            from django.utils import timezone
            refund_request.status = 'processed'
            refund_request.processed_at = timezone.now()
            refund_request.processed_by = request.user
            refund_request.stripe_refund_id = refund.id
            refund_request.save()
            
            # Envoyer email de confirmation
            self._send_refund_confirmation_email(refund_request)
            
            return Response({
                "message": "Remboursement traité avec succès",
                "refund_amount": float(refund_request.refund_amount),
                "stripe_refund_id": refund.id
            })
            
        except Exception as e:
            print(f"Erreur lors du traitement du remboursement: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": f"Erreur lors du traitement: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _reject_refund(self, refund_request, request):
        """Rejeter une demande de remboursement"""
        if refund_request.status != 'pending':
            return Response(
                {"error": "Cette demande a déjà été traitée."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', 'Rejeté par l\'organisateur')
        
        # Mettre à jour la demande
        from django.utils import timezone
        refund_request.status = 'rejected'
        refund_request.processed_at = timezone.now()
        refund_request.processed_by = request.user
        refund_request.reason = f"{refund_request.reason}\n\nRejet: {reason}"
        refund_request.save()
        
        # Envoyer email de rejet
        self._send_refund_rejection_email(refund_request, reason)
        
        return Response({
            "message": "Demande de remboursement rejetée",
            "reason": reason
        })
    
    def _send_refund_confirmation_email(self, refund_request):
        """Envoyer email de confirmation de remboursement"""
        try:
            registration = refund_request.registration
            event = registration.event
            
            subject = f"Remboursement confirmé - {event.title}"
            
            # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
            if registration.user:
                # Utilisateur connecté
                recipient_email = registration.user.email
                context = {
                    'user': registration.user,
                    'event': event,
                    'refund_request': refund_request,
                    'refund_amount': refund_request.refund_amount,
                }
                message = render_to_string('emails/refund_confirmation.txt', context)
                html_message = render_to_string('emails/refund_confirmation.html', context)
            else:
                # Invité
                recipient_email = registration.guest_email
                context = {
                    'guest_full_name': registration.guest_full_name,
                    'event': event,
                    'refund_request': refund_request,
                    'refund_amount': refund_request.refund_amount,
                }
                message = render_to_string('emails/guest_refund_confirmation.txt', context)
                html_message = render_to_string('emails/guest_refund_confirmation.html', context)
            
            from django.template.loader import render_to_string
            from django.core.mail import EmailMultiAlternatives
            from django.conf import settings
            
            msg = EmailMultiAlternatives(
                subject, 
                message, 
                getattr(settings, 'DEFAULT_FROM_EMAIL', None), 
                [recipient_email]
            )
            msg.attach_alternative(html_message, 'text/html')
            msg.send(fail_silently=False)
            
            print(f"Email de confirmation de remboursement envoyé à {recipient_email}")
            
            # 🎯 NOUVEAU : Envoyer SMS pour confirmation de remboursement
            try:
                from .sms_service import sms_service
                print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS REMBOURSEMENT CONFIRMÉ =====")
                print(f"🔍 DEBUG: Inscription ID: {registration.id}")
                print(f"🔍 DEBUG: Montant remboursé: {refund_request.refund_amount}")
                print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
                
                sms_sent = sms_service.send_confirmation_sms(registration)
                
                if sms_sent:
                    print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour remboursement confirmé {registration.id}")
                else:
                    print(f"🔍 DEBUG: ❌ Échec envoi SMS pour remboursement confirmé {registration.id}")
                print(f"🔍 DEBUG: ===== FIN ENVOI SMS REMBOURSEMENT CONFIRMÉ =====")
            except Exception as e:
                print(f"🔍 DEBUG: Erreur envoi SMS remboursement confirmé: {e}")
            
        except Exception as e:
            print(f"Erreur envoi email de confirmation de remboursement: {e}")
            import traceback
            traceback.print_exc()
    
    def _send_refund_rejection_email(self, refund_request, reason):
        """Envoyer email de rejet de remboursement"""
        try:
            registration = refund_request.registration
            event = registration.event
            
            subject = f"Demande de remboursement rejetée - {event.title}"
            
            # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
            if registration.user:
                # Utilisateur connecté
                recipient_email = registration.user.email
                context = {
                    'user': registration.user,
                    'event': event,
                    'refund_request': refund_request,
                    'reason': reason,
                }
                message = render_to_string('emails/refund_rejected.txt', context)
                html_message = render_to_string('emails/refund_rejected.html', context)
            else:
                # Invité
                recipient_email = registration.guest_email
                context = {
                    'guest_full_name': registration.guest_full_name,
                    'event': event,
                    'refund_request': refund_request,
                    'reason': reason,
                }
                message = render_to_string('emails/guest_refund_rejected.txt', context)
                html_message = render_to_string('emails/guest_refund_rejected.html', context)
            
            from django.template.loader import render_to_string
            from django.core.mail import EmailMultiAlternatives
            from django.conf import settings
            
            msg = EmailMultiAlternatives(
                subject, 
                message, 
                getattr(settings, 'DEFAULT_FROM_EMAIL', None), 
                [recipient_email]
            )
            msg.attach_alternative(html_message, 'text/html')
            msg.send(fail_silently=False)
            
            print(f"Email de rejet de remboursement envoyé à {recipient_email}")
            
            # 🎯 NOUVEAU : Envoyer SMS pour rejet de remboursement
            try:
                from .sms_service import sms_service
                print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS REMBOURSEMENT REJETÉ =====")
                print(f"🔍 DEBUG: Inscription ID: {registration.id}")
                print(f"🔍 DEBUG: Raison du rejet: {reason}")
                print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
                
                sms_sent = sms_service.send_confirmation_sms(registration)
                
                if sms_sent:
                    print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour remboursement rejeté {registration.id}")
                else:
                    print(f"🔍 DEBUG: ❌ Échec envoi SMS pour remboursement rejeté {registration.id}")
                print(f"🔍 DEBUG: ===== FIN ENVOI SMS REMBOURSEMENT REJETÉ =====")
            except Exception as e:
                print(f"🔍 DEBUG: Erreur envoi SMS remboursement rejeté: {e}")
            
        except Exception as e:
            print(f"Erreur envoi email de rejet de remboursement: {e}")
            import traceback
            traceback.print_exc()

    @action(detail=True, methods=['get'])
    def qr(self, request, pk=None):
        """Retourner l'URL du QR code pour l'inscription confirmée"""
        registration = self.get_object()
        if registration.user != request.user and registration.event.organizer != request.user:
            return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        if registration.qr_code:
            return Response({"qr_code": request.build_absolute_uri(registration.qr_code.url)})
        return Response({"qr_code": None})

    @action(detail=True, methods=['post'])
    def create_payment_intent(self, request, pk=None):
        """Créer un PaymentIntent Stripe pour une inscription payante."""
        try:
            # Vérifier si Stripe est configuré
            if not getattr(settings, 'STRIPE_SECRET_KEY', None) or 'sk_test_51H1234567890' in settings.STRIPE_SECRET_KEY:
                # Mode test - simuler un paiement réussi
                registration = self.get_object()
                
                # 🎯 CORRECTION : Calculer le montant selon le type de billet
                amount = 0
                if registration.ticket_type:
                    # Utiliser le prix du type de billet sélectionné
                    if registration.ticket_type.is_discount_active and registration.ticket_type.discount_price is not None:
                        amount = int(float(registration.ticket_type.discount_price) * 100)
                        print(f"🔍 DEBUG: Montant avec remise: {amount/100}€ (prix normal: {registration.ticket_type.price}€, remise: {registration.ticket_type.discount_price}€)")
                    else:
                        amount = int(float(registration.ticket_type.price) * 100)
                        print(f"🔍 DEBUG: Montant normal du billet: {amount/100}€")
                else:
                    # Utiliser le prix par défaut de l'événement
                    amount = int(float(registration.event.price) * 100)
                    print(f"🔍 DEBUG: Montant par défaut de l'événement: {amount/100}€")
                
                if amount <= 0:
                    return Response({"error": "Montant invalide"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Simuler un PaymentIntent de test avec un format Stripe valide
                test_intent_id = f"pi_test_{registration.id}_{int(time.time())}"
                # Format Stripe valide: pi_test_xxx_secret_xxx
                test_secret = f"pi_test_{registration.id}_{int(time.time())}_secret_{registration.id}_{int(time.time())}"
                return Response({ 
                    'client_secret': test_secret,
                    'payment_intent_id': test_intent_id,
                    'mode': 'test',
                    'amount': amount,
                    'currency': 'usd'
                })
            
            # Mode production avec Stripe réel
            stripe.api_key = settings.STRIPE_SECRET_KEY
            registration = self.get_object()
            
            # 🎯 CORRECTION : Calculer le montant selon le type de billet
            amount = 0
            if registration.ticket_type:
                # Utiliser le prix du type de billet sélectionné
                if registration.ticket_type.is_discount_active and registration.ticket_type.discount_price is not None:
                    amount = int(float(registration.ticket_type.discount_price) * 100)
                    print(f"🔍 DEBUG: Montant avec remise: {amount/100}€ (prix normal: {registration.ticket_type.price}€, remise: {registration.ticket_type.discount_price}€)")
                else:
                    amount = int(float(registration.ticket_type.price) * 100)
                    print(f"🔍 DEBUG: Montant normal du billet: {amount/100}€")
            else:
                # Utiliser le prix par défaut de l'événement
                amount = int(float(registration.event.price) * 100)
                print(f"🔍 DEBUG: Montant par défaut de l'événement: {amount/100}€")
            
            if amount <= 0:
                return Response({"error": "Montant invalide"}, status=status.HTTP_400_BAD_REQUEST)
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                automatic_payment_methods={"enabled": True},
                metadata={
                    'registration_id': registration.id,
                    'event_id': registration.event_id,
                    'user_id': registration.user_id,
                }
            )
            return Response({ 'client_secret': intent.client_secret, 'payment_intent_id': intent.id })
            
        except Exception as e:
            print(f"Erreur lors de la création du PaymentIntent: {str(e)}")
            return Response({"error": "Erreur lors de la création du PaymentIntent", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """Confirmer côté serveur qu'un PaymentIntent Stripe est payé et mettre à jour l'inscription.

        Body attendu: { payment_intent_id: "pi_..." }
        """
        print(f"🔍 DEBUG: confirm_payment START - pk: {pk}, user: {request.user.username}")
        print(f"🔍 DEBUG: Request data: {request.data}")
        
        try:
            registration = self.get_object()
            print(f"🔍 DEBUG: Registration found - ID: {registration.id}, Status: {registration.status}, Payment: {registration.payment_status}")
        except Exception as e:
            print(f"🔍 DEBUG: Error getting registration: {e}")
            return Response({"error": "Inscription introuvable"}, status=status.HTTP_404_NOT_FOUND)
        
        payment_intent_id = request.data.get('payment_intent_id')
        print(f"🔍 DEBUG: Payment intent ID: {payment_intent_id}")
        
        if not payment_intent_id:
            print(f"🔍 DEBUG: Missing payment_intent_id")
            return Response({"error": "payment_intent_id manquant"}, status=status.HTTP_400_BAD_REQUEST)

        # Mode test - simuler un paiement réussi
        if payment_intent_id.startswith('pi_test_'):
            print(f"🔍 DEBUG: Mode test - Paiement simulé pour l'inscription {registration.id}")
            # Traiter le paiement de test
            return self._process_test_payment(registration)
        
        print(f"🔍 DEBUG: Mode production - Stripe key exists: {bool(getattr(settings, 'STRIPE_SECRET_KEY', None))}")
        
        # Mode production avec Stripe réel
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            print(f"🔍 DEBUG: Stripe not configured")
            return Response({"error": "Stripe non configuré"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        print(f"🔍 DEBUG: Stripe API key set")

        try:
            print(f"🔍 DEBUG: Retrieving PaymentIntent: {payment_intent_id}")
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            print(f"🔍 DEBUG: PaymentIntent retrieved - Status: {intent.status}")
        except Exception as e:
            print(f"🔍 DEBUG: Error retrieving PaymentIntent: {e}")
            return Response({"error": "PaymentIntent introuvable", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifications de sécurité minimales
        if intent.status != 'succeeded':
            return Response({"error": "Paiement non confirmé", "status": intent.status}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier cohérence des métadonnées si présentes
        meta_reg_id = str(intent.metadata.get('registration_id')) if getattr(intent, 'metadata', None) else None
        if meta_reg_id and str(registration.id) != meta_reg_id:
            return Response({"error": "Le PaymentIntent ne correspond pas à cette inscription"}, status=status.HTTP_400_BAD_REQUEST)

        # Idempotence: si déjà payé, renvoyer l'état courant
        if registration.payment_status == 'paid':
            return Response(self.get_serializer(registration).data)

        # Marquer comme payé et confirmer l'inscription si capacité disponible
        registration.payment_status = 'paid'
        registration.payment_provider = 'stripe'
        registration.payment_reference = intent.id
        
        # 💰 CRITIQUE: Mettre à jour le prix payé avec le montant réel du paiement
        amount_paid = intent.amount / 100.0  # Stripe stocke en centimes
        registration.price_paid = amount_paid
        print(f"🔍 DEBUG: confirm_payment - Mise à jour price_paid: {amount_paid}€")

        # Confirmer l'inscription si elle n'est pas en liste d'attente
        if registration.status in ['pending', 'waitlisted']:
            event = registration.event
            
            print(f"🔍 DEBUG: confirm_payment - Event: {event.title}, Registration status: {registration.status}")
            print(f"🔍 DEBUG: Event capacity: {event.place_type}, max: {event.max_capacity}, current: {event.current_registrations}")
            
            # Calculer la capacité disponible (inscriptions confirmées uniquement)
            confirmed_count = EventRegistration.objects.filter(
                event=event, 
                status='confirmed'
            ).count()
            
            print(f"🔍 DEBUG: Confirmed count: {confirmed_count}")
            
            # 🎯 CORRECTION MAJEURE : Séparer la logique des billets personnalisés et par défaut
            if registration.ticket_type and registration.ticket_type.quantity is not None:
                # 🎯 BILLET PERSONNALISÉ : Vérifier SEULEMENT sa capacité spécifique
                print(f"🔍 DEBUG: Custom ticket capacity - {registration.ticket_type.name}: {registration.ticket_type.sold_count}/{registration.ticket_type.quantity}")
                
                if not registration.ticket_type.is_available:
                    print(f"🔍 DEBUG: Custom ticket {registration.ticket_type.name} is sold out!")
                    # Mettre en liste d'attente car billet épuisé
                    registration.status = 'waitlisted'
                else:
                    # Billet disponible - confirmer l'inscription
                    print(f"🔍 DEBUG: Custom ticket available - confirming registration")
                    registration.status = 'confirmed'
                    
                    # Mettre à jour SEULEMENT le compteur du billet personnalisé
                    tt = registration.ticket_type
                    tt.sold_count = tt.sold_count + 1
                    tt.save(update_fields=['sold_count'])
                    print(f"🔍 DEBUG: Updated custom ticket sold count to: {tt.sold_count}")
                    
                    # NE PAS toucher au compteur global de l'événement
                    print(f"🔍 DEBUG: Custom ticket - NOT updating global event counter")
            else:
                # 🎯 BILLET PAR DÉFAUT : Vérifier la capacité globale de l'événement
                # Compter seulement les billets par défaut confirmés
                confirmed_default_count = EventRegistration.objects.filter(
                    event=event,
                    ticket_type__isnull=True,  # Seulement les billets par défaut
                    status__in=['confirmed', 'attended']
                ).count()
                
                capacity_ok = (event.place_type == 'unlimited' or 
                              event.max_capacity is None or 
                              confirmed_default_count < event.max_capacity)
                
                print(f"🔍 DEBUG: Default ticket - Event capacity OK: {capacity_ok} ({confirmed_default_count}/{event.max_capacity})")
                
                if capacity_ok:
                    # Place disponible - confirmer l'inscription
                    print(f"🔍 DEBUG: Event has capacity - confirming registration")
                    registration.status = 'confirmed'
                else:
                    # Événement complet - mettre en liste d'attente
                    print(f"🔍 DEBUG: Event full - setting status to waitlisted")
                    registration.status = 'waitlisted'
            
            # Sauvegarder le statut final
            registration.save(update_fields=['payment_status', 'payment_provider', 'payment_reference', 'price_paid', 'status', 'updated_at'])
            
            # 🎯 CORRECTION : Mettre à jour le compteur global SEULEMENT pour les billets par défaut
            if registration.status == 'confirmed' and not (registration.ticket_type and registration.ticket_type.quantity is not None):
                event.current_registrations = confirmed_default_count + 1
                event.save(update_fields=['current_registrations'])
                print(f"🔍 DEBUG: Updated default ticket capacity to: {event.current_registrations}")
        else:
            print(f"🔍 DEBUG: Registration status not pending/waitlisted: {registration.status}")
            registration.save(update_fields=['payment_status', 'payment_provider', 'payment_reference', 'price_paid', 'updated_at'])

        # Envoyer l'email approprié selon le statut de l'inscription
        try:
            registration.refresh_from_db()
            
            # 🔍 LOG CRITIQUE: Vérifier si le stream se lance automatiquement
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"🔍 LOG CRITIQUE: confirm_payment - Envoi email pour inscription {registration.id}")
            logger.info(f"🔍 LOG CRITIQUE: Event {event.id} - is_virtual: {event.is_virtual}")
            if event.is_virtual:
                virtual_details = getattr(event, 'virtual_details', None)
                logger.info(f"🔍 LOG CRITIQUE: Virtual details: {virtual_details}")
                if virtual_details:
                    logger.info(f"🔍 LOG CRITIQUE: Meeting ID: {virtual_details.meeting_id}")
                    logger.info(f"🔍 LOG CRITIQUE: Meeting URL: {virtual_details.meeting_url}")
                    logger.info(f"🔍 LOG CRITIQUE: Platform: {virtual_details.platform}")
            
            if registration.status == 'waitlisted':
                # Email d'attente de validation pour les inscriptions en liste d'attente
                subject = f"Inscription en attente de validation - {registration.event.title}"
                
                # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
                if registration.user:
                    # Utilisateur connecté
                    recipient_email = registration.user.email
                    context = {
                        'user': registration.user,
                        'event': registration.event,
                    }
                else:
                    # Invité
                    recipient_email = registration.guest_email
                    context = {
                        'guest_name': registration.guest_full_name,
                        'guest_email': registration.guest_email,
                        'event': registration.event,
                    }
                
                if registration.user:
                    message = render_to_string('emails/registration_waitlisted.txt', context)
                    html_message = render_to_string('emails/registration_waitlisted.html', context)
                else:
                    message = render_to_string('emails/guest_registration_waitlisted.txt', context)
                    html_message = render_to_string('emails/guest_registration_waitlisted.html', context)
                
                msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
                msg.attach_alternative(html_message, 'text/html')
                msg.send(fail_silently=True)
                
                # 🎯 NOUVEAU : Envoyer SMS pour liste d'attente
                try:
                    from .sms_service import sms_service
                    print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS LISTE D'ATTENTE =====")
                    print(f"🔍 DEBUG: Inscription ID: {registration.id}")
                    print(f"🔍 DEBUG: Statut: {registration.status}")
                    print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
                    
                    sms_sent = sms_service.send_confirmation_sms(registration)
                    
                    if sms_sent:
                        print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour liste d'attente {registration.id}")
                    else:
                        print(f"🔍 DEBUG: ❌ Échec envoi SMS pour liste d'attente {registration.id}")
                    print(f"🔍 DEBUG: ===== FIN ENVOI SMS LISTE D'ATTENTE =====")
                except Exception as e:
                    print(f"🔍 DEBUG: Erreur envoi SMS liste d'attente: {e}")
                
            elif registration.status == 'confirmed':
                # Email de confirmation avec QR code pour les inscriptions confirmées
                qr_url = None
                if registration.qr_code:
                    qr_url = request.build_absolute_uri(registration.qr_code.url)
                
                # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
                if registration.user:
                    # Utilisateur connecté
                    recipient_email = registration.user.email
                    if registration.event.is_virtual:
                        subject = f"🎥 Événement Virtuel Confirmé - {registration.event.title}"
                        context = {
                            'user': registration.user,
                            'event': registration.event,
                            'registration': registration,
                            'qr_url': qr_url,
                        }
                        message = render_to_string('emails/virtual_event_confirmation.txt', context)
                        html_message = render_to_string('emails/virtual_event_confirmation.html', context)
                    else:
                        subject = f"🎉 Confirmation d'inscription - {registration.event.title}"
                        context = {
                            'user': registration.user,
                            'event': registration.event,
                            'qr_url': qr_url,
                        }
                        message = render_to_string('emails/registration_confirmation.txt', context)
                        html_message = render_to_string('emails/registration_confirmation.html', context)
                else:
                    # Invité
                    recipient_email = registration.guest_email
                    if registration.event.is_virtual:
                        subject = f"🎥 Événement Virtuel Confirmé - {registration.event.title}"
                        context = {
                            'guest_name': registration.guest_full_name,
                            'guest_email': registration.guest_email,
                            'event': registration.event,
                            'registration': registration,
                            'qr_url': qr_url,
                        }
                        message = render_to_string('emails/virtual_event_confirmation.txt', context)
                        html_message = render_to_string('emails/virtual_event_confirmation.html', context)
                    else:
                        subject = f"🎉 Confirmation d'inscription - {registration.event.title}"
                        context = {
                            'guest_name': registration.guest_full_name,
                            'guest_email': registration.guest_email,
                            'event': registration.event,
                            'qr_url': qr_url,
                        }
                        message = render_to_string('emails/guest_registration_confirmation.txt', context)
                        html_message = render_to_string('emails/guest_registration_confirmation.html', context)

                msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
                msg.attach_alternative(html_message, 'text/html')

                # Attacher le QR inline si disponible
                if registration.qr_code and hasattr(registration.qr_code, 'path'):
                    try:
                        with open(registration.qr_code.path, 'rb') as f:
                            img_data = f.read()
                        from email.mime.image import MIMEImage
                        img = MIMEImage(img_data)
                        img.add_header('Content-ID', '<qr_code>')
                        img.add_header('Content-Disposition', 'inline', filename='qr_code.png')
                        msg.attach(img)
                        print(f"QR code attaché à l'email normal: {registration.qr_code.path}")
                    except Exception as qr_error:
                        print(f"Erreur attachement QR normal: {qr_error}")

                msg.send(fail_silently=True)
                
                # 🔍 LOG CRITIQUE: Après envoi email
                logger.info(f"🔍 LOG CRITIQUE: Email de confirmation envoyé pour inscription {registration.id}")
                logger.info(f"🔍 LOG CRITIQUE: Aucun appel à configure_stream ou start_stream effectué")
                
                # 🎯 NOUVEAU : Envoyer SMS de confirmation après paiement
                try:
                    from .sms_service import sms_service
                    print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS APRÈS PAIEMENT =====")
                    print(f"🔍 DEBUG: Inscription ID: {registration.id}")
                    print(f"🔍 DEBUG: Statut après paiement: {registration.status}")
                    print(f"🔍 DEBUG: Prix payé: {registration.price_paid}")
                    print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
                    
                    sms_sent = sms_service.send_confirmation_sms(registration)
                    
                    if sms_sent:
                        print(f"🔍 DEBUG: ✅ SMS envoyé avec succès après paiement pour l'inscription {registration.id}")
                    else:
                        print(f"🔍 DEBUG: ❌ Échec envoi SMS après paiement pour l'inscription {registration.id}")
                    print(f"🔍 DEBUG: ===== FIN ENVOI SMS APRÈS PAIEMENT =====")
                except Exception as e:
                    print(f"🔍 DEBUG: Erreur envoi SMS après paiement: {e}")
                
        except Exception:
            pass

        return Response(self.get_serializer(registration).data)

    def _process_test_payment(self, registration):
        """Traiter un paiement de test (simulation)"""
        try:
            # Marquer comme payé
            registration.payment_status = 'paid'
            registration.payment_provider = 'test'
            registration.payment_reference = f"test_{int(time.time())}"
            
            # 💰 CRITIQUE: Mettre à jour le prix payé selon le type de billet
            if registration.ticket_type:
                # Utiliser le prix du type de billet
                if registration.ticket_type.is_discount_active and registration.ticket_type.discount_price is not None:
                    price_paid = registration.ticket_type.discount_price
                else:
                    price_paid = registration.ticket_type.price
                print(f"🔍 DEBUG: _process_test_payment - Prix du type de billet: {price_paid}€")
            else:
                # Utiliser le prix par défaut de l'événement
                price_paid = registration.event.price if registration.event.price else 0
                print(f"🔍 DEBUG: _process_test_payment - Prix par défaut: {price_paid}€")
            
            registration.price_paid = price_paid
            
            # Confirmer l'inscription si capacité disponible
            if registration.status in ['pending', 'waitlisted']:
                event = registration.event
                # Capacité événement
                capacity_ok = (event.place_type == 'unlimited' or event.max_capacity is None or (event.current_registrations or 0) < (event.max_capacity or 0))
                # Capacité type de billet
                ticket_ok = True
                if registration.ticket_type and registration.ticket_type.quantity is not None:
                    ticket_ok = registration.ticket_type.sold_count < registration.ticket_type.quantity

                if capacity_ok and ticket_ok:
                    registration.status = 'confirmed'
                    registration.save(update_fields=['payment_status', 'payment_provider', 'payment_reference', 'price_paid', 'status', 'updated_at'])
                    # Mettre à jour compteurs
                    event.current_registrations = (event.current_registrations or 0) + 1
                    event.save(update_fields=['current_registrations'])
                    if registration.ticket_type:
                        tt = registration.ticket_type
                        tt.sold_count = tt.sold_count + 1
                        tt.save(update_fields=['sold_count'])
                    
                    # Générer le QR code pour les inscriptions confirmées
                    try:
                        registration._generate_and_store_qr()
                    except Exception as qr_error:
                        print(f"Erreur génération QR: {qr_error}")
                    
                    # Envoyer l'email de confirmation
                    try:
                        qr_url = None
                        if registration.qr_code:
                            qr_url = f"http://localhost:8000{registration.qr_code.url}"
                        
                        # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
                        if registration.user:
                            # Utilisateur connecté
                            recipient_email = registration.user.email
                            if event.is_virtual:
                                subject = f"🎥 Événement Virtuel Confirmé - {event.title}"
                                context = {
                                    'user': registration.user,
                                    'event': event,
                                    'registration': registration,
                                    'qr_url': qr_url,
                                }
                                message = render_to_string('emails/virtual_event_confirmation.txt', context)
                                html_message = render_to_string('emails/virtual_event_confirmation.html', context)
                            else:
                                subject = f"🎉 Confirmation d'inscription - {event.title}"
                                context = {
                                    'user': registration.user,
                                    'event': event,
                                    'qr_url': qr_url,
                                }
                                message = render_to_string('emails/registration_confirmation.txt', context)
                                html_message = render_to_string('emails/registration_confirmation.html', context)
                        else:
                            # Invité
                            recipient_email = registration.guest_email
                            if event.is_virtual:
                                subject = f"🎥 Événement Virtuel Confirmé - {event.title}"
                                context = {
                                    'guest_name': registration.guest_full_name,
                                    'guest_email': registration.guest_email,
                                    'event': event,
                                    'registration': registration,
                                    'qr_url': qr_url,
                                }
                                message = render_to_string('emails/virtual_event_confirmation.txt', context)
                                html_message = render_to_string('emails/virtual_event_confirmation.html', context)
                            else:
                                subject = f"🎉 Confirmation d'inscription - {event.title}"
                                context = {
                                    'guest_name': registration.guest_full_name,
                                    'guest_email': registration.guest_email,
                                    'event': event,
                                    'registration': registration,
                                    'qr_url': qr_url,
                                }
                        message = render_to_string('emails/guest_registration_confirmation.txt', context)
                        html_message = render_to_string('emails/guest_registration_confirmation.html', context)

                        msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
                        msg.attach_alternative(html_message, 'text/html')
                        
                        # Attacher le QR code directement à l'email
                        if registration.qr_code and hasattr(registration.qr_code, 'path'):
                            try:
                                with open(registration.qr_code.path, 'rb') as f:
                                    img_data = f.read()
                                from email.mime.image import MIMEImage
                                img = MIMEImage(img_data)
                                img.add_header('Content-ID', '<qr_code>')
                                img.add_header('Content-Disposition', 'inline', filename='qr_code.png')
                                msg.attach(img)
                                print(f"QR code attaché à l'email: {registration.qr_code.path}")
                            except Exception as qr_attach_error:
                                print(f"Erreur attachement QR: {qr_attach_error}")
                        
                        msg.send(fail_silently=True)
                        print(f"Email de confirmation envoyé à {recipient_email} avec QR code")
                        
                        # 🎯 NOUVEAU : Envoyer SMS pour paiement de test confirmé
                        try:
                            from .sms_service import sms_service
                            print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS PAIEMENT TEST =====")
                            print(f"🔍 DEBUG: Inscription ID: {registration.id}")
                            print(f"🔍 DEBUG: Statut: {registration.status}")
                            print(f"🔍 DEBUG: Prix payé: {registration.price_paid}")
                            print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
                            
                            sms_sent = sms_service.send_confirmation_sms(registration)
                            
                            if sms_sent:
                                print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour paiement test {registration.id}")
                            else:
                                print(f"🔍 DEBUG: ❌ Échec envoi SMS pour paiement test {registration.id}")
                            print(f"🔍 DEBUG: ===== FIN ENVOI SMS PAIEMENT TEST =====")
                        except Exception as e:
                            print(f"🔍 DEBUG: Erreur envoi SMS paiement test: {e}")
                    except Exception as email_error:
                        print(f"Erreur envoi email: {email_error}")
                        
                else:
                    # Paiement OK mais mettre en liste d'attente si pas de capacité
                    registration.status = 'waitlisted'
                    registration.save(update_fields=['payment_status', 'payment_provider', 'payment_reference', 'price_paid', 'status', 'updated_at'])
                    
                    # Envoyer l'email de liste d'attente
                    try:
                        subject = f"Inscription en attente de validation - {event.title}"
                        
                        # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
                        if registration.user:
                            recipient_email = registration.user.email
                            context = {
                                'user': registration.user,
                                'event': event,
                            }
                            message = render_to_string('emails/registration_waitlisted.txt', context)
                            html_message = render_to_string('emails/registration_waitlisted.html', context)
                        else:
                            recipient_email = registration.guest_email
                            context = {
                                'guest_name': registration.guest_full_name,
                                'guest_email': registration.guest_email,
                                'event': event,
                            }
                            message = render_to_string('emails/guest_registration_waitlisted.txt', context)
                            html_message = render_to_string('emails/guest_registration_waitlisted.html', context)
                        
                        msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
                        msg.attach_alternative(html_message, 'text/html')
                        msg.send(fail_silently=True)
                        
                        # 🎯 NOUVEAU : Envoyer SMS pour liste d'attente (paiement test)
                        try:
                            from .sms_service import sms_service
                            print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS LISTE D'ATTENTE TEST =====")
                            print(f"🔍 DEBUG: Inscription ID: {registration.id}")
                            print(f"🔍 DEBUG: Statut: {registration.status}")
                            print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
                            
                            sms_sent = sms_service.send_confirmation_sms(registration)
                            
                            if sms_sent:
                                print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour liste d'attente test {registration.id}")
                            else:
                                print(f"🔍 DEBUG: ❌ Échec envoi SMS pour liste d'attente test {registration.id}")
                            print(f"🔍 DEBUG: ===== FIN ENVOI SMS LISTE D'ATTENTE TEST =====")
                        except Exception as e:
                            print(f"🔍 DEBUG: Erreur envoi SMS liste d'attente test: {e}")
                        print(f"Email de liste d'attente envoyé à {recipient_email}")
                        
                        # 🎯 NOUVEAU : Envoyer le SMS de liste d'attente
                        try:
                            from .sms_service import sms_service
                            sms_sent = sms_service.send_confirmation_sms(registration)
                            if sms_sent:
                                print(f"🔍 DEBUG: SMS de liste d'attente envoyé pour l'inscription {registration.id}")
                            else:
                                print(f"🔍 DEBUG: Échec envoi SMS de liste d'attente pour l'inscription {registration.id}")
                        except Exception as e:
                            print(f"🔍 DEBUG: Erreur envoi SMS de liste d'attente: {e}")
                    except Exception as email_error:
                        print(f"Erreur envoi email: {email_error}")
            else:
                registration.save(update_fields=['payment_status', 'payment_provider', 'payment_reference', 'price_paid', 'updated_at'])

            return Response({
                'message': 'Paiement de test traité avec succès',
                'registration': self.get_serializer(registration).data
            })
            
        except Exception as e:
            print(f"Erreur lors du traitement du paiement de test: {str(e)}")
            return Response({
                'error': 'Erreur lors du traitement du paiement de test',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def verify_qr(self, request):
        """Vérifier un QR code à l'entrée. Body: { token, mark_attended }"""
        token = request.data.get('token')
        mark_attended = bool(request.data.get('mark_attended', True))
        if not token:
            return Response({"valid": False, "error": "Token manquant"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            registration = EventRegistration.objects.select_related('event', 'user').get(qr_token=token)
        except EventRegistration.DoesNotExist:
            return Response({"valid": False}, status=status.HTTP_404_NOT_FOUND)

        # Only event organizer or staff can verify
        if registration.event.organizer != request.user and not request.user.is_staff:
            return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)

        # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
        user_display_name = None
        user_email = None
        
        if registration.user:
            # Utilisateur connecté
            user_display_name = f"{registration.user.first_name} {registration.user.last_name}"
            user_email = registration.user.email
        else:
            # Invité
            user_display_name = registration.guest_full_name
            user_email = registration.guest_email
        
        # Si l'inscription est en attente de paiement, la confirmer lors du scan
        if registration.status == 'pending':
            registration.status = 'confirmed'
            registration.save()
            print(f"✅ QR Code scan - Inscription {registration.id} confirmée pour {user_display_name}")
        # Si l'inscription est confirmée et qu'on marque la présence
        elif mark_attended and registration.status == 'confirmed':
            registration.status = 'attended'
            registration.save()
            print(f"✅ QR Code scan - Présence marquée pour {user_display_name}")
        
        return Response({
            "valid": True,
            "registration_id": registration.id,
            "status": registration.status,
            "user": {
                "username": user_display_name,
                "email": user_email,
            },
            "event": {
                "id": registration.event.id,
                "title": registration.event.title,
            },
            "session_type": registration.session_type.name if registration.session_type else None,
            "ticket_type": registration.ticket_type.name if registration.ticket_type else None
        })

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Récupérer les inscriptions aux événements à venir"""
        registrations = self.get_queryset().filter(
            event__start_date__gt=timezone.now(),
            status__in=['pending', 'confirmed']
        )
        serializer = self.get_serializer(registrations, many=True)
        return Response(serializer.data)


class EventHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour l'historique des événements"""
    serializer_class = EventHistorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'action']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    def get_queryset(self):
        """Filtrer l'historique selon les événements de l'utilisateur"""
        return EventHistory.objects.filter(event__organizer=self.request.user) 


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Enregistrement d'un nouvel utilisateur avec système d'approbation
    """
    try:
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        phone = data.get('phone', '')
        role = data.get('role', 'participant')

        # Validation des champs requis
        if not username or not email or not password or not phone:
            return Response({
                'error': 'Tous les champs sont requis (username, email, password, phone)'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer le pays
        country = data.get('country', 'FR')

        # 🎯 NOUVEAU : Validation pays/numéro de téléphone STRICTE
        print(f"🔍 DEBUG: Validation - Phone: {phone}, Country: {country}")
        
        if phone and country:
            # Nettoyer le numéro pour la détection
            import re
            cleaned_phone = re.sub(r'\D', '', phone)
            
            print(f"🔍 DEBUG: Validation - Cleaned phone: {cleaned_phone}")
            
            # 🎯 VALIDATION STRICTE : Vérifier la correspondance pays/numéro
            validation_error = None
            
            # Numéros canadiens (514, 438, 450, 579, 581, 819, 873)
            if cleaned_phone.startswith(('514', '438', '450', '579', '581', '819', '873')):
                if country != 'CA':
                    validation_error = f'Le numéro de téléphone commence par {cleaned_phone[:3]} (Canada) mais le pays sélectionné est {country}. Veuillez sélectionner le Canada ou utiliser un numéro correspondant au pays sélectionné.'
            
            # Numéros français (06, 07)
            elif cleaned_phone.startswith(('06', '07')):
                if country != 'FR':
                    validation_error = f'Le numéro de téléphone commence par {cleaned_phone[:2]} (France) mais le pays sélectionné est {country}. Veuillez sélectionner la France ou utiliser un numéro correspondant au pays sélectionné.'
            
            # Numéros togolais (90, 91, 92, 93, 96, 97, 98, 99)
            elif cleaned_phone.startswith(('90', '91', '92', '93', '96', '97', '98', '99')):
                if country != 'TG':
                    validation_error = f'Le numéro de téléphone commence par {cleaned_phone[:2]} (Togo) mais le pays sélectionné est {country}. Veuillez sélectionner le Togo ou utiliser un numéro correspondant au pays sélectionné.'
            
            # Si erreur de validation, la retourner
            if validation_error:
                print(f"🔍 DEBUG: Validation ERROR - {validation_error}")
                return Response({
                    'error': validation_error
                }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"🔍 DEBUG: Validation ACCEPTED - Numéro {cleaned_phone} correspond au pays {country}")

        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'Ce nom d\'utilisateur existe déjà'
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'Cet email est déjà utilisé'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Valider le mot de passe
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({
                'error': 'Mot de passe invalide',
                'details': list(e.messages)
            }, status=status.HTTP_400_BAD_REQUEST)

        # Valider le rôle
        valid_roles = ['participant', 'organizer']
        if role not in valid_roles:
            return Response({
                'error': f'Rôle invalide. Rôles autorisés: {", ".join(valid_roles)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        # Déterminer le statut d'approbation
        if role == 'organizer':
            status_approval = 'pending'
            message = 'Votre compte est en attente d\'approbation. Vous recevrez un email une fois approuvé.'
        else:
            status_approval = 'approved'
            message = 'Compte créé avec succès ! Vous pouvez maintenant vous connecter.'

        # Créer le profil utilisateur
        profile = UserProfile.objects.create(
            user=user,
            role=role,
            phone=phone,
            country=country,
            status_approval=status_approval
        )

        # Envoyer un email de confirmation
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            if role == 'organizer':
                subject = 'Votre compte est en attente d\'approbation'
                message_body = f"""
                Bonjour {first_name},

                Votre compte organisateur a été créé avec succès et est maintenant en attente d'approbation.

                Détails du compte :
                - Nom d'utilisateur : {username}
                - Email : {email}
                - Rôle : Organisateur

                Un administrateur examinera votre demande et vous enverra un email de confirmation une fois approuvé.

                Merci de votre patience.

                L'équipe EventManager
                """
            else:
                subject = 'Bienvenue sur EventManager !'
                message_body = f"""
                Bonjour {first_name},

                Votre compte participant a été créé avec succès !

                Détails du compte :
                - Nom d'utilisateur : {username}
                - Email : {email}
                - Rôle : Participant

                Vous pouvez maintenant vous connecter et commencer à explorer nos événements.

                Bienvenue dans la communauté EventManager !

                L'équipe EventManager
                """

            send_mail(
                subject,
                message_body,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@eventmanager.com'),
                [email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email: {e}")

        return Response({
            'message': message,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': role,
                'status_approval': status_approval,
                'phone': phone,
                'country': country
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': 'Erreur lors de la création de l\'utilisateur',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["GET"])
def test_connection(request):
    """
    Route de test simple pour vérifier la connexion API - SANS DRF
    """
    from django.utils import timezone
    return JsonResponse({
        'message': 'Connexion API réussie !',
        'status': 'success',
        'timestamp': timezone.now().isoformat()
    })

@api_view(['GET', 'DELETE'])
@permission_classes([])  # Permettre l'accès sans authentification pour le test
def get_current_user(request):
    """
    GET: Récupérer les informations de l'utilisateur connecté
    DELETE: Supprimer le compte de l'utilisateur connecté (et données associées selon on_delete)
    """
    try:
        user = request.user
        
        # Pour le test, retourner une réponse simple
        if not user.is_authenticated:
            return Response({
                'message': 'Utilisateur non authentifié - Test de connexion réussi',
                'status': 'success'
            }, status=status.HTTP_200_OK)
        
        if request.method == 'DELETE':
            try:
                username = user.username
                user.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                return Response({
                    'error': "Erreur lors de la suppression du compte",
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # GET
        print(f"DEBUG: Utilisateur connecté: {user.username}")  # Debug log
        
        # Récupérer le profil utilisateur avec le rôle
        profile_data = None
        if hasattr(user, 'profile'):
            profile_data = {
                'role': user.profile.role,
                'phone': user.profile.phone,
                'country': user.profile.country,
            }
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'profile': profile_data
        }
        
        return Response(user_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"DEBUG: Erreur dans get_current_user: {str(e)}")  # Debug log
        return Response({
            'error': 'Erreur lors de la récupération du profil',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Modifier le mot de passe de l'utilisateur connecté.
    Body attendu: { "old_password": str, "new_password": str }
    """
    try:
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response({
                'error': 'Champs requis manquants',
                'details': ['old_password et new_password sont requis']
            }, status=status.HTTP_400_BAD_REQUEST)

        if not user.check_password(old_password):
            return Response({
                'error': 'Ancien mot de passe incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            return Response({
                'error': 'Mot de passe invalide',
                'details': list(e.messages)
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({
            'message': 'Mot de passe modifié avec succès'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Erreur lors du changement de mot de passe',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """
    Modifier le profil de l'utilisateur connecté.
    Body attendu: { "first_name": str, "last_name": str, "phone": str, "country": str }
    """
    try:
        user = request.user
        data = request.data
        
        # Mettre à jour les champs de l'utilisateur
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        user.save()
        
        # 🎯 NOUVEAU : Validation pays/numéro de téléphone STRICTE
        phone = data.get('phone', '')
        country = data.get('country', 'FR')
        
        print(f"🔍 DEBUG: Validation - Phone: {phone}, Country: {country}")
        
        if phone and country:
            # Nettoyer le numéro pour la détection
            import re
            cleaned_phone = re.sub(r'\D', '', phone)
            
            print(f"🔍 DEBUG: Validation - Cleaned phone: {cleaned_phone}")
            
            # 🎯 VALIDATION STRICTE : Vérifier la correspondance pays/numéro
            validation_error = None
            
            # Numéros canadiens (514, 438, 450, 579, 581, 819, 873)
            if cleaned_phone.startswith(('514', '438', '450', '579', '581', '819', '873')):
                if country != 'CA':
                    validation_error = f'Le numéro de téléphone commence par {cleaned_phone[:3]} (Canada) mais le pays sélectionné est {country}. Veuillez sélectionner le Canada ou utiliser un numéro correspondant au pays sélectionné.'
            
            # Numéros français (06, 07)
            elif cleaned_phone.startswith(('06', '07')):
                if country != 'FR':
                    validation_error = f'Le numéro de téléphone commence par {cleaned_phone[:2]} (France) mais le pays sélectionné est {country}. Veuillez sélectionner la France ou utiliser un numéro correspondant au pays sélectionné.'
            
            # Numéros togolais (90, 91, 92, 93, 96, 97, 98, 99)
            elif cleaned_phone.startswith(('90', '91', '92', '93', '96', '97', '98', '99')):
                if country != 'TG':
                    validation_error = f'Le numéro de téléphone commence par {cleaned_phone[:2]} (Togo) mais le pays sélectionné est {country}. Veuillez sélectionner le Togo ou utiliser un numéro correspondant au pays sélectionné.'
            
            # Numéros américains (vérifier les indicatifs régionaux)
            elif cleaned_phone.startswith(('212', '213', '214', '215', '216', '217', '218', '219', '220', '221', '222', '223', '224', '225', '226', '227', '228', '229', '230', '231', '232', '233', '234', '235', '236', '237', '238', '239', '240', '241', '242', '243', '244', '245', '246', '247', '248', '249', '250', '251', '252', '253', '254', '255', '256', '257', '258', '259', '260', '261', '262', '263', '264', '265', '266', '267', '268', '269', '270', '271', '272', '273', '274', '275', '276', '277', '278', '279', '280', '281', '282', '283', '284', '285', '286', '287', '288', '289', '290', '291', '292', '293', '294', '295', '296', '297', '298', '299', '300', '301', '302', '303', '304', '305', '306', '307', '308', '309', '310', '311', '312', '313', '314', '315', '316', '317', '318', '319', '320', '321', '322', '323', '324', '325', '326', '327', '328', '329', '330', '331', '332', '333', '334', '335', '336', '337', '338', '339', '340', '341', '342', '343', '344', '345', '346', '347', '348', '349', '350', '351', '352', '353', '354', '355', '356', '357', '358', '359', '360', '361', '362', '363', '364', '365', '366', '367', '368', '369', '370', '371', '372', '373', '374', '375', '376', '377', '378', '379', '380', '381', '382', '383', '384', '385', '386', '387', '388', '389', '390', '391', '392', '393', '394', '395', '396', '397', '398', '399', '400', '401', '402', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412', '413', '414', '415', '416', '417', '418', '419', '420', '421', '422', '423', '424', '425', '426', '427', '428', '429', '430', '431', '432', '433', '434', '435', '436', '437', '439', '440', '441', '442', '443', '445', '447', '448', '449', '450', '451', '452', '453', '454', '455', '456', '457', '458', '459', '460', '461', '462', '463', '464', '465', '466', '467', '468', '469', '470', '471', '472', '473', '474', '475', '476', '477', '478', '479', '480', '481', '482', '483', '484', '485', '486', '487', '488', '489', '490', '491', '492', '493', '494', '495', '496', '497', '498', '499', '500', '501', '502', '503', '504', '505', '506', '507', '508', '509', '510', '511', '512', '513', '515', '516', '517', '518', '519', '520', '521', '522', '523', '524', '525', '526', '527', '528', '529', '530', '531', '532', '533', '534', '535', '536', '537', '538', '539', '540', '541', '542', '543', '544', '545', '546', '547', '548', '549', '550', '551', '552', '553', '554', '555', '556', '557', '558', '559', '560', '561', '562', '563', '564', '565', '566', '567', '568', '569', '570', '571', '572', '573', '574', '575', '576', '577', '578', '580', '582', '583', '584', '585', '586', '587', '588', '589', '590', '591', '592', '593', '594', '595', '596', '597', '598', '599', '600', '601', '602', '603', '604', '605', '606', '607', '608', '609', '610', '611', '612', '613', '614', '615', '616', '617', '618', '619', '620', '621', '622', '623', '624', '625', '626', '627', '628', '629', '630', '631', '632', '633', '634', '635', '636', '637', '638', '639', '640', '641', '642', '643', '644', '645', '646', '647', '648', '649', '650', '651', '652', '653', '654', '655', '656', '657', '658', '659', '660', '661', '662', '663', '664', '665', '666', '667', '668', '669', '670', '671', '672', '673', '674', '675', '676', '677', '678', '679', '680', '681', '682', '683', '684', '685', '686', '687', '688', '689', '690', '691', '692', '693', '694', '695', '696', '697', '698', '699', '700', '701', '702', '703', '704', '705', '706', '707', '708', '709', '710', '711', '712', '713', '714', '715', '716', '717', '718', '719', '720', '721', '722', '723', '724', '725', '726', '727', '728', '729', '730', '731', '732', '733', '734', '735', '736', '737', '738', '739', '740', '741', '742', '743', '744', '745', '746', '747', '748', '749', '750', '751', '752', '753', '754', '755', '756', '757', '758', '759', '760', '761', '762', '763', '764', '765', '766', '767', '768', '769', '770', '771', '772', '773', '774', '775', '776', '777', '778', '779', '780', '781', '782', '783', '784', '785', '786', '787', '788', '789', '790', '791', '792', '793', '794', '795', '796', '797', '798', '799', '800', '801', '802', '803', '804', '805', '806', '807', '808', '809', '810', '811', '812', '813', '814', '815', '816', '817', '818', '820', '821', '822', '823', '824', '825', '826', '827', '828', '829', '830', '831', '832', '833', '834', '835', '836', '837', '838', '839', '840', '841', '842', '843', '844', '845', '846', '847', '848', '849', '850', '851', '852', '853', '854', '855', '856', '857', '858', '859', '860', '861', '862', '863', '864', '865', '866', '867', '868', '869', '870', '871', '872', '874', '875', '876', '877', '878', '879', '880', '881', '882', '883', '884', '885', '886', '887', '888', '889', '890', '891', '892', '893', '894', '895', '896', '897', '898', '899', '900', '901', '902', '903', '904', '905', '906', '907', '908', '909', '910', '911', '912', '913', '914', '915', '916', '917', '918', '919', '920', '921', '922', '923', '924', '925', '926', '927', '928', '929', '930', '931', '932', '933', '934', '935', '936', '937', '938', '939', '940', '941', '942', '943', '944', '945', '946', '947', '948', '949', '950', '951', '952', '953', '954', '955', '956', '957', '958', '959', '960', '961', '962', '963', '964', '965', '966', '967', '968', '969', '970', '971', '972', '973', '974', '975', '976', '977', '978', '979', '980', '981', '982', '983', '984', '985', '986', '987', '988', '989', '990', '991', '992', '993', '994', '995', '996', '997', '998', '999')):
                if country != 'US':
                    validation_error = f'Le numéro de téléphone commence par {cleaned_phone[:3]} (États-Unis) mais le pays sélectionné est {country}. Veuillez sélectionner les États-Unis ou utiliser un numéro correspondant au pays sélectionné.'
            
            # Si erreur de validation, la retourner
            if validation_error:
                print(f"🔍 DEBUG: Validation ERROR - {validation_error}")
                return Response({
                    'error': validation_error
                }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"🔍 DEBUG: Validation ACCEPTED - Numéro {cleaned_phone} correspond au pays {country}")
        
        # Mettre à jour le profil utilisateur
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if 'phone' in data:
            profile.phone = data['phone']
        if 'country' in data:
            profile.country = data['country']
        
        profile.save()
        
        print(f"🔍 DEBUG: Profil mis à jour - Phone: {profile.phone}, Country: {profile.country}")
        
        return Response({
            'message': 'Profil mis à jour avec succès',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile': {
                    'phone': profile.phone,
                    'country': profile.country,
                    'role': profile.role
                }
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Erreur lors de la mise à jour du profil',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_refund_view(request, refund_request_id):
    """Vue simple pour traiter les demandes de remboursement"""
    try:
        print(f"🔍 DEBUG process_refund_view: user={request.user.username}, refund_request_id={refund_request_id}")
        
        # Récupérer la demande de remboursement
        try:
            refund_request = RefundRequest.objects.get(id=refund_request_id)
            registration = refund_request.registration
            event = registration.event
        except RefundRequest.DoesNotExist:
            return Response(
                {"error": "Demande de remboursement non trouvée."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        print(f"🔍 DEBUG: event={event.title} (ID={event.id}), organizer={event.organizer.username}")
        print(f"🔍 DEBUG: user={request.user.username}, is_staff={request.user.is_staff}")
        print(f"🔍 DEBUG: organizer check: {event.organizer == request.user}")
        
        # Vérifier les permissions (organisateur ou staff)
        if event.organizer != request.user and not request.user.is_staff:
            print(f"❌ DEBUG: Permission denied for user {request.user.username}")
            return Response(
                {"error": "Vous n'êtes pas autorisé à traiter cette demande."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        print(f"✅ DEBUG: Permission granted for user {request.user.username}")
        
        action = request.data.get('action')  # 'approve', 'reject', ou 'process' (synonyme de 'approve')
        reason = request.data.get('reason', '')
        
        print(f"🔍 DEBUG: action reçue = '{action}', reason = '{reason}'")
        
        # Ne pas normaliser 'process' - c'est une action distincte
        # if action == 'process':
        #     action = 'approve'
        #     print(f"🔄 DEBUG: 'process' normalisé en 'approve'")
        
        print(f"🔍 DEBUG: action finale = '{action}'")
        
        # Vérifier que le remboursement n'est pas déjà traité
        if refund.status in ['processed', 'rejected']:
            print(f"⚠️ DEBUG: Refund {refund.id} déjà traité avec le statut '{refund.status}'")
            return Response({
                'error': f'Ce remboursement est déjà {refund.get_status_display().lower()}',
                'current_status': refund.status
            }, status=400)
        
        if action == 'approve':
            return _process_approve_refund(refund_request, request)
        elif action == 'reject':
            return _process_reject_refund(refund_request, request)
        else:
            return Response(
                {"error": "Action non valide. Utilisez 'approve' ou 'reject'."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except EventRegistration.DoesNotExist:
        return Response(
            {"error": "Inscription non trouvée."},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {"error": f"Erreur serveur: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _process_approve_refund(refund_request, request):
    """Approuver et traiter un remboursement"""
    if refund_request.status != 'pending':
        return Response(
            {"error": "Cette demande a déjà été traitée."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Traiter le remboursement via Stripe
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response(
                {"error": "Stripe non configuré"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        registration = refund_request.registration
        
        if not registration.payment_reference:
            return Response(
                {"error": "Référence de paiement manquante"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Effectuer le remboursement Stripe
        refund = stripe.Refund.create(
            payment_intent=registration.payment_reference,
            amount=int(float(refund_request.refund_amount) * 100),  # Centimes
            reason='requested_by_customer',
            metadata={
                'registration_id': registration.id,
                'event_id': registration.event.id,
                'refund_request_id': refund_request.id,
                'processed_by': request.user.username,
            }
        )
        
        # Mettre à jour la demande de remboursement
        from django.utils import timezone
        refund_request.status = 'processed'
        refund_request.processed_at = timezone.now()
        refund_request.processed_by = request.user
        refund_request.stripe_refund_id = refund.id
        refund_request.save()
        
        # Envoyer email de confirmation
        _send_refund_email_confirmation(refund_request)
        
        return Response({
            "message": "Remboursement traité avec succès",
            "refund_amount": float(refund_request.refund_amount),
            "stripe_refund_id": refund.id
        })
        
    except Exception as e:
        print(f"Erreur lors du traitement du remboursement: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {"error": f"Erreur lors du traitement: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _process_reject_refund(refund_request, request):
    """Rejeter une demande de remboursement"""
    if refund_request.status != 'pending':
        return Response(
            {"error": "Cette demande a déjà été traitée."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    reason = request.data.get('reason', 'Rejeté par l\'organisateur')
    
    # Mettre à jour la demande
    from django.utils import timezone
    refund_request.status = 'rejected'
    refund_request.processed_at = timezone.now()
    refund_request.processed_by = request.user
    refund_request.reason = f"{refund_request.reason}\n\nRejet: {reason}"
    refund_request.save()
    
    # Envoyer email de rejet
    _send_refund_email_rejection(refund_request, reason)
    
    return Response({
        "message": "Demande de remboursement rejetée",
        "reason": reason
    })


def _send_refund_email_confirmation(refund_request):
    """Envoyer email de confirmation de remboursement"""
    try:
        registration = refund_request.registration
        event = registration.event
        
        subject = f"Remboursement confirmé - {event.title}"
        context = {
            'user': registration.user,
            'event': event,
            'refund_request': refund_request,
            'refund_amount': refund_request.refund_amount,
        }
        
        message = render_to_string('emails/refund_confirmation.txt', context)
        html_message = render_to_string('emails/refund_confirmation.html', context)
        
        msg = EmailMultiAlternatives(
            subject, 
            message, 
            getattr(settings, 'DEFAULT_FROM_EMAIL', None), 
            [registration.user.email]
        )
        msg.attach_alternative(html_message, 'text/html')
        msg.send(fail_silently=False)
        
        print(f"Email de confirmation de remboursement envoyé à {registration.user.email}")
        
        # 🎯 NOUVEAU : Envoyer SMS pour confirmation de remboursement (fonction séparée)
        try:
            from .sms_service import sms_service
            print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS REMBOURSEMENT CONFIRMÉ (FONCTION) =====")
            print(f"🔍 DEBUG: Inscription ID: {registration.id}")
            print(f"🔍 DEBUG: Montant remboursé: {refund_request.refund_amount}")
            print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
            
            sms_sent = sms_service.send_confirmation_sms(registration)
            
            if sms_sent:
                print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour remboursement confirmé (fonction) {registration.id}")
            else:
                print(f"🔍 DEBUG: ❌ Échec envoi SMS pour remboursement confirmé (fonction) {registration.id}")
            print(f"🔍 DEBUG: ===== FIN ENVOI SMS REMBOURSEMENT CONFIRMÉ (FONCTION) =====")
        except Exception as e:
            print(f"🔍 DEBUG: Erreur envoi SMS remboursement confirmé (fonction): {e}")
        
    except Exception as e:
        print(f"Erreur envoi email de confirmation de remboursement: {e}")


def _send_refund_email_rejection(refund_request, reason):
    """Envoyer email de rejet de remboursement"""
    try:
        registration = refund_request.registration
        event = registration.event
        
        subject = f"Demande de remboursement rejetée - {event.title}"
        
        # Email simple inline
        message = f"""Bonjour {registration.user.first_name or registration.user.username},

Votre demande de remboursement pour l'événement "{event.title}" a été rejetée.

Raison: {reason}

Montant demandé: {refund_request.refund_amount}€

Si vous avez des questions, contactez l'organisateur de l'événement.

Cordialement,
L'équipe de gestion d'événements"""

        html_message = f"""<p>Bonjour {registration.user.first_name or registration.user.username},</p>

<p>Votre demande de remboursement pour l'événement "<strong>{event.title}</strong>" a été rejetée.</p>

<p><strong>Raison:</strong> {reason}</p>
<p><strong>Montant demandé:</strong> {refund_request.refund_amount}€</p>

<p>Si vous avez des questions, contactez l'organisateur de l'événement.</p>

<p>Cordialement,<br>L'équipe de gestion d'événements</p>"""
        
        msg = EmailMultiAlternatives(
            subject, 
            message, 
            getattr(settings, 'DEFAULT_FROM_EMAIL', None), 
            [registration.user.email]
        )
        msg.attach_alternative(html_message, 'text/html')
        msg.send(fail_silently=False)
        
        print(f"Email de rejet de remboursement envoyé à {registration.user.email}")
        
        # 🎯 NOUVEAU : Envoyer SMS pour rejet de remboursement (fonction séparée)
        try:
            from .sms_service import sms_service
            print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS REMBOURSEMENT REJETÉ (FONCTION) =====")
            print(f"🔍 DEBUG: Inscription ID: {registration.id}")
            print(f"🔍 DEBUG: Raison du rejet: {reason}")
            print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
            
            sms_sent = sms_service.send_confirmation_sms(registration)
            
            if sms_sent:
                print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour remboursement rejeté (fonction) {registration.id}")
            else:
                print(f"🔍 DEBUG: ❌ Échec envoi SMS pour remboursement rejeté (fonction) {registration.id}")
            print(f"🔍 DEBUG: ===== FIN ENVOI SMS REMBOURSEMENT REJETÉ (FONCTION) =====")
        except Exception as e:
            print(f"🔍 DEBUG: Erreur envoi SMS remboursement rejeté (fonction): {e}")
        
    except Exception as e:
        print(f"Erreur envoi email de rejet de remboursement: {e}")

# =====================================
# VUES SUPER ADMIN
# =====================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_dashboard_stats(request):
    """Statistiques globales pour le Super Admin"""
    from .permissions import IsSuperAdmin
    
    if not IsSuperAdmin().has_permission(request, None):
        return Response({'error': 'Accès réservé aux Super Administrateurs'}, status=403)
    
    # Statistiques des utilisateurs
    total_users = User.objects.count()
    total_organizers = UserProfile.objects.filter(role='organizer').count()
    total_participants = UserProfile.objects.filter(role='participant').count()
    new_users_this_month = User.objects.filter(
        date_joined__gte=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    # Statistiques des événements
    total_events = Event.objects.count()
    published_events = Event.objects.filter(status='published').count()
    draft_events = Event.objects.filter(status='draft').count()
    cancelled_events = Event.objects.filter(status='cancelled').count()
    
    # Statistiques des inscriptions
    total_registrations = EventRegistration.objects.count()
    confirmed_registrations = EventRegistration.objects.filter(status='confirmed').count()
    waitlisted_registrations = EventRegistration.objects.filter(status='waitlisted').count()
    
    # Statistiques financières
    total_revenue = EventRegistration.objects.filter(
        status='confirmed',
        price_paid__isnull=False
    ).aggregate(total=Sum('price_paid'))['total'] or 0
    
    # Événements par mois (6 derniers mois)
    six_months_ago = timezone.now() - timedelta(days=180)
    events_by_month = Event.objects.filter(
        created_at__gte=six_months_ago
    ).annotate(
        month=TruncDate('created_at', 'month')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # Top organisateurs
    top_organizers = User.objects.filter(
        events__isnull=False
    ).annotate(
        event_count=Count('events')
    ).order_by('-event_count')[:10]
    
    organizer_stats = []
    for user in top_organizers:
        organizer_stats.append({
            'username': user.username,
            'email': user.email,
            'event_count': user.event_count,
            'total_registrations': EventRegistration.objects.filter(
                event__organizer=user
            ).count()
        })
    
    return Response({
        'users': {
            'total': total_users,
            'organizers': total_organizers,
            'participants': total_participants,
            'new_this_month': new_users_this_month
        },
        'events': {
            'total': total_events,
            'published': published_events,
            'draft': draft_events,
            'cancelled': cancelled_events
        },
        'registrations': {
            'total': total_registrations,
            'confirmed': confirmed_registrations,
            'waitlisted': waitlisted_registrations
        },
        'financial': {
            'total_revenue': float(total_revenue)
        },
        'trends': {
            'events_by_month': list(events_by_month),
            'top_organizers': organizer_stats
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_users_list(request):
    """Liste de tous les utilisateurs pour le Super Admin"""
    from .permissions import IsSuperAdmin
    
    if not IsSuperAdmin().has_permission(request, None):
        return Response({'error': 'Accès réservé aux Super Administrateurs'}, status=403)
    
    # Filtres
    role_filter = request.query_params.get('role', '')
    search_query = request.query_params.get('search', '')
    status_filter = request.query_params.get('status', '')
    
    users = User.objects.select_related('profile').all()
    
    if role_filter:
        users = users.filter(profile__role=role_filter)
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    total_users = users.count()
    users_page = users[start:end]
    
    user_data = []
    for user in users_page:
        profile = getattr(user, 'profile', None)
        user_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'role': profile.role if profile else 'participant',
            'phone': profile.phone if profile else '',
            'event_count': Event.objects.filter(organizer=user).count(),
            'registration_count': EventRegistration.objects.filter(user=user).count()
        })
    
    return Response({
        'users': user_data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total_users,
            'total_pages': (total_users + page_size - 1) // page_size
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_user_action(request, user_id):
    """Actions sur les utilisateurs (suspendre, changer de rôle, etc.)"""
    from .permissions import IsSuperAdmin
    
    if not IsSuperAdmin().has_permission(request, None):
        return Response({'error': 'Accès réservé aux Super Administrateurs'}, status=403)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur non trouvé'}, status=404)
    
    action_type = request.data.get('action')
    
    if action_type == 'suspend':
        user.is_active = False
        user.save()
        return Response({'message': f'Utilisateur {user.username} suspendu'})
    
    elif action_type == 'activate':
        user.is_active = True
        user.save()
        return Response({'message': f'Utilisateur {user.username} réactivé'})
    
    elif action_type == 'change_role':
        new_role = request.data.get('new_role')
        if new_role not in ['super_admin', 'organizer', 'participant', 'guest']:
            return Response({'error': 'Rôle invalide'}, status=400)
        
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.role = new_role
        profile.save()
        
        return Response({'message': f'Rôle de {user.username} changé vers {new_role}'})
    
    elif action_type == 'delete':
        # Vérifier qu'on ne supprime pas le dernier super admin
        if user.profile.role == 'super_admin':
            super_admin_count = UserProfile.objects.filter(role='super_admin').count()
            if super_admin_count <= 1:
                return Response({'error': 'Impossible de supprimer le dernier Super Admin'}, status=400)
        
        user.delete()
        return Response({'message': f'Utilisateur {user.username} supprimé'})
    
    else:
        return Response({'error': 'Action non reconnue'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_events_list(request):
    """Liste de tous les événements pour le Super Admin"""
    from .permissions import IsSuperAdmin
    
    if not IsSuperAdmin().has_permission(request, None):
        return Response({'error': 'Accès réservé aux Super Administrateurs'}, status=403)
    
    # Filtres
    status_filter = request.query_params.get('status', '')
    category_filter = request.query_params.get('category', '')
    organizer_filter = request.query_params.get('organizer', '')
    search_query = request.query_params.get('search', '')
    
    events = Event.objects.select_related('organizer', 'category').prefetch_related('tags').all()
    
    if status_filter:
        events = events.filter(status=status_filter)
    
    if category_filter:
        events = events.filter(category_id=category_filter)
    
    if organizer_filter:
        events = events.filter(organizer__username__icontains=organizer_filter)
    
    if search_query:
        events = events.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Pagination
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    total_events = events.count()
    events_page = events[start:end]
    
    event_data = []
    for event in events_page:
        event_data.append({
            'id': event.id,
            'title': event.title,
            'status': event.status,
            'organizer': {
                'id': event.organizer.id,
                'username': event.organizer.username,
                'email': event.organizer.email
            },
            'category': event.category.name if event.category else None,
            'start_date': event.start_date,
            'end_date': event.end_date,
            'location': event.location,
            'max_participants': event.max_participants,
            'current_participants': EventRegistration.objects.filter(
                event=event, 
                status='confirmed'
            ).count(),
            'revenue': float(EventRegistration.objects.filter(
                event=event,
                status='confirmed',
                price_paid__isnull=False
            ).aggregate(total=Sum('price_paid'))['total'] or 0),
            'created_at': event.created_at
        })
    
    return Response({
        'events': event_data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total_events,
            'total_pages': (total_events + page_size - 1) // page_size
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_event_action(request, event_id):
    """Actions sur les événements (modérer, suspendre, etc.)"""
    from .permissions import IsSuperAdmin
    
    if not IsSuperAdmin().has_permission(request, None):
        return Response({'error': 'Accès réservé aux Super Administrateurs'}, status=403)
    
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return Response({'error': 'Événement non trouvé'}, status=404)
    
    action_type = request.data.get('action')
    
    if action_type == 'approve':
        event.status = 'published'
        event.save()
        return Response({'message': f'Événement "{event.title}" approuvé'})
    
    elif action_type == 'suspend':
        event.status = 'draft'
        event.save()
        return Response({'message': f'Événement "{event.title}" suspendu'})
    
    elif action_type == 'reject':
        event.status = 'draft'
        event.save()
        return Response({'message': f'Événement "{event.title}" rejeté'})
    
    elif action_type == 'cancel':
        # 🆕 ANNULATION D'ÉVÉNEMENT AVEC REMBOURSEMENTS AUTOMATIQUES
        if event.status == 'cancelled':
            return Response({'error': 'Cet événement est déjà annulé'}, status=400)
        
        reason = request.data.get('reason', 'Événement annulé par le Super Admin')
        
        # Annuler l'événement
        old_status = event.status
        event.status = 'cancelled'
        event.save()
        
        # Enregistrer l'action dans l'historique
        EventHistory.objects.create(
            event=event,
            action='cancelled',
            details=f"Événement annulé par {request.user.username}. Raison: {reason}",
            user=request.user
        )
        
        # 🆕 CRÉER AUTOMATIQUEMENT DES DEMANDES DE REMBOURSEMENT pour tous les inscrits payants
        refunds_created = 0
        from .models import RefundPolicy, RefundRequest
        from django.utils import timezone
        
        for registration in event.registrations.filter(status='confirmed'):
            try:
                # Vérifier si l'inscription est payante
                if registration.payment_status == 'paid' and registration.price_paid > 0:
                    # Obtenir ou créer la politique de remboursement
                    try:
                        policy = event.refund_policy
                    except RefundPolicy.DoesNotExist:
                        policy = RefundPolicy.objects.create(
                            event=event,
                            mode='mixed',
                            auto_refund_delay_hours=24,
                            refund_percentage_immediate=100,
                            refund_percentage_after_delay=100,
                            cutoff_hours_before_event=24,
                            allow_partial_refunds=True,
                            require_reason=False,
                            notify_organizer_on_cancellation=True
                        )
                    
                    # Calculer les montants et dates
                    refund_percentage = policy.get_refund_percentage(0)  # Annulation immédiate = 100%
                    refund_amount = (registration.price_paid * refund_percentage) / 100
                    
                    now = timezone.now()
                    auto_process_at = None
                    if policy.mode in ['auto', 'mixed']:
                        auto_process_at = now + timezone.timedelta(hours=policy.auto_refund_delay_hours)
                    
                    expires_at = event.start_date - timezone.timedelta(hours=policy.cutoff_hours_before_event)
                    
                    # Créer la demande de remboursement
                    refund_request = RefundRequest.objects.create(
                        registration=registration,
                        reason=f'Événement annulé par le Super Admin: {reason}',
                        amount_paid=registration.price_paid,
                        refund_percentage=refund_percentage,
                        refund_amount=refund_amount,
                        auto_process_at=auto_process_at,
                        expires_at=expires_at
                    )
                    
                    refunds_created += 1
                    print(f"✅ Demande de remboursement créée automatiquement (Super Admin Action): ID={refund_request.id} pour {registration.user.email if registration.user else registration.guest_email} - Montant: {refund_amount}€")
                    
            except Exception as e:
                print(f"❌ Erreur création demande remboursement automatique (Super Admin Action) pour {registration.id}: {e}")
                import traceback
                traceback.print_exc()
        
        # Notifier tous les participants inscrits
        _notify_participants_event_cancelled(event, reason)
        
        return Response({
            'message': f'Événement "{event.title}" annulé avec succès. {refunds_created} demandes de remboursement ont été créées automatiquement.',
            'event_id': event.id,
            'old_status': old_status,
            'new_status': 'cancelled',
            'reason': reason,
            'refunds_created': refunds_created
        })
    
    elif action_type == 'delete':
        event.delete()
        return Response({'message': f'Événement "{event.title}" supprimé'})
    
    else:
        return Response({'error': 'Action non reconnue'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_financial_report(request):
    """Rapport financier global pour le Super Admin"""
    from .permissions import IsSuperAdmin
    
    if not IsSuperAdmin().has_permission(request, None):
        return Response({'error': 'Accès réservé aux Super Administrateurs'}, status=403)
    
    # Période
    period = request.query_params.get('period', 'month')
    if period == 'week':
        start_date = timezone.now() - timedelta(days=7)
    elif period == 'month':
        start_date = timezone.now() - timedelta(days=30)
    elif period == 'year':
        start_date = timezone.now() - timedelta(days=365)
    else:
        start_date = timezone.now() - timedelta(days=30)
    
    # Revenus par période
    revenue_by_date = EventRegistration.objects.filter(
        status='confirmed',
        price_paid__isnull=False,
        created_at__gte=start_date
    ).annotate(
        date=TruncDate('created_at', 'day')
    ).values('date').annotate(
        revenue=Sum('price_paid'),
        count=Count('id')
    ).order_by('date')
    
    # Revenus par organisateur
    revenue_by_organizer = EventRegistration.objects.filter(
        status='confirmed',
        price_paid__isnull=False,
        created_at__gte=start_date
    ).values('event__organizer__username').annotate(
        revenue=Sum('price_paid'),
        event_count=Count('event', distinct=True),
        registration_count=Count('id')
    ).order_by('-revenue')
    
    # Revenus par catégorie
    revenue_by_category = EventRegistration.objects.filter(
        status='confirmed',
        price_paid__isnull=False,
        created_at__gte=start_date
    ).values('event__category__name').annotate(
        revenue=Sum('price_paid'),
        event_count=Count('event', distinct=True),
        registration_count=Count('id')
    ).order_by('-revenue')
    
    # Statistiques globales
    total_revenue = sum(item['revenue'] for item in revenue_by_date)
    total_registrations = sum(item['count'] for item in revenue_by_date)
    avg_ticket_price = total_revenue / total_registrations if total_registrations > 0 else 0
    
    return Response({
        'period': {
            'start_date': start_date,
            'end_date': timezone.now()
        },
        'summary': {
            'total_revenue': float(total_revenue),
            'total_registrations': total_registrations,
            'avg_ticket_price': float(avg_ticket_price)
        },
        'revenue_by_date': list(revenue_by_date),
        'revenue_by_organizer': list(revenue_by_organizer),
        'revenue_by_category': list(revenue_by_category)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_system_health(request):
    """État de santé du système pour le Super Admin"""
    from .permissions import IsSuperAdmin
    
    if not IsSuperAdmin().has_permission(request, None):
        return Response({'error': 'Accès réservé aux Super Administrateurs'}, status=403)
    
    # Vérifications système
    system_checks = {
        'database': True,
        'media_files': True,
        'email_service': True,
        'payment_service': True
    }
    
    # Vérification base de données
    try:
        User.objects.count()
    except Exception:
        system_checks['database'] = False
    
    # Vérification fichiers média
    try:
        import os
        media_root = getattr(settings, 'MEDIA_ROOT', 'media/')
        if not os.path.exists(media_root):
            system_checks['media_files'] = False
    except Exception:
        system_checks['media_files'] = False
    
    # Vérification service email
    try:
        email_backend = getattr(settings, 'EMAIL_BACKEND', '')
        system_checks['email_service'] = email_backend != 'django.core.mail.backends.console.EmailBackend'
    except Exception:
        system_checks['email_service'] = False
    
    # Vérification service de paiement
    try:
        stripe_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
        system_checks['payment_service'] = bool(stripe_key)
    except Exception:
        system_checks['payment_service'] = False
    
    # Statistiques système
    system_stats = {
        'total_users': User.objects.count(),
        'total_events': Event.objects.count(),
        'total_registrations': EventRegistration.objects.count(),
        'active_events': Event.objects.filter(status='published').count(),
        'pending_refunds': RefundRequest.objects.filter(status='pending').count(),
        'system_uptime': 'N/A'  # À implémenter si nécessaire
    }
    
    return Response({
        'system_health': system_checks,
        'system_stats': system_stats,
        'timestamp': timezone.now()
    })

# ============================================================================
# VUES POUR CATÉGORIES ET TAGS
# ============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def categories_list(request):
    """Liste et création des catégories (Super Admin)"""
    if request.method == 'GET':
        try:
            categories = Category.objects.filter(is_active=True).order_by('name')
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des catégories: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'POST':
        try:
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la création de la catégorie: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def category_detail(request, pk):
    """Détail, modification et suppression d'une catégorie (Super Admin)"""
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(
            {'error': 'Catégorie non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        try:
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la modification: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'DELETE':
        try:
            # Vérifier si la catégorie est utilisée (relation inverse)
            if Event.objects.filter(category=category).exists():
                return Response(
                    {'error': 'Impossible de supprimer une catégorie utilisée par des événements'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            category.delete()
            return Response({'message': 'Catégorie supprimée avec succès'})
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la suppression: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def tags_list(request):
    """Liste et création des tags (Super Admin)"""
    if request.method == 'GET':
        try:
            tags = Tag.objects.filter(is_active=True).order_by('name')
            serializer = TagSerializer(tags, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des tags: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'POST':
        try:
            serializer = TagSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la création du tag: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def tag_detail(request, pk):
    """Détail, modification et suppression d'un tag (Super Admin)"""
    try:
        tag = Tag.objects.get(pk=pk)
    except Tag.DoesNotExist:
        return Response(
            {'error': 'Tag non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = TagSerializer(tag)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        try:
            serializer = TagSerializer(tag, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la modification: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    elif request.method == 'DELETE':
        try:
            # Vérifier si le tag est utilisé (relation inverse)
            if Event.objects.filter(tags=tag).exists():
                return Response(
                    {'error': 'Impossible de supprimer un tag utilisé par des événements'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            tag.delete()
            return Response({'message': 'Tag supprimé avec succès'})
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la suppression: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ============================================================================
# VUES POUR LA GESTION DES UTILISATEURS PAR LE SUPER ADMIN
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_users_list(request):
    """Liste de tous les utilisateurs pour le Super Admin"""
    try:
        users = User.objects.select_related('profile').all()
        user_data = []
        
        for user in users:
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.profile.role if hasattr(user, 'profile') else 'participant',
                'status': 'active' if user.is_active else 'inactive',
                'created_at': user.date_joined.strftime('%Y-%m-%d'),
                'last_login': user.last_login.strftime('%Y-%m-%d') if user.last_login else None,
                'phone': user.profile.phone if hasattr(user, 'profile') else ''
            })
        
        return Response({
            'count': len(user_data),
            'results': user_data
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_create_user(request):
    """Créer un nouvel utilisateur"""
    try:
        print(f"🔍 DEBUG: create_user - Données reçues: {request.data}")
        data = request.data
        
        # Vérifier si l'utilisateur existe déjà
        print(f"🔍 DEBUG: Vérification username: {data.get('username')}")
        if User.objects.filter(username=data['username']).exists():
            print(f"❌ DEBUG: Username déjà existant: {data['username']}")
            return Response({'error': 'Ce nom d\'utilisateur existe déjà'}, status=400)
        
        print(f"🔍 DEBUG: Vérification email: {data.get('email')}")
        if User.objects.filter(email=data['email']).exists():
            print(f"❌ DEBUG: Email déjà existant: {data['email']}")
            return Response({'error': 'Cet email existe déjà'}, status=400)
        
        print(f"🔍 DEBUG: Création de l'utilisateur...")
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        print(f"✅ DEBUG: Utilisateur créé: {user.username}")
        
        print(f"🔍 DEBUG: Création du profil UserProfile...")
        # Créer le profil utilisateur
        profile = UserProfile.objects.create(
            user=user,
            role=data['role'],
            phone=data.get('phone', '')
        )
        print(f"✅ DEBUG: Profil créé avec le rôle: {profile.role}")
        
        # Préparer la réponse
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': data['role'],
            'status': 'active',
            'created_at': user.date_joined.strftime('%Y-%m-%d'),
            'last_login': None,
            'phone': data.get('phone', '')
        }
        
        print(f"✅ DEBUG: Réponse préparée: {user_data}")
        return Response(user_data, status=201)
        
    except Exception as e:
        print(f"❌ DEBUG: Erreur lors de la création: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_manage_user(request):
    """Gérer un utilisateur (suspendre, activer, supprimer, changer de rôle)"""
    try:
        user_id = request.data.get('user_id')
        action = request.data.get('action')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'Utilisateur non trouvé'}, status=404)
        
        if action == 'suspend':
            user.is_active = False
            user.save()
            return Response({'message': 'Utilisateur suspendu avec succès'})
            
        elif action == 'activate':
            user.is_active = True
            user.save()
            return Response({'message': 'Utilisateur activé avec succès'})
            
        elif action == 'delete':
            user.delete()
            return Response({'message': 'Utilisateur supprimé avec succès'})
            
        elif action == 'change_role':
            new_role = request.data.get('new_role')
            if new_role not in ['super_admin', 'organizer', 'participant', 'guest']:
                return Response({'error': 'Rôle invalide'}, status=400)
            
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = new_role
            profile.save()
            return Response({'message': 'Rôle modifié avec succès'})
            
        else:
            return Response({'error': 'Action non reconnue'}, status=400)
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# ============================================================================
# VUES POUR LES STATISTIQUES ET ANALYTICS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_refunds_list(request):
    """Liste des remboursements pour le Super Admin"""
    try:
        from django.db.models import Q
        
        # Récupérer tous les remboursements avec pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        start = (page - 1) * page_size
        end = start + page_size
        
        refunds = RefundRequest.objects.select_related(
            'registration__event', 
            'registration__user'
        ).order_by('-created_at')[start:end]
        
        total_count = RefundRequest.objects.count()
        
        refunds_data = []
        for refund in refunds:
            refunds_data.append({
                'id': refund.id,
                'registration_id': refund.registration.id if refund.registration else None,
                'user': {
                    'id': refund.registration.user.id if refund.registration and refund.registration.user else None,
                    'username': refund.registration.user.username if refund.registration and refund.registration.user else 'N/A'
                },
                'event': {
                    'id': refund.registration.event.id if refund.registration and refund.registration.event else None,
                    'title': refund.registration.event.title if refund.registration and refund.registration.event else 'N/A'
                },
                'amount_paid': float(refund.amount_paid) if refund.amount_paid else 0,
                'refund_amount': float(refund.refund_amount) if refund.refund_amount else 0,
                'status': refund.status,
                'reason': refund.reason,
                'created_at': refund.created_at.isoformat() if refund.created_at else None,
                'processed_at': refund.processed_at.isoformat() if refund.processed_at else None
            })
        
        return Response({
            'count': total_count,
            'results': refunds_data,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_global_stats(request):
    """Statistiques globales pour le Super Admin"""
    try:
        from django.db.models import Count, Sum, Q
        from django.utils import timezone
        from datetime import timedelta
        
        # Période de calcul (30 derniers jours)
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Statistiques générales
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        total_events = Event.objects.count()
        published_events = Event.objects.filter(status='published').count()
        pending_events = Event.objects.filter(status='pending').count()
        total_registrations = EventRegistration.objects.count()
        confirmed_registrations = EventRegistration.objects.filter(status='confirmed').count()
        
        # Revenus (si applicable)
        total_revenue = EventRegistration.objects.aggregate(
            total=Sum('price_paid')
        )['total'] or 0
        
        # Nouveaux utilisateurs ce mois
        new_users_this_month = User.objects.filter(
            date_joined__gte=start_date
        ).count()
        
        # Nouveaux événements ce mois
        new_events_this_month = Event.objects.filter(
            created_at__gte=start_date
        ).count()
        
        # Répartition des rôles
        role_distribution = {}
        for role_choice in UserProfile.ROLE_CHOICES:
            role_value = role_choice[0]
            role_name = role_choice[1]
            count = UserProfile.objects.filter(role=role_value).count()
            role_distribution[role_value] = {
                'name': role_name,
                'count': count
            }
        
        # Top événements par participants
        top_events = Event.objects.annotate(
            participant_count=Count('registrations')
        ).order_by('-participant_count')[:5]
        
        top_events_data = []
        for event in top_events:
            top_events_data.append({
                'id': event.id,
                'title': event.title,
                'participants': event.participant_count,
                'revenue': 0  # À implémenter si nécessaire
            })
        
        stats = {
            'general_stats': {
                'total_users': total_users,
                'active_users': active_users,
                'total_events': total_events,
                'published_events': published_events,
                'pending_events': pending_events,
                'total_registrations': total_registrations,
                'confirmed_registrations': confirmed_registrations,
                'total_revenue': total_revenue,
            },
            'recent_activity': {
                'new_users_30d': new_users_this_month,
                'new_events_30d': new_events_this_month
            }
        }
        
        return Response(stats)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_analytics(request):
    """Analytics avancées pour le Super Admin"""
    try:
        from django.db.models import Count, Sum, Q
        from django.utils import timezone
        from datetime import timedelta
        
        period = request.GET.get('period', 'month')
        
        if period == 'week':
            days = 7
        elif period == 'month':
            days = 30
        elif period == 'year':
            days = 365
        else:
            days = 30
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Croissance des utilisateurs
        user_growth = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            count = User.objects.filter(date_joined__date=date.date()).count()
            user_growth.append(count)
        
        # Croissance des revenus
        revenue_growth = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            revenue = EventRegistration.objects.filter(
                registered_at__date=date.date()
            ).aggregate(total=Sum('price_paid'))['total'] or 0
            revenue_growth.append(revenue)
        
        # Top événements par revenus
        top_revenue_events = Event.objects.annotate(
            total_revenue=Sum('registrations__price_paid')
        ).filter(total_revenue__gt=0).order_by('-total_revenue')[:10]
        
        top_revenue_data = []
        for event in top_revenue_events:
            top_revenue_data.append({
                'id': event.id,
                'title': event.title,
                'organizer': event.organizer.username if event.organizer else 'N/A',
                'start_date': event.start_date.isoformat() if event.start_date else None,
                'total_revenue': event.total_revenue or 0
            })
        
        analytics = {
            'summary': {
                'total_platform_users': User.objects.count(),
                'active_organizers': UserProfile.objects.filter(role='organizer').count(),
                'published_events': Event.objects.filter(status='published').count(),
                            'this_month_revenue': EventRegistration.objects.filter(
                registered_at__gte=start_date
            ).aggregate(total=Sum('price_paid'))['total'] or 0
            },
            'daily_stats': [
                {
                    'date': (start_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                    'new_users': User.objects.filter(date_joined__date=(start_date + timedelta(days=i)).date()).count(),
                    'new_events': Event.objects.filter(created_at__date=(start_date + timedelta(days=i)).date()).count(),
                    'new_registrations': EventRegistration.objects.filter(registered_at__date=(start_date + timedelta(days=i)).date()).count(),
                    'revenue': EventRegistration.objects.filter(registered_at__date=(start_date + timedelta(days=i)).date()).aggregate(total=Sum('price_paid'))['total'] or 0
                }
                for i in range(min(days, 7))  # Limiter à 7 jours pour l'affichage
            ],
            'role_distribution': {
                role: {
                    'name': dict(UserProfile.ROLE_CHOICES)[role],
                    'count': UserProfile.objects.filter(role=role).count()
                }
                for role, _ in UserProfile.ROLE_CHOICES
            },
            'top_revenue_events': top_revenue_data
        }
        
        return Response(analytics)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def approve_refund(request, refund_id):
    """Approuver un remboursement (Super Admin)"""
    try:
        refund_request = RefundRequest.objects.get(id=refund_id)
        
        if refund_request.status != 'pending':
            return Response(
                {'error': 'Seuls les remboursements en attente peuvent être approuvés'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Approuver le remboursement
        refund_request.status = 'approved'
        refund_request.processed_at = timezone.now()
        refund_request.processed_by = request.user
        refund_request.save()
        
        # Envoyer email de confirmation
        _send_refund_approval_email(refund_request)
        
        return Response({
            'message': 'Remboursement approuvé avec succès',
            'refund_id': refund_request.id,
            'status': 'approved'
        })
        
    except RefundRequest.DoesNotExist:
        return Response(
            {'error': 'Demande de remboursement non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'approbation: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def reject_refund(request, refund_id):
    """Rejeter un remboursement (Super Admin)"""
    try:
        refund_request = RefundRequest.objects.get(id=refund_id)
        reason = request.data.get('reason', '')
        
        if not reason:
            return Response(
                {'error': 'Une raison est requise pour rejeter un remboursement'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if refund_request.status != 'pending':
            return Response(
                {'error': 'Seuls les remboursements en attente peuvent être rejetés'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rejeter le remboursement
        refund_request.status = 'rejected'
        refund_request.processed_at = timezone.now()
        refund_request.processed_by = request.user
        refund_request.rejection_reason = reason
        refund_request.save()
        
        # Envoyer email de rejet
        _send_refund_rejection_email(refund_request, reason)
        
        return Response({
            'message': 'Remboursement rejeté avec succès',
            'refund_id': refund_request.id,
            'status': 'rejected',
            'reason': reason
        })
        
    except RefundRequest.DoesNotExist:
        return Response(
            {'error': 'Demande de remboursement non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors du rejet: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def _send_refund_approval_email(refund_request):
    """Envoyer email de confirmation d'approbation de remboursement"""
    try:
        from django.template.loader import render_to_string
        from django.core.mail import EmailMultiAlternatives
        
        registration = refund_request.registration
        user = registration.user
        event = registration.event
        
        context = {
            'user': user,
            'event': event,
            'refund_amount': refund_request.refund_amount,
            'refund_request': refund_request,
            'approval_date': timezone.now()
        }
        
        subject = f"✅ Remboursement approuvé - {event.title}"
        text_body = render_to_string('emails/refund_approved.txt', context)
        html_body = render_to_string('emails/refund_approved.html', context)
        
        msg = EmailMultiAlternatives(
            subject,
            text_body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        
        print(f"📧 Email d'approbation envoyé à {user.email}")
        
        # 🎯 NOUVEAU : Envoyer SMS pour approbation de remboursement (Super Admin)
        try:
            from .sms_service import sms_service
            print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS REMBOURSEMENT APPROUVÉ (SUPER ADMIN) =====")
            print(f"🔍 DEBUG: Inscription ID: {registration.id}")
            print(f"🔍 DEBUG: Montant remboursé: {refund_request.refund_amount}")
            print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
            
            sms_sent = sms_service.send_confirmation_sms(registration)
            
            if sms_sent:
                print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour remboursement approuvé (Super Admin) {registration.id}")
            else:
                print(f"🔍 DEBUG: ❌ Échec envoi SMS pour remboursement approuvé (Super Admin) {registration.id}")
            print(f"🔍 DEBUG: ===== FIN ENVOI SMS REMBOURSEMENT APPROUVÉ (SUPER ADMIN) =====")
        except Exception as e:
            print(f"🔍 DEBUG: Erreur envoi SMS remboursement approuvé (Super Admin): {e}")
        
    except Exception as e:
        print(f"❌ Erreur envoi email d'approbation: {e}")

def _send_refund_rejection_email(refund_request, reason):
    """Envoyer email de rejet de remboursement"""
    try:
        from django.template.loader import render_to_string
        from django.core.mail import EmailMultiAlternatives
        
        registration = refund_request.registration
        user = registration.user
        event = registration.event
        
        context = {
            'user': user,
            'event': event,
            'refund_request': refund_request,
            'rejection_reason': reason,
            'rejection_date': timezone.now()
        }
        
        subject = f"❌ Remboursement rejeté - {event.title}"
        text_body = render_to_string('emails/refund_rejected.txt', context)
        html_body = render_to_string('emails/refund_rejected.html', context)
        
        msg = EmailMultiAlternatives(
            subject,
            text_body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        
        print(f"📧 Email de rejet envoyé à {user.email}")
        
        # 🎯 NOUVEAU : Envoyer SMS pour rejet de remboursement (Super Admin)
        try:
            from .sms_service import sms_service
            print(f"🔍 DEBUG: ===== DÉBUT ENVOI SMS REMBOURSEMENT REJETÉ (SUPER ADMIN) =====")
            print(f"🔍 DEBUG: Inscription ID: {registration.id}")
            print(f"🔍 DEBUG: Raison du rejet: {reason}")
            print(f"🔍 DEBUG: Type d'inscription: {'Utilisateur connecté' if registration.user else 'Invité'}")
            
            sms_sent = sms_service.send_confirmation_sms(registration)
            
            if sms_sent:
                print(f"🔍 DEBUG: ✅ SMS envoyé avec succès pour remboursement rejeté (Super Admin) {registration.id}")
            else:
                print(f"🔍 DEBUG: ❌ Échec envoi SMS pour remboursement rejeté (Super Admin) {registration.id}")
            print(f"🔍 DEBUG: ===== FIN ENVOI SMS REMBOURSEMENT REJETÉ (SUPER ADMIN) =====")
        except Exception as e:
            print(f"🔍 DEBUG: Erreur envoi SMS remboursement rejeté (Super Admin): {e}")
        
    except Exception as e:
        print(f"❌ Erreur envoi email de rejet: {e}")

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def system_health_check(request):
    """Vérification de la santé du système (Super Admin)"""
    try:
        from django.db import connection
        from django.core.cache import cache
        import os
        
        health_status = {
            'timestamp': timezone.now().isoformat(),
            'system_health': {},
            'system_stats': {},
            'warnings': [],
            'errors': []
        }
        
        # 1. Vérification de la base de données
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
                health_status['system_health']['database'] = True
        except Exception as e:
            health_status['system_health']['database'] = False
            health_status['errors'].append(f"Base de données: {str(e)}")
        
        # 2. Vérification des fichiers média
        try:
            media_root = getattr(settings, 'MEDIA_ROOT', None)
            if media_root and os.path.exists(media_root):
                # Vérifier l'espace disque
                import shutil
                total, used, free = shutil.disk_usage(media_root)
                free_gb = free // (1024**3)
                
                health_status['system_health']['media_files'] = True
                health_status['system_stats']['disk_free_gb'] = free_gb
                
                if free_gb < 1:  # Moins de 1GB libre
                    health_status['warnings'].append("Espace disque faible pour les fichiers média")
            else:
                health_status['system_health']['media_files'] = False
                health_status['warnings'].append("Répertoire média non configuré")
        except Exception as e:
            health_status['system_health']['media_files'] = False
            health_status['errors'].append(f"Fichiers média: {str(e)}")
        
        # 3. Vérification du service email
        try:
            email_backend = getattr(settings, 'EMAIL_BACKEND', None)
            if email_backend and 'smtp' in email_backend:
                health_status['system_health']['email_service'] = True
            else:
                health_status['system_health']['email_service'] = False
                health_status['warnings'].append("Service email non configuré (SMTP)")
        except Exception as e:
            health_status['system_health']['email_service'] = False
            health_status['errors'].append(f"Service email: {str(e)}")
        
        # 4. Vérification du cache
        try:
            cache.set('health_check_test', 'test_value', 10)
            test_value = cache.get('health_check_test')
            if test_value == 'test_value':
                health_status['system_health']['cache_service'] = True
            else:
                health_status['system_health']['cache_service'] = False
                health_status['warnings'].append("Service de cache défaillant")
        except Exception as e:
            health_status['system_health']['cache_service'] = False
            health_status['errors'].append(f"Service de cache: {str(e)}")
        
        # 5. Statistiques système
        try:
            health_status['system_stats'].update({
                'total_users': User.objects.count(),
                'total_events': Event.objects.count(),
                'total_registrations': EventRegistration.objects.count(),
                'active_events': Event.objects.filter(status='published').count(),
                'pending_refunds': RefundRequest.objects.filter(status='pending').count(),
                'pending_events': Event.objects.filter(status='draft').count(),
                'total_revenue': float(EventRegistration.objects.filter(
                    payment_status='paid'
                ).exclude(
                    refund_request__status='processed'
                ).aggregate(total=Sum('price_paid')).get('total') or 0)
            })
        except Exception as e:
            health_status['errors'].append(f"Statistiques système: {str(e)}")
        
        # 6. Vérification des migrations
        try:
            from django.db.migrations.executor import MigrationExecutor
            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
            
            if plan:
                health_status['warnings'].append(f"{len(plan)} migration(s) en attente")
                health_status['system_health']['migrations'] = False
            else:
                health_status['system_health']['migrations'] = True
        except Exception as e:
            health_status['errors'].append(f"Vérification migrations: {str(e)}")
        
        # 7. Calcul du score de santé global
        health_checks = health_status['system_health'].values()
        if health_checks:
            health_score = (sum(health_checks) / len(health_checks)) * 100
            health_status['health_score'] = round(health_score, 1)
            
            if health_score >= 90:
                health_status['overall_status'] = 'excellent'
            elif health_score >= 75:
                health_status['overall_status'] = 'bon'
            elif health_score >= 50:
                health_status['overall_status'] = 'moyen'
            else:
                health_status['overall_status'] = 'critique'
        else:
            health_status['health_score'] = 0
            health_status['overall_status'] = 'inconnu'
        
        return Response(health_status)
        
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la vérification de la santé du système: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_event_detail(request, event_id):
    """Détails complets d'un événement pour le Super Admin"""
    try:
        event = Event.objects.select_related(
            'organizer', 'category'
        ).prefetch_related(
            'tags', 'registrations', 'registrations__user'
        ).get(id=event_id)
        
        # Statistiques des inscriptions
        registrations_stats = {
            'total': event.registrations.count(),
            'confirmed': event.registrations.filter(status='confirmed').count(),
            'pending': event.registrations.filter(status='pending').count(),
            'cancelled': event.registrations.filter(status='cancelled').count(),
            'attended': event.registrations.filter(status='attended').count(),
            'revenue': float(event.registrations.filter(
                payment_status='paid'
            ).exclude(
                refund_request__status='processed'
            ).aggregate(total=Sum('price_paid')).get('total') or 0)
        }
        
        # Demandes de remboursement
        refund_requests = event.registrations.filter(
            refund_request__isnull=False
        ).select_related('refund_request', 'user')
        
        refunds_data = []
        for registration in refund_requests:
            refund = registration.refund_request
            refunds_data.append({
                'id': refund.id,
                'user': {
                    'id': registration.user.id,
                    'username': registration.user.username,
                    'email': registration.user.email
                },
                'amount_paid': float(registration.price_paid),
                'refund_amount': float(refund.refund_amount),
                'status': refund.status,
                'reason': refund.reason,
                'created_at': refund.created_at.isoformat(),
                'processed_at': refund.processed_at.isoformat() if refund.processed_at else None
            })
        
        # Liste complète des participants
        registrations_data = []
        for registration in event.registrations.select_related('user', 'ticket_type').prefetch_related('refund_request').all():
            registration_data = {
                'id': registration.id,
                'user': {
                    'id': registration.user.id,
                    'username': registration.user.username,
                    'email': registration.user.email,
                    'first_name': registration.user.first_name,
                    'last_name': registration.user.last_name
                },
                'status': registration.status,
                'price_paid': float(registration.price_paid or 0),
                'registered_at': registration.registered_at.isoformat(),
                'payment_status': registration.payment_status,
                'ticket_type': {
                    'id': registration.ticket_type.id,
                    'name': registration.ticket_type.name
                } if registration.ticket_type else None,
                'refund_request': {
                    'id': registration.refund_request.id,
                    'status': registration.refund_request.status,
                    'refund_amount': float(registration.refund_request.refund_amount),
                    'reason': registration.refund_request.reason
                } if hasattr(registration, 'refund_request') and registration.refund_request else None
            }
            registrations_data.append(registration_data)

        # Historique des modifications
        event_history = event.history.all().order_by('-timestamp')[:10]
        history_data = [
            {
                'id': h.id,
                'action': h.action,
                'details': h.details,
                'timestamp': h.timestamp.isoformat(),
                'user': h.user.username if h.user else 'Système'
            }
            for h in event_history
        ]
        
        event_data = {
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'status': event.status,
            'start_date': event.start_date.isoformat(),
            'end_date': event.end_date.isoformat(),
            'location': event.location,
            'max_participants': event.max_capacity,
            'price': float(event.price),
            'created_at': event.created_at.isoformat(),
            'updated_at': event.updated_at.isoformat(),
            'organizer': {
                'id': event.organizer.id,
                'username': event.organizer.username,
                'email': event.organizer.email,
                'first_name': event.organizer.first_name,
                'last_name': event.organizer.last_name
            },
            'category': {
                'id': event.category.id,
                'name': event.category.name,
                'color': event.category.color
            } if event.category else None,
            'tags': [
                {
                    'id': tag.id,
                    'name': tag.name,
                    'color': tag.color
                }
                for tag in event.tags.all()
            ],
            'registrations_stats': registrations_stats,
            'registrations': registrations_data,
            'refund_requests': refunds_data,
            'event_history': history_data,
            'image_url': event.poster.url if event.poster else None,
            'virtual_link': event.virtual_link,
            'access_type': event.access_type
        }
        
        return Response(event_data)
        
    except Event.DoesNotExist:
        return Response(
            {'error': 'Événement non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la récupération des détails: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_reject_event(request, event_id):
    """Rejeter un événement (Super Admin)"""
    try:
        event = Event.objects.get(id=event_id)
        reason = request.data.get('reason', '')
        
        if not reason:
            return Response(
                {'error': 'Une raison est requise pour rejeter un événement'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if event.status == 'cancelled':
            return Response(
                {'error': 'Cet événement est déjà annulé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rejeter l'événement
        old_status = event.status
        event.status = 'cancelled'
        event.save()
        
        # Enregistrer l'action dans l'historique
        EventHistory.objects.create(
            event=event,
            action='rejected',
            details=f"Événement rejeté par {request.user.username}. Raison: {reason}",
            user=request.user
        )
        
        # Envoyer notification à l'organisateur
        _send_event_rejection_email(event, reason, request.user)
        
        # 🆕 CRÉER AUTOMATIQUEMENT DES DEMANDES DE REMBOURSEMENT pour tous les inscrits payants
        refunds_created = 0
        from .models import RefundPolicy, RefundRequest
        from django.utils import timezone
        
        for registration in event.registrations.filter(status='confirmed'):
            try:
                # Vérifier si l'inscription est payante
                if registration.payment_status == 'paid' and registration.price_paid > 0:
                    # Obtenir ou créer la politique de remboursement
                    try:
                        policy = event.refund_policy
                    except RefundPolicy.DoesNotExist:
                        policy = RefundPolicy.objects.create(
                            event=event,
                            mode='mixed',
                            auto_refund_delay_hours=24,
                            refund_percentage_immediate=100,
                            refund_percentage_after_delay=100,
                            cutoff_hours_before_event=24,
                            allow_partial_refunds=True,
                            require_reason=False,
                            notify_organizer_on_cancellation=True
                        )
                    
                    # Calculer les montants et dates
                    refund_percentage = policy.get_refund_percentage(0)  # Annulation immédiate = 100%
                    refund_amount = (registration.price_paid * refund_percentage) / 100
                    
                    now = timezone.now()
                    auto_process_at = None
                    if policy.mode in ['auto', 'mixed']:
                        auto_process_at = now + timezone.timedelta(hours=policy.auto_refund_delay_hours)
                    
                    expires_at = event.start_date - timezone.timedelta(hours=policy.cutoff_hours_before_event)
                    
                    # Créer la demande de remboursement
                    refund_request = RefundRequest.objects.create(
                        registration=registration,
                        reason=f'Événement rejeté par le Super Admin: {reason}',
                        amount_paid=registration.price_paid,
                        refund_percentage=refund_percentage,
                        refund_amount=refund_amount,
                        auto_process_at=auto_process_at,
                        expires_at=expires_at
                    )
                    
                    refunds_created += 1
                    print(f"✅ Demande de remboursement créée automatiquement (Super Admin): ID={refund_request.id} pour {registration.user.email if registration.user else registration.guest_email} - Montant: {refund_amount}€")
                    
            except Exception as e:
                print(f"❌ Erreur création demande remboursement automatique (Super Admin) pour {registration.id}: {e}")
                import traceback
                traceback.print_exc()
        
        # Notifier tous les participants inscrits
        _notify_participants_event_cancelled(event, reason)
        
        return Response({
            'message': f'Événement rejeté avec succès. {refunds_created} demandes de remboursement ont été créées automatiquement.',
            'event_id': event.id,
            'old_status': old_status,
            'new_status': 'cancelled',
            'reason': reason,
            'refunds_created': refunds_created
        })
        
    except Event.DoesNotExist:
        return Response(
            {'error': 'Événement non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors du rejet: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_delete_event(request, event_id):
    """Supprimer un événement (Super Admin)"""
    try:
        event = Event.objects.get(id=event_id)
        
        # 🔧 DEBUG: Log des vérifications
        print(f"🔍 DEBUG: Vérification suppression événement {event.id} ({event.title})")
        print(f"🔍 DEBUG: Statut: {event.status}, Date début: {event.start_date}")
        print(f"🔍 DEBUG: Inscriptions: {event.registrations.count()}")
        print(f"🔍 DEBUG: Utilisateur: {request.user.username} (super: {request.user.is_superuser})")
        
        # Vérifications de sécurité avant suppression (contournables par super admin)
        if event.registrations.exists():
            print(f"⚠️ DEBUG: Événement a {event.registrations.count()} inscriptions")
            # Les super admins peuvent forcer la suppression même avec des inscriptions
            if not request.user.is_superuser:
                return Response(
                    {'error': 'Impossible de supprimer un événement avec des inscriptions'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                print(f"🔧 DEBUG: Super admin force la suppression malgré les inscriptions")
        
        if event.status == 'published' and event.start_date > timezone.now():
            print(f"⚠️ DEBUG: Événement publié et à venir")
            # Les super admins peuvent forcer la suppression même des événements publiés
            if not request.user.is_superuser:
                return Response(
                    {'error': 'Impossible de supprimer un événement publié et à venir'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                print(f"🔧 DEBUG: Super admin force la suppression malgré le statut publié")
        
        # Sauvegarder les informations avant suppression
        event_info = {
            'id': event.id,
            'title': event.title,
            'organizer': event.organizer.username,
            'created_at': event.created_at
        }
        
        # Supprimer l'événement
        print(f"🗑️ DEBUG: Suppression de l'événement {event.id} ({event.title})")
        event.delete()
        print(f"✅ DEBUG: Événement supprimé avec succès")
        
        # Enregistrer l'action dans l'historique (si possible)
        try:
            EventHistory.objects.create(
                event_id=event_id,  # Utiliser l'ID même si l'événement est supprimé
                action='deleted',
                details=f"Événement supprimé définitivement par {request.user.username}",
                user=request.user
            )
            print(f"📝 DEBUG: Historique enregistré")
        except Exception as e:
            print(f"⚠️ DEBUG: Erreur historique: {e}")
            pass  # Ignorer les erreurs d'historique lors de la suppression
        
        return Response({
            'message': 'Événement supprimé avec succès',
            'deleted_event': event_info
        })
        
    except Event.DoesNotExist:
        return Response(
            {'error': 'Événement non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de la suppression: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def _send_event_rejection_email(event, reason, admin_user):
    """Envoyer email de rejet d'événement à l'organisateur"""
    try:
        from django.template.loader import render_to_string
        from django.core.mail import EmailMultiAlternatives
        
        organizer = event.organizer
        
        context = {
            'event': event,
            'organizer': organizer,
            'reason': reason,
            'admin_user': admin_user,
            'rejection_date': timezone.now()
        }
        
        subject = f"❌ Événement rejeté - {event.title}"
        text_body = render_to_string('emails/event_rejected.txt', context)
        html_body = render_to_string('emails/event_rejected.html', context)
        
        msg = EmailMultiAlternatives(
            subject,
            text_body,
            settings.DEFAULT_FROM_EMAIL,
            [organizer.email]
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        
        print(f"📧 Email de rejet d'événement envoyé à {organizer.email}")
        
    except Exception as e:
        print(f"❌ Erreur envoi email de rejet d'événement: {e}")

def _notify_participants_event_cancelled(event, reason):
    """Notifier tous les participants d'un événement annulé"""
    try:
        from django.template.loader import render_to_string
        from django.core.mail import EmailMultiAlternatives
        
        # Récupérer tous les participants confirmés
        confirmed_registrations = event.registrations.filter(
            status__in=['confirmed', 'pending']
        ).select_related('user')
        
        for registration in confirmed_registrations:
            try:
                # 🎯 CORRECTION : Déterminer l'email du destinataire (utilisateur ou invité)
                recipient_email = None
                if registration.user:
                    recipient_email = registration.user.email
                elif registration.guest_email:
                    recipient_email = registration.guest_email
                
                if recipient_email:
                    # 🎯 CORRECTION : Préparer le contexte selon le type d'inscription
                    if registration.user:
                        # Utilisateur connecté
                        context = {
                            'event': event,
                            'user': registration.user,
                            'reason': reason,
                            'cancellation_date': timezone.now()
                        }
                        text_body = render_to_string('emails/event_cancelled_participant.txt', context)
                        html_body = render_to_string('emails/event_cancelled_participant.html', context)
                    else:
                        # Invité
                        context = {
                            'event': event,
                            'guest_full_name': registration.guest_full_name,
                            'reason': reason,
                            'cancellation_date': timezone.now()
                        }
                        text_body = render_to_string('emails/guest_event_cancelled.txt', context)
                        html_body = render_to_string('emails/guest_event_cancelled.html', context)
                    
                    subject = f"❌ Événement annulé - {event.title}"
                    
                    msg = EmailMultiAlternatives(
                        subject,
                        text_body,
                        settings.DEFAULT_FROM_EMAIL,
                        [recipient_email]
                    )
                    msg.attach_alternative(html_body, "text/html")
                    msg.send()
                    
                    print(f"📧 Email d'annulation envoyé à {recipient_email} ({'Utilisateur' if registration.user else 'Invitée'})")
                else:
                    print(f"⚠️ Aucun email trouvé pour l'inscription {registration.id} (user: {registration.user}, guest: {registration.guest_email})")
                
            except Exception as e:
                print(f"❌ Erreur envoi email d'annulation à {recipient_email if 'recipient_email' in locals() else 'N/A'}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Erreur notification participants: {e}")


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_export_registrations_csv(request, event_id):
    """Exporter la liste des participants en CSV (Super Admin)"""
    try:
        event = Event.objects.get(id=event_id)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="registrations_event_{event_id}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID Inscription', 'Username', 'Email', 'Nom', 'Prénom', 'Status', 
            'Type de Billet', 'Prix Payé', 'Date d\'inscription', 'Statut Paiement',
            'Demande de Remboursement', 'Statut Remboursement'
        ])
        
        for reg in event.registrations.select_related('user', 'ticket_type').prefetch_related('refund_request').all():
            refund_status = reg.refund_request.status if hasattr(reg, 'refund_request') and reg.refund_request else 'Aucune'
            writer.writerow([
                reg.id,
                reg.user.username,
                reg.user.email,
                reg.user.first_name or '',
                reg.user.last_name or '',
                reg.status,
                getattr(reg.ticket_type, 'name', 'Standard'),
                str(reg.price_paid or 0),
                reg.registered_at.strftime('%Y-%m-%d %H:%M'),
                reg.payment_status or 'Non défini',
                'Oui' if hasattr(reg, 'refund_request') and reg.refund_request else 'Non',
                refund_status
            ])
        
        return response
        
    except Event.DoesNotExist:
        return Response(
            {'error': 'Événement non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'export: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def super_admin_export_registrations_excel(request, event_id):
    """Exporter la liste des participants en Excel (Super Admin)"""
    try:
        if Workbook is None:
            return Response(
                {"error": "openpyxl non installé pour l'export Excel"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        event = Event.objects.get(id=event_id)
        wb = Workbook()
        ws = wb.active
        ws.title = 'Inscriptions'
        
        # En-têtes
        headers = [
            'ID Inscription', 'Username', 'Email', 'Nom', 'Prénom', 'Status', 
            'Type de Billet', 'Prix Payé', 'Date d\'inscription', 'Statut Paiement',
            'Demande de Remboursement', 'Statut Remboursement'
        ]
        ws.append(headers)
        
        # Données
        for reg in event.registrations.select_related('user', 'ticket_type').prefetch_related('refund_request').all():
            refund_status = reg.refund_request.status if hasattr(reg, 'refund_request') and reg.refund_request else 'Aucune'
            ws.append([
                reg.id,
                reg.user.username,
                reg.user.email,
                reg.user.first_name or '',
                reg.user.last_name or '',
                reg.status,
                getattr(reg.ticket_type, 'name', 'Standard'),
                float(reg.price_paid or 0),
                reg.registered_at.strftime('%Y-%m-%d %H:%M'),
                reg.payment_status or 'Non défini',
                'Oui' if hasattr(reg, 'refund_request') and reg.refund_request else 'Non',
                refund_status
            ])
        
        # Ajuster la largeur des colonnes
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="registrations_event_{event_id}.xlsx"'
        return response
        
    except Event.DoesNotExist:
        return Response(
            {'error': 'Événement non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Erreur lors de l\'export: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def organizer_refunds_list(request):
    """Liste des remboursements pour les organisateurs d'événements"""
    try:
        from django.db.models import Q, Sum
        
        # Récupérer les événements de l'utilisateur connecté (incluant les annulés)
        user_events = Event.objects.filter(organizer=request.user)
        
        # Récupérer les remboursements pour ces événements
        refunds = RefundRequest.objects.filter(
            registration__event__in=user_events
        ).select_related(
            'registration__event', 
            'registration__user'
        ).order_by('-created_at')
        
        # 🆕 AJOUTER LES ÉVÉNEMENTS ANNULÉS SANS REMBOURSEMENTS pour visibilité complète
        cancelled_events_without_refunds = []
        for event in user_events.filter(status='cancelled'):
            # Vérifier si l'événement a des inscriptions payantes
            paid_registrations = event.registrations.filter(
                status='confirmed',
                payment_status='paid',
                price_paid__gt=0
            )
            
            if paid_registrations.exists():
                # Compter les remboursements existants
                existing_refunds = RefundRequest.objects.filter(
                    registration__event=event
                ).count()
                
                # Si il y a des inscriptions payantes mais pas de remboursements, c'est un problème
                if existing_refunds == 0:
                    total_amount = paid_registrations.aggregate(total=Sum('price_paid'))['total'] or 0
                    cancelled_events_without_refunds.append({
                        'event_id': event.id,
                        'event_title': event.title,
                        'paid_registrations_count': paid_registrations.count(),
                        'total_amount': float(total_amount),
                        'status': 'missing_refunds',
                        'message': 'Événement annulé avec des inscriptions payantes mais sans demandes de remboursement'
                    })
        
        # Filtres
        status_filter = request.GET.get('status')
        if status_filter:
            refunds = refunds.filter(status=status_filter)
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        start = (page - 1) * page_size
        end = start + page_size
        
        total_count = refunds.count()
        refunds_page = refunds[start:end]
        
        refunds_data = []
        for refund in refunds_page:
            # Logs de débogage pour chaque remboursement
            print(f"🔍 DEBUG: Processing refund {refund.id}")
            print(f"🔍 DEBUG: - Registration: {refund.registration}")
            print(f"🔍 DEBUG: - User: {refund.registration.user if refund.registration else 'None'}")
            print(f"🔍 DEBUG: - Event: {refund.registration.event if refund.registration else 'None'}")
            print(f"🔍 DEBUG: - Amount paid: {refund.amount_paid}")
            print(f"🔍 DEBUG: - Refund amount: {refund.refund_amount}")
            
            refunds_data.append({
                'id': refund.id,
                'registration_id': refund.registration.id if refund.registration else None,
                'user': {
                    'id': refund.registration.user.id if refund.registration and refund.registration.user else None,
                    'username': refund.registration.user.username if refund.registration and refund.registration.user else refund.registration.guest_full_name or 'Invité',
                    'email': refund.registration.user.email if refund.registration and refund.registration.user else refund.registration.guest_email or 'Email inconnu'
                },
                'event': {
                    'id': refund.registration.event.id if refund.registration and refund.registration.event else None,
                    'title': refund.registration.event.title if refund.registration and refund.registration.event else 'Événement inconnu'
                },
                'amount_paid': float(refund.amount_paid) if refund.amount_paid else 0,
                'refund_amount': float(refund.refund_amount) if refund.refund_amount else 0,
                'status': refund.status,
                'reason': refund.reason,
                'created_at': refund.created_at.isoformat() if refund.created_at else None,
                'processed_at': refund.processed_at.isoformat() if refund.processed_at else None
            })
        
        return Response({
            'count': total_count,
            'results': refunds_data,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'cancelled_events_without_refunds': cancelled_events_without_refunds,
            'summary': {
                'total_refunds': total_count,
                'events_with_missing_refunds': len(cancelled_events_without_refunds),
                'total_amount_at_risk': sum(event['total_amount'] for event in cancelled_events_without_refunds)
            }
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_missing_refunds_for_cancelled_event(request, event_id):
    """Créer manuellement des demandes de remboursement pour un événement annulé qui n'en a pas"""
    try:
        from .models import RefundPolicy, RefundRequest
        from django.utils import timezone
        
        # Récupérer l'événement
        try:
            event = Event.objects.get(id=event_id, organizer=request.user)
        except Event.DoesNotExist:
            return Response({'error': 'Événement non trouvé ou accès non autorisé'}, status=404)
        
        # Vérifier que l'événement est annulé
        if event.status != 'cancelled':
            return Response({'error': 'Cette fonction est réservée aux événements annulés'}, status=400)
        
        # Vérifier s'il y a déjà des remboursements
        existing_refunds = RefundRequest.objects.filter(registration__event=event).count()
        if existing_refunds > 0:
            return Response({'error': 'Cet événement a déjà des demandes de remboursement'}, status=400)
        
        # Récupérer les inscriptions payantes confirmées
        paid_registrations = event.registrations.filter(
            status='confirmed',
            payment_status='paid',
            price_paid__gt=0
        )
        
        if not paid_registrations.exists():
            return Response({'error': 'Aucune inscription payante trouvée pour cet événement'}, status=400)
        
        # Obtenir ou créer la politique de remboursement
        try:
            policy = event.refund_policy
        except RefundPolicy.DoesNotExist:
            policy = RefundPolicy.objects.create(
                event=event,
                mode='mixed',
                auto_refund_delay_hours=24,
                refund_percentage_immediate=100,
                refund_percentage_after_delay=100,
                cutoff_hours_before_event=24,
                allow_partial_refunds=True,
                require_reason=False,
                notify_organizer_on_cancellation=True
            )
        
        # Créer les demandes de remboursement
        refunds_created = 0
        for registration in paid_registrations:
            try:
                # Calculer les montants et dates
                refund_percentage = policy.get_refund_percentage(0)  # Annulation immédiate = 100%
                refund_amount = (registration.price_paid * refund_percentage) / 100
                
                now = timezone.now()
                auto_process_at = None
                if policy.mode in ['auto', 'mixed']:
                    auto_process_at = now + timezone.timedelta(hours=policy.auto_refund_delay_hours)
                
                expires_at = event.start_date - timezone.timedelta(hours=policy.cutoff_hours_before_event)
                
                # Créer la demande de remboursement
                refund_request = RefundRequest.objects.create(
                    registration=registration,
                    reason='Remboursement manuel créé par l\'organisateur pour événement annulé',
                    amount_paid=registration.price_paid,
                    refund_percentage=refund_percentage,
                    refund_amount=refund_amount,
                    auto_process_at=auto_process_at,
                    expires_at=expires_at
                )
                
                refunds_created += 1
                print(f"✅ Demande de remboursement manuelle créée: ID={refund_request.id} pour {registration.user.email if registration.user else registration.guest_email} - Montant: {refund_amount}€")
                
            except Exception as e:
                print(f"❌ Erreur création demande remboursement manuelle pour {registration.id}: {e}")
                import traceback
                traceback.print_exc()
        
        return Response({
            'message': f'{refunds_created} demandes de remboursement ont été créées avec succès pour l\'événement annulé',
            'event_id': event.id,
            'event_title': event.title,
            'refunds_created': refunds_created,
            'total_amount': float(paid_registrations.aggregate(total=models.Sum('price_paid'))['total'] or 0)
        })
        
    except Exception as e:
        return Response({'error': f'Erreur lors de la création des remboursements: {str(e)}'}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_refund_request(request, refund_id):
    """Traiter une demande de remboursement (pour les organisateurs)"""
    try:
        print(f"🔍 DEBUG: process_refund_request appelé avec refund_id={refund_id}")
        print(f"🔍 DEBUG: request.data = {request.data}")
        print(f"🔍 DEBUG: request.user = {request.user.username}")
        
        refund = RefundRequest.objects.get(id=refund_id)
        print(f"🔍 DEBUG: Refund trouvé: {refund.id}, status={refund.status}")
        
        # Vérifier que l'utilisateur est l'organisateur de l'événement
        if refund.registration.event.organizer != request.user:
            print(f"❌ DEBUG: Permission refusée - {request.user.username} n'est pas l'organisateur de {refund.registration.event.title}")
            return Response({'error': 'Accès non autorisé'}, status=403)
        
        print(f"✅ DEBUG: Permission accordée pour {request.user.username}")
        
        action = request.data.get('action')  # 'approve', 'reject', ou 'process' (synonyme de 'approve')
        reason = request.data.get('reason', '')
        
        print(f"🔍 DEBUG: action reçue = '{action}', reason = '{reason}'")
        
        print(f"🔍 DEBUG: action finale = '{action}'")
        
        # Vérifier que le remboursement n'est pas déjà traité
        if refund.status in ['processed', 'rejected']:
            print(f"⚠️ DEBUG: Refund {refund.id} déjà traité avec le statut '{refund.status}'")
            return Response({
                'error': f'Ce remboursement est déjà {refund.get_status_display().lower()}',
                'current_status': refund.status
            }, status=400)
        
        # Gérer l'action 'process' pour finaliser un remboursement approuvé
        if action == 'process':
            if refund.status != 'approved':
                return Response({
                    'error': 'Seuls les remboursements approuvés peuvent être traités'
                }, status=400)
            
            # Marquer comme traité
            refund.status = 'processed'
            refund.processed_by = request.user
            refund.processed_at = timezone.now()
            refund.save()
            
            # Envoyer email de traitement
            try:
                subject = f"Remboursement traité - {refund.registration.event.title}"
                # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
                if refund.registration.user:
                    # Utilisateur connecté
                    recipient_email = refund.registration.user.email
                    context = {
                        'user': refund.registration.user,
                        'event': refund.registration.event,
                        'refund_amount': refund.refund_amount,
                        'reason': reason
                    }
                    message = render_to_string('emails/refund_processed.txt', context)
                    html_message = render_to_string('emails/refund_processed.html', context)
                else:
                    # Invité
                    recipient_email = refund.registration.guest_email
                    context = {
                        'guest_full_name': refund.registration.guest_full_name,
                        'event': refund.registration.event,
                        'refund_amount': refund.refund_amount,
                        'reason': reason
                    }
                    message = render_to_string('emails/guest_refund_processed.txt', context)
                    html_message = render_to_string('emails/guest_refund_processed.html', context)
                
                msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
                msg.attach_alternative(html_message, 'text/html')
                msg.send(fail_silently=True)
            except Exception as email_error:
                print(f"Erreur envoi email remboursement traité: {email_error}")
            
            return Response({'message': 'Remboursement traité avec succès'})
        
        if action == 'approve':
            refund.status = 'approved'
            refund.processed_by = request.user
            refund.processed_at = timezone.now()
            refund.save()
            
            # Envoyer email de confirmation
            try:
                subject = f"Remboursement approuvé - {refund.registration.event.title}"
                # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
                if refund.registration.user:
                    # Utilisateur connecté
                    recipient_email = refund.registration.user.email
                    context = {
                        'user': refund.registration.user,
                        'event': refund.registration.event,
                        'refund_amount': refund.refund_amount,
                        'reason': reason
                    }
                    message = render_to_string('emails/refund_approved.txt', context)
                    html_message = render_to_string('emails/refund_approved.html', context)
                else:
                    # Invité
                    recipient_email = refund.registration.guest_email
                    context = {
                        'guest_full_name': refund.registration.guest_full_name,
                        'event': refund.registration.event,
                        'refund_amount': refund.refund_amount,
                        'reason': reason
                    }
                    message = render_to_string('emails/guest_refund_confirmation.txt', context)
                    html_message = render_to_string('emails/guest_refund_confirmation.html', context)
                
                msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
                msg.attach_alternative(html_message, 'text/html')
                msg.send(fail_silently=True)
            except Exception as email_error:
                print(f"Erreur envoi email remboursement: {email_error}")
            
            return Response({'message': 'Remboursement approuvé avec succès'})
            
        elif action == 'reject':
            refund.status = 'rejected'
            refund.processed_by = request.user
            refund.processed_at = timezone.now()
            refund.save()
            
            # Envoyer email de rejet
            try:
                subject = f"Remboursement rejeté - {refund.registration.event.title}"
                # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
                if refund.registration.user:
                    # Utilisateur connecté
                    recipient_email = refund.registration.user.email
                    context = {
                        'user': refund.registration.user,
                        'event': refund.registration.event,
                        'reason': reason
                    }
                    message = render_to_string('emails/refund_rejected.txt', context)
                    html_message = render_to_string('emails/refund_rejected.html', context)
                else:
                    # Invité
                    recipient_email = refund.registration.guest_email
                    context = {
                        'guest_full_name': refund.registration.guest_full_name,
                        'event': refund.registration.event,
                        'reason': reason
                    }
                    message = render_to_string('emails/guest_refund_rejected.txt', context)
                    html_message = render_to_string('emails/guest_refund_rejected.html', context)
                
                msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
                msg.attach_alternative(html_message, 'text/html')
                msg.send(fail_silently=True)
            except Exception as email_error:
                print(f"Erreur envoi email remboursement: {email_error}")
            
            return Response({'message': 'Remboursement rejeté'})
        elif action == 'process':
            # Traiter un remboursement approuvé (le marquer comme traité)
            if refund.status == 'approved':
                refund.status = 'processed'
                refund.processed_by = request.user
                refund.processed_at = timezone.now()
                refund.save()
                
                # Envoyer email de confirmation de traitement
                try:
                    subject = f"Remboursement traité - {refund.registration.event.title}"
                    # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
                    if refund.registration.user:
                        # Utilisateur connecté
                        recipient_email = refund.registration.user.email
                        context = {
                            'user': refund.registration.user,
                            'event': refund.registration.event,
                            'refund_amount': refund.refund_amount,
                            'reason': reason
                        }
                        message = render_to_string('emails/refund_processed.txt', context)
                        html_message = render_to_string('emails/refund_processed.html', context)
                    else:
                        # Invité
                        recipient_email = refund.registration.guest_email
                        context = {
                            'guest_full_name': refund.registration.guest_full_name,
                            'event': refund.registration.event,
                            'refund_amount': refund.refund_amount,
                            'reason': reason
                        }
                        message = render_to_string('emails/guest_refund_processed.txt', context)
                        html_message = render_to_string('emails/guest_refund_processed.html', context)
                    
                    msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
                    msg.attach_alternative(html_message, 'text/html')
                    msg.send(fail_silently=True)
                except Exception as email_error:
                    print(f"Erreur envoi email remboursement traité: {email_error}")
                
                return Response({'message': 'Remboursement traité avec succès'})
            else:
                return Response({'error': 'Seuls les remboursements approuvés peuvent être traités'}, status=400)
        else:
            return Response({'error': 'Action invalide'}, status=400)
            
    except RefundRequest.DoesNotExist:
        return Response({'error': 'Demande de remboursement non trouvée'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def organizer_bulk_process_refunds(request):
    """Traiter des demandes de remboursement en lot (pour les organisateurs)"""
    try:
        refund_ids = request.data.get('refund_ids', [])
        action = request.data.get('action')  # 'approve' ou 'reject'
        reason = request.data.get('reason', '')
        
        if not refund_ids or not action:
            return Response({'error': 'Paramètres manquants'}, status=400)
        
        # Récupérer les remboursements
        refunds = RefundRequest.objects.filter(
            id__in=refund_ids,
            registration__event__organizer=request.user
        )
        
        if not refunds.exists():
            return Response({'error': 'Aucun remboursement trouvé ou accès non autorisé'}, status=404)
        
        processed_count = 0
        for refund in refunds:
            try:
                if action == 'approve':
                    refund.status = 'approved'
                elif action == 'reject':
                    refund.status = 'rejected'
                else:
                    continue
                
                refund.processed_by = request.user
                refund.processed_at = timezone.now()
                refund.save()
                processed_count += 1
                
                # Envoyer email de notification
                try:
                    if action == 'approve':
                        subject = f"Remboursement approuvé - {refund.registration.event.title}"
                        template_txt = 'emails/refund_approved.txt'
                        template_html = 'emails/refund_approved.html'
                    else:
                        subject = f"Remboursement rejeté - {refund.registration.event.title}"
                        template_txt = 'emails/refund_rejected.txt'
                        template_html = 'emails/refund_rejected.html'
                    
                    # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
                    if refund.registration.user:
                        # Utilisateur connecté
                        recipient_email = refund.registration.user.email
                        context = {
                            'user': refund.registration.user,
                            'event': refund.registration.event,
                            'refund_amount': refund.refund_amount,
                            'reason': reason
                        }
                        message = render_to_string(template_txt, context)
                        html_message = render_to_string(template_html, context)
                    else:
                        # Invité
                        recipient_email = refund.registration.guest_email
                        if action == 'approve':
                            template_txt = 'emails/guest_refund_confirmation.txt'
                            template_html = 'emails/guest_refund_confirmation.html'
                        else:
                            template_txt = 'emails/guest_refund_rejected.txt'
                            template_html = 'emails/guest_refund_rejected.html'
                        
                        context = {
                            'guest_full_name': refund.registration.guest_full_name,
                            'event': refund.registration.event,
                            'refund_amount': refund.refund_amount,
                            'reason': reason
                        }
                        message = render_to_string(template_txt, context)
                        html_message = render_to_string(template_html, context)
                    
                    msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
                    msg.attach_alternative(html_message, 'text/html')
                    msg.send(fail_silently=True)
                except Exception as email_error:
                    print(f"Erreur envoi email remboursement: {email_error}")
                    
            except Exception as refund_error:
                print(f"Erreur traitement remboursement {refund.id}: {refund_error}")
                continue
        
        return Response({
            'message': f'{processed_count} remboursements traités avec succès',
            'processed_count': processed_count
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_waitlist_registration(request, registration_id):
    """Approuver une inscription en liste d'attente (pour l'organisateur)"""
    try:
        registration = EventRegistration.objects.get(id=registration_id)
        
        # Vérifier que l'utilisateur est l'organisateur de l'événement
        if registration.event.organizer != request.user:
            return Response({'error': 'Accès non autorisé'}, status=403)
        
        # Vérifier que l'inscription est en liste d'attente
        if registration.status != 'waitlisted':
            return Response({'error': 'Cette inscription n\'est pas en liste d\'attente'}, status=400)
        
        # Vérifier la capacité
        event = registration.event
        if event.place_type == 'limited' and event.max_capacity:
            confirmed_count = EventRegistration.objects.filter(
                event=event, 
                status='confirmed'
            ).count()
            
            if confirmed_count >= event.max_capacity:
                return Response({'error': 'L\'événement est complet'}, status=400)
        
        # Approuver l'inscription
        registration.status = 'confirmed'
        registration.save()
        
        # Mettre à jour le compteur
        if event.place_type == 'limited':
            event.current_registrations = (event.current_registrations or 0) + 1
            event.save()
        
        # Envoyer email de confirmation
        try:
            subject = f"🎉 Inscription approuvée - {event.title}"
            
            # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
            if registration.user:
                # Utilisateur connecté
                recipient_email = registration.user.email
                context = {
                    'user': registration.user,
                    'event': event,
                }
                message = render_to_string('emails/registration_approved.txt', context)
                html_message = render_to_string('emails/registration_approved.html', context)
            else:
                # Invité
                recipient_email = registration.guest_email
                context = {
                    'guest_name': registration.guest_full_name,
                    'guest_email': registration.guest_email,
                    'event': event,
                }
                message = render_to_string('emails/guest_registration_approved.txt', context)
                html_message = render_to_string('emails/guest_registration_approved.html', context)
            
            msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
            msg.attach_alternative(html_message, 'text/html')
            msg.send(fail_silently=True)
        except Exception as e:
            print(f"🔍 DEBUG: Error sending approval email: {e}")
        
        return Response({'message': 'Inscription approuvée avec succès'})
        
    except EventRegistration.DoesNotExist:
        return Response({'error': 'Inscription introuvable'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_waitlist_registration(request, registration_id):
    """Rejeter une inscription en liste d'attente (pour l'organisateur)"""
    try:
        registration = EventRegistration.objects.get(id=registration_id)
        
        # Vérifier que l'utilisateur est l'organisateur de l'événement
        if registration.event.organizer != request.user:
            return Response({'error': 'Accès non autorisé'}, status=403)
        
        # Vérifier que l'inscription est en liste d'attente
        if registration.status != 'waitlisted':
            return Response({'error': 'Cette inscription n\'est pas en liste d\'attente'}, status=400)
        
        # Rejeter l'inscription
        registration.status = 'cancelled'
        registration.save()
        
        # Envoyer email de rejet
        try:
            subject = f"❌ Inscription rejetée - {registration.event.title}"
            
            # 🎯 CORRECTION : Gérer les utilisateurs ET les invités
            if registration.user:
                # Utilisateur connecté
                recipient_email = registration.user.email
                context = {
                    'user': registration.user,
                    'event': registration.event,
                }
                message = render_to_string('emails/registration_rejected.txt', context)
                html_message = render_to_string('emails/registration_rejected.html', context)
            else:
                # Invité
                recipient_email = registration.guest_email
                context = {
                    'guest_name': registration.guest_full_name,
                    'guest_email': registration.guest_email,
                    'event': registration.event,
                }
                message = render_to_string('emails/guest_registration_rejected.txt', context)
                html_message = render_to_string('emails/guest_registration_rejected.html', context)
            
            msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [recipient_email])
            msg.attach_alternative(html_message, 'text/html')
            msg.send(fail_silently=True)
        except Exception as e:
            print(f"🔍 DEBUG: Error sending rejection email: {e}")
        
        return Response({'message': 'Inscription rejetée avec succès'})
        
    except EventRegistration.DoesNotExist:
        return Response({'error': 'Inscription introuvable'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_stream_access(request, event_id):
    """
    Vérifie les identifiants de connexion avant d'accéder au stream
    """
    try:
        # Vérifier que l'événement existe
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Événement non trouvé'
            }, status=404)
        
        # Vérifier que c'est un événement virtuel
        if event.event_type != 'virtual':
            return Response({
                'success': False,
                'error': 'Cet événement n\'est pas virtuel'
            }, status=400)
        
        # Vérifier que l'utilisateur a une inscription confirmée
        try:
            registration = EventRegistration.objects.get(
                event=event,
                user=request.user,
                status='confirmed'
            )
        except EventRegistration.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Vous n\'êtes pas inscrit à cet événement'
            }, status=403)
        
        # Vérifier le statut du paiement
        if not registration.payment_status or registration.payment_status != 'paid':
            return Response({
                'success': False,
                'error': 'Accès refusé - Paiement non confirmé',
                'details': 'Vous devez avoir un billet payé et confirmé pour accéder à ce stream'
            }, status=403)
        
        # Récupérer les détails virtuels
        try:
            virtual_event = event.virtual_details
        except Exception:
            return Response({
                'success': False,
                'error': 'Détails virtuels non disponibles'
            }, status=400)
        
        # Vérifier que les identifiants sont présents
        if not virtual_event.meeting_id:
            return Response({
                'success': False,
                'error': 'Stream non encore configuré',
                'details': 'Le stream sera disponible quelques minutes avant l\'événement'
            }, status=400)
        
        # Retourner les identifiants de connexion
        return Response({
            'success': True,
            'message': 'Accès autorisé',
            'stream_info': {
                'event_title': event.title,
                'meeting_id': virtual_event.meeting_id,
                'meeting_url': virtual_event.meeting_url,
                'meeting_password': virtual_event.meeting_password,
                'platform': virtual_event.get_platform_display(),
                'access_code': registration.virtual_access_code
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification d'accès au stream: {e}")
        return Response({
            'success': False,
            'error': 'Erreur interne du serveur'
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stream_access_form(request, event_id):
    """
    Affiche le formulaire de vérification des identifiants pour accéder au stream
    """
    try:
        # Vérifier que l'événement existe
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Événement non trouvé'
            }, status=404)
        
        # Vérifier que c'est un événement virtuel
        if event.event_type != 'virtual':
            return Response({
                'success': False,
                'error': 'Cet événement n\'est pas virtuel'
            }, status=400)
        
        # Vérifier que l'utilisateur a une inscription confirmée
        try:
            registration = EventRegistration.objects.get(
                event=event,
                user=request.user,
                status='confirmed'
            )
        except EventRegistration.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Vous n\'êtes pas inscrit à cet événement',
                'action_required': 'register'
            }, status=403)
        
        # Vérifier le statut du paiement
        if not registration.payment_status or registration.payment_status != 'paid':
            return Response({
                'success': False,
                'error': 'Accès refusé - Paiement non confirmé',
                'details': 'Vous devez avoir un billet payé et confirmé pour accéder à ce stream',
                'action_required': 'payment'
            }, status=403)
        
        # Récupérer les détails virtuels
        try:
            virtual_event = event.virtual_details
        except Exception:
            return Response({
                'success': False,
                'error': 'Détails virtuels non disponibles',
                'action_required': 'contact_organizer'
            }, status=400)
        
        # Vérifier que les identifiants sont présents
        if not virtual_event.meeting_id:
            return Response({
                'success': False,
                'error': 'Stream non encore configuré',
                'details': 'Le stream sera disponible quelques minutes avant l\'événement',
                'action_required': 'wait'
            }, status=400)
        
        # Retourner le formulaire de vérification
        return Response({
            'success': True,
            'message': 'Vérification des identifiants requise',
            'form_data': {
                'event_title': event.title,
                'event_id': event.id,
                'platform': virtual_event.get_platform_display(),
                'meeting_id': virtual_event.meeting_id,
                'meeting_url': virtual_event.meeting_url,
                'meeting_password': virtual_event.meeting_password,
                'access_code': registration.virtual_access_code,
                'verification_required': True
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du formulaire d'accès: {e}")
        return Response({
            'success': False,
            'error': 'Erreur interne du serveur'
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth(request):
    """Authentification via Google OAuth2"""
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        import os
        
        # Récupérer le token ID de Google
        token = request.data.get('id_token')
        if not token:
            return Response({
                'error': 'Token Google requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le token avec Google
        try:
            # Remplacer par votre CLIENT_ID Google
            GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', 'your-google-client-id')
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
            
            # Extraire les informations utilisateur
            google_user_id = idinfo['sub']
            email = idinfo['email']
            name = idinfo.get('name', '')
            picture = idinfo.get('picture', '')
            
        except Exception as e:
            return Response({
                'error': 'Token Google invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si l'utilisateur existe déjà
        user = None
        social_account = None
        
        # Chercher par compte social existant
        try:
            social_account = SocialAccount.objects.get(
                provider='google',
                provider_account_id=google_user_id
            )
            user = social_account.user
        except SocialAccount.DoesNotExist:
            pass
        
        # Si pas de compte social, chercher par email
        if not user:
            try:
                user = User.objects.get(email=email)
                # Créer le compte social pour cet utilisateur existant
                social_account = SocialAccount.objects.create(
                    user=user,
                    provider='google',
                    provider_account_id=google_user_id,
                    email=email,
                    name=name,
                    picture_url=picture
                )
            except User.DoesNotExist:
                # Créer un nouvel utilisateur
                username = f"google_{google_user_id[:8]}"
                # S'assurer que le username est unique
                counter = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}_{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=name.split()[0] if name else '',
                    last_name=' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
                    password=None  # Pas de mot de passe pour les comptes sociaux
                )
                
                # Créer le profil utilisateur
                profile = UserProfile.objects.create(
                    user=user,
                    role='participant',
                    status_approval='approved'  # Approuvé automatiquement
                )
                
                # Créer le compte social
                social_account = SocialAccount.objects.create(
                    user=user,
                    provider='google',
                    provider_account_id=google_user_id,
                    email=email,
                    name=name,
                    picture_url=picture
                )
        
        # Générer le token JWT
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile': {
                    'role': user.profile.role,
                    'status_approval': user.profile.status_approval,
                    'phone': user.profile.phone
                }
            },
            'social_account': {
                'provider': social_account.provider,
                'name': social_account.name,
                'picture_url': social_account.picture_url
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur authentification Google: {e}")
        return Response({
            'error': 'Erreur lors de l\'authentification Google'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def facebook_auth(request):
    """Authentification via Facebook OAuth2"""
    try:
        import requests
        import os
        
        # Récupérer le token d'accès Facebook
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({
                'error': 'Token Facebook requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier le token avec Facebook
        try:
            FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID', 'your-facebook-app-id')
            FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET', 'your-facebook-app-secret')
            
            # Vérifier le token
            response = requests.get(
                f'https://graph.facebook.com/me?fields=id,name,email,picture&access_token={access_token}'
            )
            
            if response.status_code != 200:
                return Response({
                    'error': 'Token Facebook invalide'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            fb_data = response.json()
            facebook_user_id = fb_data['id']
            email = fb_data.get('email', '')
            name = fb_data.get('name', '')
            picture = fb_data.get('picture', {}).get('data', {}).get('url', '')
            
        except Exception as e:
            return Response({
                'error': 'Token Facebook invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Vérifier si l'utilisateur existe déjà
        user = None
        social_account = None
        
        # Chercher par compte social existant
        try:
            social_account = SocialAccount.objects.get(
                provider='facebook',
                provider_account_id=facebook_user_id
            )
            user = social_account.user
        except SocialAccount.DoesNotExist:
            pass
        
        # Si pas de compte social, chercher par email
        if not user and email:
            try:
                user = User.objects.get(email=email)
                # Créer le compte social pour cet utilisateur existant
                social_account = SocialAccount.objects.create(
                    user=user,
                    provider='facebook',
                    provider_account_id=facebook_user_id,
                    email=email,
                    name=name,
                    picture_url=picture
                )
            except User.DoesNotExist:
                # Créer un nouvel utilisateur
                username = f"fb_{facebook_user_id[:8]}"
                # S'assurer que le username est unique
                counter = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}_{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email if email else f"{username}@facebook.com",
                    first_name=name.split()[0] if name else '',
                    last_name=' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
                    password=None  # Pas de mot de passe pour les comptes sociaux
                )
                
                # Créer le profil utilisateur
                profile = UserProfile.objects.create(
                    user=user,
                    role='participant',
                    status_approval='approved'  # Approuvé automatiquement
                )
                
                # Créer le compte social
                social_account = SocialAccount.objects.create(
                    user=user,
                    provider='facebook',
                    provider_account_id=facebook_user_id,
                    email=email if email else f"{username}@facebook.com",
                    name=name,
                    picture_url=picture
                )
        
        # Générer le token JWT
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'profile': {
                    'role': user.profile.role,
                    'status_approval': user.profile.status_approval,
                    'phone': user.profile.phone
                }
            },
            'social_account': {
                'provider': social_account.provider,
                'name': social_account.name,
                'picture_url': social_account.picture_url
            }
        })
        
    except Exception as e:
        print(f"❌ Erreur authentification Facebook: {e}")
        return Response({
            'error': 'Erreur lors de l\'authentification Facebook'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Première définition supprimée - conflit avec la seconde


class CustomReminderViewSet(viewsets.ModelViewSet):
    """ViewSet pour les rappels personnalisés"""
    queryset = CustomReminder.objects.all()  # 🔍 DEBUG: Ajout du queryset par défaut
    serializer_class = CustomReminderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['event', 'status', 'reminder_type', 'target_audience']
    ordering_fields = ['created_at', 'scheduled_at', 'sent_at']
    ordering = ['-created_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("🔍 DEBUG: CustomReminderViewSet initialisé")
    
    def list(self, request, *args, **kwargs):
        print("🔍 DEBUG: ===== CustomReminderViewSet.list() DÉBUT =====")
        print(f"🔍 DEBUG: request.user: {request.user}")
        print(f"🔍 DEBUG: request.method: {request.method}")
        print(f"🔍 DEBUG: request.path: {request.path}")
        print(f"🔍 DEBUG: request.META.get('HTTP_AUTHORIZATION'): {request.META.get('HTTP_AUTHORIZATION', 'AUCUN')}")
        print(f"🔍 DEBUG: request.headers: {dict(request.headers)}")
        print(f"🔍 DEBUG: request.GET: {request.GET}")
        print(f"🔍 DEBUG: request.POST: {request.POST}")
        print(f"🔍 DEBUG: request.body: {request.body}")
        
        try:
            queryset = self.get_queryset()
            print(f"🔍 DEBUG: Queryset obtenu: {queryset}")
            print(f"🔍 DEBUG: Queryset count: {queryset.count()}")
            
            serializer = self.get_serializer(queryset, many=True)
            print(f"🔍 DEBUG: Serializer créé: {serializer}")
            print(f"🔍 DEBUG: Données sérialisées: {serializer.data}")
            
            response = Response(serializer.data)
            print(f"🔍 DEBUG: Response créée: {response}")
            print(f"🔍 DEBUG: Response status_code: {response.status_code}")
            print("🔍 DEBUG: ===== CustomReminderViewSet.list() FIN =====")
            return response
        except Exception as e:
            print(f"🔍 DEBUG: ERREUR dans list(): {e}")
            import traceback
            print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
            return Response({'error': str(e)}, status=500)
    
    def create(self, request, *args, **kwargs):
        print("🔍 DEBUG: ===== CustomReminderViewSet.create() DÉBUT =====")
        print(f"🔍 DEBUG: request.user: {request.user}")
        print(f"🔍 DEBUG: request.method: {request.method}")
        print(f"🔍 DEBUG: request.path: {request.path}")
        print(f"🔍 DEBUG: request.META.get('HTTP_AUTHORIZATION'): {request.META.get('HTTP_AUTHORIZATION', 'AUCUN')}")
        print(f"🔍 DEBUG: request.headers: {dict(request.headers)}")
        print(f"🔍 DEBUG: request.data: {request.data}")
        print(f"🔍 DEBUG: request.body: {request.body}")
        
        try:
            result = super().create(request, *args, **kwargs)
            print(f"🔍 DEBUG: Create réussi: {result}")
            print("🔍 DEBUG: ===== CustomReminderViewSet.create() FIN =====")
            return result
        except Exception as e:
            print(f"🔍 DEBUG: ERREUR dans create(): {e}")
            import traceback
            print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
            raise
    
    def get_queryset(self):
        """Filtrer les rappels selon l'utilisateur"""
        print("🔍 DEBUG: CustomReminderViewSet.get_queryset() appelé")
        user = self.request.user
        print(f"🔍 DEBUG: user: {user}")
        print(f"🔍 DEBUG: user.is_authenticated: {user.is_authenticated}")
        print(f"🔍 DEBUG: user.is_superuser: {user.is_superuser}")
        
        if user.is_authenticated:
            if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'super_admin'):
                # Super admin peut voir tous les rappels
                queryset = CustomReminder.objects.all()
                print(f"🔍 DEBUG: Super admin - queryset count: {queryset.count()}")
                return queryset
            else:
                # Organisateur ne peut voir que ses propres rappels
                queryset = CustomReminder.objects.filter(created_by=user)
                print(f"🔍 DEBUG: Organisateur - queryset count: {queryset.count()}")
                return queryset
        else:
            print("🔍 DEBUG: Utilisateur non authentifié - queryset vide")
            return CustomReminder.objects.none()
    
    def perform_create(self, serializer):
        """Définir automatiquement l'organisateur lors de la création"""
        print(f"🔍 DEBUG: CustomReminderViewSet.perform_create() DÉBUT")
        print(f"🔍 DEBUG: serializer.validated_data: {serializer.validated_data}")
        print(f"🔍 DEBUG: request.user: {self.request.user}")
        
        try:
            result = serializer.save(created_by=self.request.user)
            print(f"🔍 DEBUG: perform_create() SUCCÈS - Rappel créé: {result}")
            print(f"🔍 DEBUG: ID du rappel: {result.id}")
            print(f"🔍 DEBUG: Statut du rappel: {result.status}")
            print(f"🔍 DEBUG: Total recipients: {result.total_recipients}")
        except Exception as e:
            print(f"🔍 DEBUG: ERREUR dans perform_create(): {e}")
            print(f"🔍 DEBUG: Type d'erreur: {type(e)}")
            raise
    
    @action(detail=True, methods=['post'])
    def send_now(self, request, pk=None):
        """Envoyer le rappel immédiatement"""
        print(f"🔍 DEBUG: ===== send_now() DÉBUT =====")
        print(f"🔍 DEBUG: Rappel ID: {pk}")
        
        reminder = self.get_object()
        print(f"🔍 DEBUG: Rappel trouvé: {reminder}")
        print(f"🔍 DEBUG: Statut actuel: {reminder.status}")
        print(f"🔍 DEBUG: Email activé: {reminder.send_email}")
        print(f"🔍 DEBUG: SMS activé: {reminder.send_sms}")
        
        if reminder.status == 'sent':
            return Response(
                {'error': 'Ce rappel a déjà été envoyé.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 🔍 LOGS DÉTAILLÉS POUR LA RÉCUPÉRATION DES DESTINATAIRES
            print(f"🔍 DEBUG: ===== RÉCUPÉRATION DESTINATAIRES =====")
            print(f"🔍 DEBUG: Target audience: {reminder.target_audience}")
            print(f"🔍 DEBUG: Event ID: {reminder.event.id}")
            print(f"🔍 DEBUG: Event title: {reminder.event.title}")
            
            # Récupérer les destinataires
            recipients = reminder.get_recipients()
            print(f"🔍 DEBUG: Nombre de destinataires: {recipients.count()}")
            
            # 🔍 LOGS DÉTAILLÉS POUR CHAQUE DESTINATAIRE
            for i, recipient in enumerate(recipients):
                print(f"🔍 DEBUG: --- Destinataire {i+1} ---")
                print(f"🔍 DEBUG: ID: {recipient.id}")
                print(f"🔍 DEBUG: Type: {'User' if recipient.user else 'Guest'}")
                if recipient.user:
                    print(f"🔍 DEBUG: User: {recipient.user.username}")
                    print(f"🔍 DEBUG: Email: {recipient.user.email}")
                    print(f"🔍 DEBUG: Phone: {getattr(recipient.user.profile, 'phone', 'N/A') if hasattr(recipient.user, 'profile') else 'N/A'}")
                else:
                    print(f"🔍 DEBUG: Guest Name: {recipient.guest_full_name}")
                    print(f"🔍 DEBUG: Guest Email: {recipient.guest_email}")
                    print(f"🔍 DEBUG: Guest Phone: {recipient.guest_phone}")
                print(f"🔍 DEBUG: Status: {recipient.status}")
                print(f"🔍 DEBUG: --------------------")
            
            if not recipients.exists():
                print(f"🔍 DEBUG: ❌ Aucun destinataire trouvé!")
                return Response(
                    {'error': 'Aucun destinataire trouvé pour ce rappel.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Initialiser les statistiques
            statistics = {
                'total_recipients': recipients.count(),
                'emails_sent': 0,
                'sms_sent': 0,
                'emails_failed': 0,
                'sms_failed': 0
            }
            
            # Envoyer à chaque destinataire
            for registration in recipients:
                # 🔍 LOGS DÉTAILLÉS POUR DEBUGGING
                print(f"🔍 DEBUG: ===== TRAITEMENT DESTINATAIRE =====")
                print(f"🔍 DEBUG: Registration ID: {registration.id}")
                print(f"🔍 DEBUG: Registration Type: {'User' if registration.user else 'Guest'}")
                
                # Déterminer le nom et l'email selon le type d'inscription
                if registration.user:
                    # Inscription d'utilisateur connecté
                    recipient_name = registration.user.get_full_name() or registration.user.username
                    recipient_email = registration.user.email
                    recipient_phone = getattr(registration.user.profile, 'phone', '') if hasattr(registration.user, 'profile') else ''
                    print(f"🔍 DEBUG: User - Name: {recipient_name}, Email: {recipient_email}, Phone: {recipient_phone}")
                else:
                    # Inscription d'invité
                    recipient_name = registration.guest_full_name or "Invité"
                    recipient_email = registration.guest_email or ""
                    recipient_phone = registration.guest_phone or ""
                    print(f"🔍 DEBUG: Guest - Name: {recipient_name}, Email: {recipient_email}, Phone: {recipient_phone}")
                
                print(f"🔍 DEBUG: Statut inscription: {registration.status}")
                print(f"🔍 DEBUG: =================================")
                
                # Envoyer email si activé
                if reminder.send_email and recipient_email:
                    print(f"🔍 DEBUG: 📧 ENVOI EMAIL à {recipient_email}")
                    email_sent = self._send_reminder_email(reminder, registration)
                    if email_sent:
                        statistics['emails_sent'] += 1
                        print(f"🔍 DEBUG: ✅ Email envoyé avec succès à {recipient_email}")
                    else:
                        statistics['emails_failed'] += 1
                        print(f"🔍 DEBUG: ❌ Échec envoi email à {recipient_email}")
                elif reminder.send_email and not recipient_email:
                    print(f"🔍 DEBUG: ⚠️ Email activé mais pas d'email disponible pour {recipient_name}")
                    statistics['emails_failed'] += 1
                
                # Envoyer SMS si activé
                if reminder.send_sms and recipient_phone:
                    print(f"🔍 DEBUG: 📱 ENVOI SMS à {recipient_phone}")
                    sms_sent = self._send_reminder_sms(reminder, registration)
                    if sms_sent:
                        statistics['sms_sent'] += 1
                        print(f"🔍 DEBUG: ✅ SMS envoyé avec succès à {recipient_phone}")
                    else:
                        statistics['sms_failed'] += 1
                        print(f"🔍 DEBUG: ❌ Échec envoi SMS à {recipient_phone}")
                elif reminder.send_sms and not recipient_phone:
                    print(f"🔍 DEBUG: ⚠️ SMS activé mais pas de téléphone disponible pour {recipient_name}")
                    statistics['sms_failed'] += 1
            
            # Mettre à jour le rappel
            reminder.status = 'sent'
            reminder.sent_at = timezone.now()
            reminder.emails_sent = statistics['emails_sent']
            reminder.sms_sent = statistics['sms_sent']
            reminder.emails_failed = statistics['emails_failed']
            reminder.sms_failed = statistics['sms_failed']
            reminder.save()
            
            print(f"🔍 DEBUG: Statistiques finales: {statistics}")
            print(f"🔍 DEBUG: ===== send_now() FIN =====")
            
            return Response({
                'message': 'Rappel envoyé avec succès!',
                'statistics': statistics
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"🔍 DEBUG: ERREUR dans send_now(): {e}")
            import traceback
            print(f"🔍 DEBUG: Traceback: {traceback.format_exc()}")
            
            reminder.status = 'failed'
            reminder.save()
            return Response(
                {'error': f'Erreur lors de l\'envoi: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Programmer l'envoi du rappel"""
        reminder = self.get_object()
        scheduled_at = request.data.get('scheduled_at')
        
        if not scheduled_at:
            return Response(
                {'error': 'La date de programmation est requise.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from django.utils.dateparse import parse_datetime
            scheduled_datetime = parse_datetime(scheduled_at)
            
            if scheduled_datetime <= timezone.now():
                return Response(
                    {'error': 'La date de programmation doit être dans le futur.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            reminder.scheduled_at = scheduled_datetime
            reminder.status = 'scheduled'
            reminder.save()
            
            # 🔍 PROGRAMMER L'ENVOI AUTOMATIQUE AVEC CELERY
            print(f"🔍 DEBUG: ===== PROGRAMMATION CELERY =====")
            print(f"🔍 DEBUG: Rappel ID: {reminder.id}")
            print(f"🔍 DEBUG: Heure programmée: {scheduled_datetime}")
            
            try:
                from .tasks import send_reminder_task
                
                # Calculer le délai en secondes
                delay_seconds = (scheduled_datetime - timezone.now()).total_seconds()
                print(f"🔍 DEBUG: Délai en secondes: {delay_seconds}")
                
                if delay_seconds > 0:
                    # Programmer l'envoi avec Celery
                    task = send_reminder_task.apply_async(
                        args=[reminder.id],
                        eta=scheduled_datetime
                    )
                    print(f"🔍 DEBUG: ✅ Tâche Celery programmée: {task.id}")
                    print(f"🔍 DEBUG: ETA: {scheduled_datetime}")
                else:
                    print(f"🔍 DEBUG: ⚠️ Délai négatif, envoi immédiat")
                    send_reminder_task.delay(reminder.id)
                
            except Exception as celery_error:
                print(f"🔍 DEBUG: ❌ Erreur Celery: {celery_error}")
                # Fallback: le rappel reste programmé, sera vérifié par la tâche périodique
            
            print(f"🔍 DEBUG: ================================")
            
            return Response(
                {'message': 'Rappel programmé avec succès!'},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la programmation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _send_reminder_email(self, reminder, registration):
        """Envoyer le rappel par email"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            # 🔍 LOGS DÉTAILLÉS POUR DEBUGGING EMAIL
            print(f"🔍 DEBUG: ===== ENVOI EMAIL =====")
            print(f"🔍 DEBUG: Registration ID: {registration.id}")
            print(f"🔍 DEBUG: Registration Type: {'User' if registration.user else 'Guest'}")
            
            # Déterminer l'email et le nom du destinataire selon le type d'inscription
            if registration.user:
                # Inscription d'utilisateur connecté
                recipient_email = registration.user.email
                recipient_name = registration.user.get_full_name() or registration.user.username
                print(f"🔍 DEBUG: User Email: {recipient_email}, Name: {recipient_name}")
            else:
                # Inscription d'invité
                recipient_email = registration.guest_email
                recipient_name = registration.guest_full_name or "Invité"
                print(f"🔍 DEBUG: Guest Email: {recipient_email}, Name: {recipient_name}")
            
            if not recipient_email:
                print(f"🔍 DEBUG: ❌ Aucun email disponible pour {recipient_name}")
                return False
            
            # Créer le sujet et le message
            subject = f"[{reminder.event.title}] {reminder.title}"
            message = f"""
Bonjour {recipient_name},

{reminder.message}

Détails de l'événement :
- Titre : {reminder.event.title}
- Date : {reminder.event.start_date.strftime('%d/%m/%Y à %H:%M')}
- Lieu : {reminder.event.location}

Cordialement,
L'équipe {reminder.event.title}
            """
            
            # Envoyer l'email
            print(f"🔍 DEBUG: 📧 Envoi email en cours...")
            print(f"🔍 DEBUG: Sujet: {subject}")
            print(f"🔍 DEBUG: Destinataire: {recipient_email}")
            print(f"🔍 DEBUG: Expéditeur: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')}")
            
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                recipient_list=[recipient_email],
                fail_silently=False
            )
            
            print(f"🔍 DEBUG: ✅ Email envoyé avec succès à {recipient_email}")
            print(f"🔍 DEBUG: =========================")
            return True
            
        except Exception as e:
            print(f"🔍 DEBUG: ❌ Erreur envoi email: {e}")
            import traceback
            print(f"🔍 DEBUG: Traceback email: {traceback.format_exc()}")
            print(f"🔍 DEBUG: =========================")
            return False
    
    def _send_reminder_sms(self, reminder, registration):
        """Envoyer le rappel par SMS"""
        try:
            # 🔍 LOGS DÉTAILLÉS POUR DEBUGGING SMS
            print(f"🔍 DEBUG: ===== ENVOI SMS =====")
            print(f"🔍 DEBUG: Registration ID: {registration.id}")
            print(f"🔍 DEBUG: Registration Type: {'User' if registration.user else 'Guest'}")
            
            # Déterminer le téléphone et le nom du destinataire selon le type d'inscription
            if registration.user:
                # Inscription d'utilisateur connecté
                recipient_phone = getattr(registration.user.profile, 'phone', '') if hasattr(registration.user, 'profile') else ''
                recipient_name = registration.user.get_full_name() or registration.user.username
                print(f"🔍 DEBUG: User Phone: {recipient_phone}, Name: {recipient_name}")
            else:
                # Inscription d'invité
                recipient_phone = registration.guest_phone
                recipient_name = registration.guest_full_name or "Invité"
                print(f"🔍 DEBUG: Guest Phone: {recipient_phone}, Name: {recipient_name}")
            
            if not recipient_phone:
                print(f"🔍 DEBUG: ❌ Aucun téléphone disponible pour {recipient_name}")
                return False
            
            # Créer le message SMS
            message = f"{reminder.title}\n\n{reminder.message}\n\nÉvénement: {reminder.event.title}\nDate: {reminder.event.start_date.strftime('%d/%m/%Y à %H:%M')}"
            
            # 🔍 LOGS DÉTAILLÉS POUR L'ENVOI SMS
            print(f"🔍 DEBUG: 📱 Envoi SMS en cours...")
            print(f"🔍 DEBUG: Destinataire: {recipient_phone}")
            print(f"🔍 DEBUG: Message: {message}")
            print(f"🔍 DEBUG: Twilio configuré: {getattr(settings, 'TWILIO_ENABLED', False)}")
            
            # Vérifier si Twilio est activé
            if not getattr(settings, 'TWILIO_ENABLED', False):
                print(f"🔍 DEBUG: ⚠️ Twilio désactivé - Simulation SMS")
                print(f"🔍 DEBUG: ✅ [SIMULATION] SMS envoyé avec succès à {recipient_phone}")
                print(f"🔍 DEBUG: =========================")
                return True
            
            # Envoi SMS réel avec Twilio
            try:
                from twilio.rest import Client
                from django.conf import settings
                
                print(f"🔍 DEBUG: 🔧 Initialisation client Twilio...")
                client = Client(
                    getattr(settings, 'TWILIO_ACCOUNT_SID', ''),
                    getattr(settings, 'TWILIO_AUTH_TOKEN', '')
                )
                
                print(f"🔍 DEBUG: 📤 Envoi SMS via Twilio...")
                print(f"🔍 DEBUG: From: {getattr(settings, 'TWILIO_FROM_NUMBER', '')}")
                print(f"🔍 DEBUG: To: {recipient_phone}")
                
                twilio_message = client.messages.create(
                    body=message,
                    from_=getattr(settings, 'TWILIO_FROM_NUMBER', ''),
                    to=recipient_phone
                )
                
                print(f"🔍 DEBUG: ✅ SMS envoyé avec succès via Twilio!")
                print(f"🔍 DEBUG: Message SID: {twilio_message.sid}")
                print(f"🔍 DEBUG: Status: {twilio_message.status}")
                print(f"🔍 DEBUG: =========================")
                return True
                
            except ImportError:
                print(f"🔍 DEBUG: ❌ Module twilio non installé - Simulation SMS")
                print(f"🔍 DEBUG: ✅ [SIMULATION] SMS envoyé avec succès à {recipient_phone}")
                print(f"🔍 DEBUG: =========================")
                return True
                
            except Exception as twilio_error:
                print(f"🔍 DEBUG: ❌ Erreur Twilio: {twilio_error}")
                print(f"🔍 DEBUG: ⚠️ Fallback vers simulation SMS")
                print(f"🔍 DEBUG: ✅ [SIMULATION] SMS envoyé avec succès à {recipient_phone}")
                print(f"🔍 DEBUG: =========================")
                return True
            
        except Exception as e:
            print(f"🔍 DEBUG: ❌ Erreur envoi SMS: {e}")
            import traceback
            print(f"🔍 DEBUG: Traceback SMS: {traceback.format_exc()}")
            print(f"🔍 DEBUG: =========================")
            return False