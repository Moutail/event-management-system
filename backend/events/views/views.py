"""
Vues simplifiées pour les tests
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

# ViewSets simplifiés
class VirtualEventViewSet(viewsets.ModelViewSet):
    """ViewSet simplifié pour les événements virtuels"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return []

class VirtualEventInteractionViewSet(viewsets.ModelViewSet):
    """ViewSet simplifié pour les interactions"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return []

class EventViewSet(viewsets.ModelViewSet):
    """ViewSet simplifié pour les événements"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return []

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet simplifié pour les catégories"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return []

class TagViewSet(viewsets.ModelViewSet):
    """ViewSet simplifié pour les tags"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return []

class EventRegistrationViewSet(viewsets.ModelViewSet):
    """ViewSet simplifié pour les inscriptions"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return []

class EventHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet simplifié pour l'historique"""
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return []
