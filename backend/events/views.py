"""
Vues principales pour l'API des événements
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
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
import io
import logging

from .models import (
    Event, Category, Tag, EventRegistration, EventHistory, 
    UserProfile, RefundRequest, VirtualEvent, VirtualEventInteraction,
    CustomReminder, CustomReminderRecipient
)
from .serializers import (
    EventSerializer, CategorySerializer, TagSerializer,
    EventRegistrationSerializer, EventHistorySerializer,
    UserProfileSerializer, RefundRequestSerializer,
    VirtualEventSerializer, VirtualEventInteractionSerializer,
    CustomReminderSerializer
)
from .permissions import IsSuperAdmin, IsOrganizerOrSuperAdmin

logger = logging.getLogger(__name__)

# ViewSets principaux
class EventViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des événements"""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'tags', 'event_type', 'is_virtual', 'status']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'event_date', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            # Filtrer les événements publics pour les utilisateurs non authentifiés
            if not self.request.user.is_authenticated:
                queryset = queryset.filter(is_public=True)
        return queryset

    @action(detail=True, methods=['post'])
    def register(self, request, pk=None):
        """Inscription à un événement"""
        event = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Vérifier si déjà inscrit
        if EventRegistration.objects.filter(event=event, user=user).exists():
            return Response({'error': 'Already registered'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer l'inscription
        registration = EventRegistration.objects.create(
            event=event,
            user=user,
            registration_date=timezone.now()
        )
        
        serializer = EventRegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des catégories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class TagViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des tags"""
    queryset = Tag.objects.filter(is_active=True)
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class EventRegistrationViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des inscriptions"""
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        return queryset

class EventHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet pour l'historique des événements"""
    serializer_class = EventHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return EventHistory.objects.all()

class VirtualEventViewSet(viewsets.ModelViewSet):
    """ViewSet pour les événements virtuels"""
    serializer_class = VirtualEventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return VirtualEvent.objects.all()

class VirtualEventInteractionViewSet(viewsets.ModelViewSet):
    """ViewSet pour les interactions d'événements virtuels"""
    serializer_class = VirtualEventInteractionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return VirtualEventInteraction.objects.all()

class CustomReminderViewSet(viewsets.ModelViewSet):
    """ViewSet pour les rappels personnalisés"""
    serializer_class = CustomReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CustomReminder.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(created_by=self.request.user)
        return queryset

# Vues de fonction
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Inscription d'un nouvel utilisateur"""
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not all([username, email, password]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(user=user)
        
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Obtenir les informations de l'utilisateur actuel"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        
        # Structure attendue par le frontend
        user_data = {
            'id': request.user.id,
            'username': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'is_superuser': request.user.is_superuser,
            'is_staff': request.user.is_staff,
            'is_active': request.user.is_active,
            'date_joined': request.user.date_joined.isoformat() if request.user.date_joined else None,
            'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
            'profile': {
                'id': profile.id,
                'phone': profile.phone,
                'country': profile.country,
                'role': profile.role,
                'role_display': profile.get_role_display(),
                'status_approval': profile.status_approval,
                'status_approval_display': profile.get_status_approval_display(),
                'approval_date': profile.approval_date.isoformat() if profile.approval_date else None,
                'approved_by': profile.approved_by_id,
                'rejection_reason': profile.rejection_reason
            }
        }
        
        return Response(user_data)
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Changer le mot de passe"""
    try:
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
        
        validate_password(new_password)
        user.set_password(new_password)
        user.save()
        
        return Response({'message': 'Password changed successfully'})
    
    except ValidationError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Mettre à jour le profil utilisateur"""
    try:
        profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except UserProfile.DoesNotExist:
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def system_health_check(request):
    """Vérification de santé du système"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0.0'
    })

# Vues de remboursement
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_refund_view(request):
    """Traiter une demande de remboursement"""
    try:
        registration_id = request.data.get('registration_id')
        reason = request.data.get('reason', '')
        
        registration = get_object_or_404(EventRegistration, id=registration_id, user=request.user)
        
        refund_request = RefundRequest.objects.create(
            registration=registration,
            reason=reason,
            requested_by=request.user
        )
        
        serializer = RefundRequestSerializer(refund_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f"Error processing refund: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def approve_refund(request, refund_id):
    """Approuver un remboursement"""
    try:
        refund = get_object_or_404(RefundRequest, id=refund_id)
        refund.status = 'approved'
        refund.processed_by = request.user
        refund.processed_at = timezone.now()
        refund.save()
        
        return Response({'message': 'Refund approved'})
    
    except Exception as e:
        logger.error(f"Error approving refund: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def reject_refund(request, refund_id):
    """Rejeter un remboursement"""
    try:
        refund = get_object_or_404(RefundRequest, id=refund_id)
        refund.status = 'rejected'
        refund.processed_by = request.user
        refund.processed_at = timezone.now()
        refund.save()
        
        return Response({'message': 'Refund rejected'})
    
    except Exception as e:
        logger.error(f"Error rejecting refund: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Vues d'administration (simplifiées)
@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def super_admin_event_detail(request, event_id):
    """Détails d'un événement pour super admin"""
    event = get_object_or_404(Event, id=event_id)
    serializer = EventSerializer(event)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsSuperAdmin])
def super_admin_reject_event(request, event_id):
    """Rejeter un événement"""
    event = get_object_or_404(Event, id=event_id)
    event.status = 'rejected'
    event.save()
    return Response({'message': 'Event rejected'})

@api_view(['DELETE'])
@permission_classes([IsSuperAdmin])
def super_admin_delete_event(request, event_id):
    """Supprimer un événement"""
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return Response({'message': 'Event deleted'})

@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def super_admin_export_registrations_csv(request, event_id):
    """Exporter les inscriptions en CSV"""
    event = get_object_or_404(Event, id=event_id)
    registrations = EventRegistration.objects.filter(event=event)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="registrations_{event_id}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['User', 'Email', 'Registration Date', 'Status'])
    
    for reg in registrations:
        writer.writerow([
            reg.user.username,
            reg.user.email,
            reg.registration_date,
            reg.status
        ])
    
    return response

@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def super_admin_export_registrations_excel(request, event_id):
    """Exporter les inscriptions en Excel"""
    # Implémentation simplifiée - retourne CSV pour l'instant
    return super_admin_export_registrations_csv(request, event_id)

# Vues d'organisateur
@api_view(['GET'])
@permission_classes([IsOrganizerOrSuperAdmin])
def organizer_refunds_list(request):
    """Liste des remboursements pour l'organisateur"""
    user_events = Event.objects.filter(organizer=request.user)
    refunds = RefundRequest.objects.filter(registration__event__in=user_events)
    serializer = RefundRequestSerializer(refunds, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsOrganizerOrSuperAdmin])
