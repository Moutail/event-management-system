"""
Vues simplifiées pour éviter les erreurs 500
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
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
    
    def get_queryset(self):
        """Retourner seulement les événements publics pour éviter les erreurs"""
        try:
            queryset = Event.objects.filter(is_public=True, status='published')
            return queryset.order_by('-created_at')
        except Exception as e:
            # En cas d'erreur, retourner un queryset vide
            return Event.objects.none()
    
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
