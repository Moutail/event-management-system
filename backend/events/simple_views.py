"""
Vues simplifiées pour éviter les erreurs 500
"""
from rest_framework import viewsets, status
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
