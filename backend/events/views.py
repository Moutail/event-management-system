from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Event, Category, Tag, EventRegistration, EventHistory
from .serializers import (
    EventSerializer, EventListSerializer, EventDetailSerializer,
    CategorySerializer, TagSerializer, EventRegistrationSerializer,
    EventRegistrationCreateSerializer, EventHistorySerializer
)


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


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet pour les événements"""
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'tags', 'is_featured', 'is_free', 'place_type']
    search_fields = ['title', 'description', 'location', 'organizer__username']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'price', 'title']
    ordering = ['-start_date']

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
            print("DEBUG: EventViewSet.create - Aucun fichier reçu")
            
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        """Filtrer les événements selon les paramètres"""
        queryset = Event.objects.all()
        
        # Filtrer par statut si spécifié
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filtrer par date
        date_filter = self.request.query_params.get('date_filter', None)
        now = timezone.now()
        
        if date_filter == 'upcoming':
            queryset = queryset.filter(start_date__gt=now)
        elif date_filter == 'ongoing':
            queryset = queryset.filter(start_date__lte=now, end_date__gte=now)
        elif date_filter == 'past':
            queryset = queryset.filter(end_date__lt=now)
        elif date_filter == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            queryset = queryset.filter(start_date__gte=today_start, start_date__lt=today_end)
        elif date_filter == 'week':
            week_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)
            queryset = queryset.filter(start_date__gte=week_start, start_date__lt=week_end)
        elif date_filter == 'month':
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                month_end = now.replace(year=now.year + 1, month=1, day=1)
            else:
                month_end = now.replace(month=now.month + 1, day=1)
            queryset = queryset.filter(start_date__gte=month_start, start_date__lt=month_end)
        
        # Filtrer par prix
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        
        # Filtrer par lieu
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        # Filtrer par organisateur
        organizer = self.request.query_params.get('organizer', None)
        if organizer:
            queryset = queryset.filter(organizer__username__icontains=organizer)
        
        return queryset

    def get_serializer_class(self):
        """Choisir le bon sérialiseur selon l'action"""
        if self.action == 'list':
            return EventListSerializer
        elif self.action == 'retrieve':
            return EventDetailSerializer
        return EventSerializer

    def perform_create(self, serializer):
        """Créer un événement avec l'utilisateur connecté comme organisateur"""
        print(f"DEBUG: perform_create - Données reçues: {self.request.data}")
        print(f"DEBUG: perform_create - Type de données: {type(self.request.data)}")
        print(f"DEBUG: perform_create - Clés disponibles: {list(self.request.data.keys()) if hasattr(self.request.data, 'keys') else 'N/A'}")
        print(f"DEBUG: perform_create - FILES: {self.request.FILES}")
        print(f"DEBUG: perform_create - Utilisateur: {self.request.user.username}")
        print(f"DEBUG: perform_create - Serializer validé: {serializer.validated_data}")
        
        # Log spécifique pour l'image
        if 'poster' in self.request.FILES:
            poster_file = self.request.FILES['poster']
            print(f"DEBUG: perform_create - Image trouvée: {poster_file.name}")
            print(f"DEBUG: perform_create - Type d'image: {poster_file.content_type}")
            print(f"DEBUG: perform_create - Taille d'image: {poster_file.size}")
        else:
            print("DEBUG: perform_create - Aucune image trouvée dans request.FILES")
            
        event = serializer.save(organizer=self.request.user)
        print(f"DEBUG: perform_create - Événement créé: {event.title}")
        print(f"DEBUG: perform_create - Image sauvegardée: {event.poster}")
        return event

    def perform_update(self, serializer):
        """Mettre à jour un événement et enregistrer l'historique"""
        old_instance = self.get_object()
        serializer.save()
        
        # Enregistrer l'historique des changements
        EventHistory.objects.create(
            event=serializer.instance,
            user=self.request.user,
            action="Mise à jour",
            field_name="Événement modifié",
            old_value=str(old_instance),
            new_value=str(serializer.instance)
        )

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Dupliquer un événement"""
        event = self.get_object()
        
        # Créer une copie de l'événement
        event.pk = None
        event.title = f"{event.title} (Copie)"
        event.status = 'draft'
        event.start_date = timezone.now() + timedelta(days=7)
        event.end_date = timezone.now() + timedelta(days=7, hours=2)
        event.current_registrations = 0
        event.organizer = request.user
        event.save()
        
        # Copier les tags
        original_tags = Event.objects.get(pk=pk).tags.all()
        event.tags.set(original_tags)
        
        serializer = self.get_serializer(event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publier un événement"""
        event = self.get_object()
        
        if event.organizer != request.user:
            return Response(
                {"error": "Vous n'êtes pas autorisé à publier cet événement."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        event.status = 'published'
        event.published_at = timezone.now()
        event.save()
        
        # Enregistrer l'historique
        EventHistory.objects.create(
            event=event,
            user=request.user,
            action="Publication",
            field_name="Statut",
            old_value="draft",
            new_value="published"
        )
        
        serializer = self.get_serializer(event)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler un événement"""
        event = self.get_object()
        
        if event.organizer != request.user:
            return Response(
                {"error": "Vous n'êtes pas autorisé à annuler cet événement."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        event.status = 'cancelled'
        event.save()
        
        # Enregistrer l'historique
        EventHistory.objects.create(
            event=event,
            user=request.user,
            action="Annulation",
            field_name="Statut",
            old_value=event.status,
            new_value="cancelled"
        )
        
        serializer = self.get_serializer(event)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Récupérer les événements en vedette"""
        events = self.get_queryset().filter(is_featured=True, status='published')
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Récupérer les événements à venir"""
        events = self.get_queryset().filter(
            start_date__gt=timezone.now(),
            status='published'
        )
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ongoing(self, request):
        """Récupérer les événements en cours"""
        now = timezone.now()
        events = self.get_queryset().filter(
            start_date__lte=now,
            end_date__gte=now,
            status='published'
        )
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_events(self, request):
        """Récupérer les événements de l'utilisateur connecté"""
        events = self.get_queryset().filter(organizer=request.user)
        serializer = EventListSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Récupérer les statistiques des événements"""
        total_events = Event.objects.count()
        published_events = Event.objects.filter(status='published').count()
        upcoming_events = Event.objects.filter(
            start_date__gt=timezone.now(),
            status='published'
        ).count()
        ongoing_events = Event.objects.filter(
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
            status='published'
        ).count()
        
        # Statistiques par catégorie
        category_stats = Category.objects.annotate(
            event_count=Count('event')
        ).values('name', 'event_count')
        
        return Response({
            'total_events': total_events,
            'published_events': published_events,
            'upcoming_events': upcoming_events,
            'ongoing_events': ongoing_events,
            'category_stats': category_stats,
        })


class EventRegistrationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les inscriptions aux événements"""
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'event']
    ordering_fields = ['registered_at', 'updated_at']
    ordering = ['-registered_at']

    def get_queryset(self):
        """Filtrer les inscriptions selon l'utilisateur"""
        return EventRegistration.objects.filter(user=self.request.user)

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
        
        registration.status = 'cancelled'
        registration.save()
        
        # Mettre à jour le compteur d'inscriptions de l'événement
        event = registration.event
        event.current_registrations = max(0, event.current_registrations - 1)
        event.save()
        
        serializer = self.get_serializer(registration)
        return Response(serializer.data)

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
    Enregistrement d'un nouvel utilisateur
    """
    try:
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        # Validation des champs requis
        if not username or not email or not password:
            return Response({
                'error': 'Tous les champs sont requis'
            }, status=status.HTTP_400_BAD_REQUEST)

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

        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        return Response({
            'message': 'Utilisateur créé avec succès',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'error': 'Erreur lors de la création de l\'utilisateur',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Récupérer les informations de l'utilisateur connecté
    """
    try:
        user = request.user
        print(f"DEBUG: Utilisateur connecté: {user.username}")  # Debug log
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        })
    except Exception as e:
        print(f"DEBUG: Erreur dans get_current_user: {str(e)}")  # Debug log
        return Response({
            'error': 'Erreur lors de la récupération du profil',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 