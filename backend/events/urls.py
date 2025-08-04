from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EventViewSet, CategoryViewSet, TagViewSet,
    EventRegistrationViewSet, EventHistoryViewSet, register_user, get_current_user
)

# Configuration du routeur
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'registrations', EventRegistrationViewSet, basename='registration')
router.register(r'history', EventHistoryViewSet, basename='history')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', register_user, name='register'),
    path('auth/user/', get_current_user, name='get_current_user'),
] 