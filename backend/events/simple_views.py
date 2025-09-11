"""
Vues simplifiées pour éviter les erreurs 500
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from .models import Event, Category, Tag, EventRegistration
from .simple_serializers import (
    SimpleEventSerializer, SimpleCategorySerializer, 
    SimpleTagSerializer, SimpleEventRegistrationSerializer
)


class SimpleEventViewSet(viewsets.ModelViewSet):
    """ViewSet simplifié pour les événements - évite les erreurs 500"""
    queryset = Event.objects.all()
    serializer_class = SimpleEventSerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        """
        Instancie et retourne la liste des permissions que cette vue nécessite.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Retourner seulement les événements publics pour éviter les erreurs"""
        try:
            if self.action == 'list':
                queryset = Event.objects.filter(is_public=True, status='published')
            else:
                queryset = Event.objects.all()
            return queryset.order_by('-created_at')
        except Exception as e:
            # En cas d'erreur, retourner un queryset vide
            return Event.objects.none()
    
    def perform_create(self, serializer):
        """Définir l'organisateur lors de la création d'un événement"""
        if self.request.user.is_authenticated:
            serializer.save(organizer=self.request.user)
        else:
            return Response(
                {'error': 'Authentication required to create events'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    def list(self, request, *args, **kwargs):
        """Liste des événements avec gestion d'erreur"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des événements: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def my_events(self, request):
        """Récupérer les événements de l'utilisateur connecté"""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            events = Event.objects.filter(organizer=request.user).order_by('-created_at')
            serializer = SimpleEventSerializer(events, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération de vos événements: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publier un événement"""
        event = self.get_object()
        
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if event.organizer != request.user:
            return Response({'error': 'Vous ne pouvez publier que vos propres événements'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            event.status = 'published'
            event.save()
            serializer = SimpleEventSerializer(event)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la publication: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def ticket_types(self, request, pk=None):
        """Récupérer les types de billets d'un événement"""
        event = self.get_object()
        
        try:
            from .models import TicketType
            ticket_types = TicketType.objects.filter(event=event)
            # Créer un sérialiseur simple pour les types de billets
            data = []
            for ticket_type in ticket_types:
                data.append({
                    'id': ticket_type.id,
                    'name': ticket_type.name,
                    'price': float(ticket_type.price),
                    'quantity': ticket_type.quantity,
                    'sold_count': ticket_type.sold_count,
                    'available_quantity': ticket_type.available_quantity if hasattr(ticket_type, 'available_quantity') else (ticket_type.quantity - ticket_type.sold_count) if ticket_type.quantity else None,
                    'is_available': ticket_type.is_available if hasattr(ticket_type, 'is_available') else True
                })
            return Response(data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des types de billets: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def session_types(self, request, pk=None):
        """Récupérer les types de sessions d'un événement"""
        event = self.get_object()
        
        try:
            from .models import SessionType
            session_types = SessionType.objects.filter(event=event)
            # Créer un sérialiseur simple pour les types de sessions
            data = []
            for session_type in session_types:
                data.append({
                    'id': session_type.id,
                    'name': session_type.name,
                    'description': session_type.description,
                    'start_time': session_type.start_time,
                    'end_time': session_type.end_time,
                    'max_participants': session_type.max_participants,
                    'current_participants': session_type.current_participants
                })
            return Response(data)
        except Exception as e:
            return Response(
                {'error': f'Erreur lors de la récupération des types de sessions: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SimpleCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet simplifié pour les catégories"""
    queryset = Category.objects.all()
    serializer_class = SimpleCategorySerializer
    permission_classes = [AllowAny]


class SimpleTagViewSet(viewsets.ModelViewSet):
    """ViewSet simplifié pour les tags"""
    queryset = Tag.objects.all()
    serializer_class = SimpleTagSerializer
    permission_classes = [AllowAny]


class SimpleEventRegistrationViewSet(viewsets.ModelViewSet):
    """ViewSet simplifié pour les inscriptions"""
    queryset = EventRegistration.objects.all()
    serializer_class = SimpleEventRegistrationSerializer
    permission_classes = [AllowAny]