def process_refund_request(request, refund_id):
    """Traiter une demande de remboursement"""
    refund = get_object_or_404(RefundRequest, id=refund_id)
    
    # Vérifier que l'organisateur peut traiter cette demande
    if refund.registration.event.organizer != request.user and not request.user.is_superuser:
        return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    action = request.data.get('action')
    if action == 'approve':
        refund.status = 'approved'
    elif action == 'reject':
        refund.status = 'rejected'
    else:
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    
    refund.processed_by = request.user
    refund.processed_at = timezone.now()
    refund.save()
    
    return Response({'message': f'Refund {action}d'})

@api_view(['POST'])
@permission_classes([IsOrganizerOrSuperAdmin])
def organizer_bulk_process_refunds(request):
    """Traitement en lot des remboursements"""
    refund_ids = request.data.get('refund_ids', [])
    action = request.data.get('action')
    
    if action not in ['approve', 'reject']:
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    
    refunds = RefundRequest.objects.filter(id__in=refund_ids)
    
    for refund in refunds:
        if refund.registration.event.organizer == request.user or request.user.is_superuser:
            refund.status = 'approved' if action == 'approve' else 'rejected'
            refund.processed_by = request.user
            refund.processed_at = timezone.now()
            refund.save()
    
    return Response({'message': f'{len(refunds)} refunds {action}d'})