"""
URLs simplifiés pour les tests
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_simple

# Configuration du routeur simplifié
router = DefaultRouter()
router.register(r'events', views_simple.EventViewSet, basename='event')
router.register(r'categories', views_simple.CategoryViewSet, basename='category')
router.register(r'tags', views_simple.TagViewSet, basename='tag')
router.register(r'registrations', views_simple.EventRegistrationViewSet, basename='registration')
router.register(r'history', views_simple.EventHistoryViewSet, basename='history')
router.register(r'virtual-events', views_simple.VirtualEventViewSet, basename='virtual_event')
router.register(r'virtual-interactions', views_simple.VirtualEventInteractionViewSet, basename='virtual_interaction')

urlpatterns = [
    path('', include(router.urls)),
    # Route de test simple
    path('test/', lambda request: None, name='test_connection'),
]
