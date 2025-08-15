from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    EventViewSet, CategoryViewSet, TagViewSet,
    EventRegistrationViewSet, EventHistoryViewSet, register_user, get_current_user, change_password,
    process_refund_view, approve_refund, reject_refund, system_health_check,
    super_admin_event_detail, super_admin_reject_event, super_admin_delete_event
)
from .admin_views import SuperAdminViewSet, platform_analytics, pending_moderation

# Configuration du routeur
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'registrations', EventRegistrationViewSet, basename='registration')
router.register(r'history', EventHistoryViewSet, basename='history')
router.register(r'admin', SuperAdminViewSet, basename='admin')

urlpatterns = [
    path('', include(router.urls)),
    path('refund/<int:refund_request_id>/process/', process_refund_view, name='process_refund'),
    # Nouvelles routes pour les remboursements
    path('refunds/<int:refund_id>/approve/', approve_refund, name='approve_refund'),
    path('refunds/<int:refund_id>/reject/', reject_refund, name='reject_refund'),
    path('auth/register/', register_user, name='register'),
    path('auth/user/', get_current_user, name='get_current_user'),
    path('auth/change_password/', change_password, name='change_password'),
    # Super Admin routes
    path('admin/analytics/', platform_analytics, name='admin_analytics'),
    path('admin/moderation/', pending_moderation, name='admin_moderation'),
    
    # Nouvelles routes Super Admin
    path('admin/global_stats/', views.super_admin_global_stats, name='super_admin_global_stats'),
    path('admin/analytics_advanced/', views.super_admin_analytics, name='super_admin_analytics'),
    path('admin/users/', views.super_admin_users_list, name='super_admin_users_list'),
    path('admin/create_user/', views.super_admin_create_user, name='super_admin_create_user'),
    path('admin/manage_user/', views.super_admin_manage_user, name='super_admin_manage_user'),
    
    # Routes pour la gestion complète des événements
    path('admin/events/<int:event_id>/detail/', super_admin_event_detail, name='super_admin_event_detail'),
    path('admin/events/<int:event_id>/reject/', super_admin_reject_event, name='super_admin_reject_event'),
    path('admin/events/<int:event_id>/delete/', super_admin_delete_event, name='super_admin_delete_event'),
    
    # Routes pour catégories et tags
    path('categories_management/', views.categories_list, name='categories_list'),
    path('categories_management/<int:pk>/', views.category_detail, name='category_detail'),
    path('tags_management/', views.tags_list, name='tags_list'),
    path('tags_management/<int:pk>/', views.tag_detail, name='tag_detail'),
    
    # Route pour les remboursements
    path('refunds/', views.super_admin_refunds_list, name='super_admin_refunds_list'),
    
    # Route pour la santé du système
    path('admin/system_health/', system_health_check, name='system_health_check'),
] 