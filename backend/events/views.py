from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .permissions import IsSuperAdmin
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum
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
from decimal import Decimal

try:
    from openpyxl import Workbook
except Exception:  # pragma: no cover
    Workbook = None

from .models import Event, Category, Tag, EventRegistration, EventHistory, TicketType, RefundRequest, UserProfile
from .serializers import (
    EventSerializer, EventListSerializer, EventDetailSerializer,
    CategorySerializer, TagSerializer, EventRegistrationSerializer,
    EventRegistrationCreateSerializer, EventHistorySerializer,
    TicketTypeSerializer
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

        # Par défaut, ne pas afficher les événements passés dans la liste publique
        # (la vue "my_events" reste complète pour l'organisateur)
        if getattr(self, 'action', None) == 'list' and not date_filter:
            queryset = queryset.filter(end_date__gte=now, status='published')
        
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

    def destroy(self, request, *args, **kwargs):
        """Autoriser la suppression uniquement pour l'organisateur (ou staff) et uniquement pour les événements passés."""
        event = self.get_object()
        if event.organizer != request.user and not request.user.is_staff:
            return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        if event.end_date >= timezone.now():
            return Response({"error": "Vous ne pouvez supprimer qu'un événement déjà passé."}, status=status.HTTP_400_BAD_REQUEST)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get', 'post'], url_path='ticket-types')
    def ticket_types(self, request, pk=None):
        """Lister ou créer des types de billets pour un événement"""
        event = self.get_object()
        if request.method == 'GET':
            serializer = TicketTypeSerializer(event.ticket_types.all(), many=True)
            return Response(serializer.data)
        # POST create (organizer only)
        if event.organizer != request.user:
            return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        data['event'] = event.id
        serializer = TicketTypeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch', 'delete'], url_path='ticket-types/(?P<tt_id>[^/.]+)')
    def ticket_type_detail(self, request, pk=None, tt_id=None):
        """Mettre à jour ou supprimer un type de billet (organisateur uniquement)."""
        event = self.get_object()
        if event.organizer != request.user and not request.user.is_staff:
            return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        tt = get_object_or_404(TicketType, id=tt_id, event=event)
        if request.method.lower() == 'delete':
            tt.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # patch
        serializer = TicketTypeSerializer(tt, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
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

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Liste des participants pour un événement (organisateur ou staff uniquement)."""
        event = self.get_object()
        if event.organizer != request.user and not request.user.is_staff:
            return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        regs = event.registrations.select_related('user', 'ticket_type').all()
        serializer = EventRegistrationSerializer(regs, many=True)
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
        # Statistiques personnelles de l'organisateur connecté
        user = request.user
        user_events = Event.objects.filter(organizer=user)
        total_events = user_events.count()
        published_events = user_events.filter(status='published').count()
        upcoming_events = user_events.filter(start_date__gt=timezone.now(), status='published').count()
        ongoing_events = user_events.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now(), status='published').count()

        # Total inscriptions (tous statuts confondus) sur mes événements
        total_registrations = EventRegistration.objects.filter(event__organizer=user).count()

        # Revenus générés (inscriptions payées MOINS les remboursements traités)
        total_revenue = EventRegistration.objects.filter(
            event__organizer=user,
            payment_status='paid'
        ).exclude(
            # Exclure les inscriptions qui ont un remboursement traité
            refund_request__status='processed'
        ).aggregate(total=Sum('price_paid')).get('total') or 0

        # Alternative: inclure aussi les inscriptions confirmées même si pas encore payées
        if total_revenue == 0:
            total_revenue = EventRegistration.objects.filter(
                event__organizer=user,
                status__in=['confirmed', 'attended', 'pending']
            ).exclude(
                # Exclure aussi ici les remboursements traités
                refund_request__status='processed'
            ).aggregate(total=Sum('price_paid')).get('total') or 0

        # Répartition par statut
        status_keys = [k for k, _ in Event.STATUS_CHOICES]
        status_distribution = {key: user_events.filter(status=key).count() for key in status_keys}

        # Répartition par catégorie
        categories = Category.objects.all()
        category_distribution = {}
        for cat in categories:
            count = user_events.filter(category=cat).count()
            if count:
                category_distribution[cat.name] = count
        if not category_distribution:
            category_distribution['Sans catégorie'] = user_events.filter(category__isnull=True).count()

        # Timeseries (30 derniers jours)
        start = timezone.now() - timedelta(days=29)
        daily_qs = EventRegistration.objects.filter(
            event__organizer=user,
            registered_at__date__gte=start.date()
        ).annotate(day=TruncDate('registered_at')).values('day').order_by('day')
        daily_counts = daily_qs.annotate(registrations=Count('id'))
        # Revenus par jour (confirmés/présents)
        daily_revenue_qs = EventRegistration.objects.filter(
            event__organizer=user,
            status__in=['confirmed', 'attended'],
            registered_at__date__gte=start.date()
        ).annotate(day=TruncDate('registered_at')).values('day').order_by('day').annotate(revenue=Sum('price_paid'))
        day_to_rev = {str(item['day']): float(item['revenue'] or 0) for item in daily_revenue_qs}
        timeseries = []
        for item in daily_counts:
            d = str(item['day'])
            timeseries.append({
                'date': d,
                'registrations': int(item['registrations'] or 0),
                'revenue': float(day_to_rev.get(d, 0)),
            })

        return Response({
            'total_events': total_events,
            'published_events': published_events,
            'upcoming_events': upcoming_events,
            'ongoing_events': ongoing_events,
            'total_registrations': total_registrations,
            'total_revenue': float(total_revenue),
            'status_distribution': status_distribution,
            'category_distribution': category_distribution,
            'timeseries': timeseries,
        })

    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        """Rapport d'un événement: inscrits, présents, taux de participation, revenus."""
        event = self.get_object()
        total = event.registrations.count()
        confirmed = event.registrations.filter(status='confirmed').count()
        attended = event.registrations.filter(status='attended').count()
        waitlisted = event.registrations.filter(status='waitlisted').count()
        revenue = event.registrations.filter(status__in=['confirmed', 'attended']).aggregate(total=Sum('price_paid')).get('total') or 0
        participation_rate = (attended / confirmed) * 100 if confirmed else 0
        return Response({
            'total_registrations': total,
            'confirmed': confirmed,
            'attended': attended,
            'waitlisted': waitlisted,
            'participation_rate': round(participation_rate, 2),
            'revenue': float(revenue),
        })

    @action(detail=True, methods=['get'])
    def export_registrations_csv(self, request, pk=None):
        """Exporter la liste des participants en CSV"""
        event = self.get_object()
        if event.organizer != request.user and not request.user.is_staff:
            return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="registrations_{event.id}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Username', 'Email', 'Status', 'Ticket', 'Price', 'Registered At'])
        for reg in event.registrations.select_related('user', 'ticket_type').all():
            writer.writerow([
                reg.user.username,
                reg.user.email,
                reg.status,
                getattr(reg.ticket_type, 'name', ''),
                str(reg.price_paid),
                reg.registered_at.strftime('%Y-%m-%d %H:%M')
            ])
        return response

    @action(detail=True, methods=['get'])
    def export_registrations_excel(self, request, pk=None):
        """Exporter la liste des participants en Excel"""
        event = self.get_object()
        if event.organizer != request.user and not request.user.is_staff:
            return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        if Workbook is None:
            return Response({"error": "openpyxl non installé"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        wb = Workbook()
        ws = wb.active
        ws.title = 'Inscriptions'
        ws.append(['Username', 'Email', 'Status', 'Ticket', 'Price', 'Registered At'])
        for reg in event.registrations.select_related('user', 'ticket_type').all():
            ws.append([
                reg.user.username,
                reg.user.email,
                reg.status,
                getattr(reg.ticket_type, 'name', ''),
                float(reg.price_paid or 0),
                reg.registered_at.strftime('%Y-%m-%d %H:%M')
            ])
        from io import BytesIO
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="registrations_{event.id}.xlsx"'
        return response

    @action(detail=True, methods=['get'])
    def waitlisted_registrations(self, request, pk=None):
        """Obtenir les inscriptions en attente pour un événement (organisateur ou staff uniquement)"""
        event = self.get_object()
        
        # Vérifier les permissions
        if event.organizer != request.user and not request.user.is_staff:
            return Response(
                {"error": "Vous n'êtes pas autorisé à voir ces inscriptions."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Récupérer les inscriptions en attente
        waitlisted = EventRegistration.objects.filter(
            event=event,
            status='waitlisted'
        ).order_by('registered_at')
        
        from .serializers import EventRegistrationSerializer
        serializer = EventRegistrationSerializer(waitlisted, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def refund_requests(self, request, pk=None):
        """Récupérer les demandes de remboursement pour un événement (organisateur ou staff)"""
        event = self.get_object()
        
        # Vérifier les permissions
        if event.organizer != request.user and not request.user.is_staff:
            return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        
        from .models import RefundRequest
        # Récupérer les demandes de remboursement
        refund_requests = RefundRequest.objects.filter(
            registration__event=event
        ).select_related('registration__user', 'registration__ticket_type', 'processed_by').order_by('-created_at')
        
        # Sérialiser les données
        data = []
        for refund_request in refund_requests:
            data.append({
                'id': refund_request.id,
                'registration': {
                    'id': refund_request.registration.id,
                    'user': {
                        'id': refund_request.registration.user.id,
                        'first_name': refund_request.registration.user.first_name,
                        'last_name': refund_request.registration.user.last_name,
                        'email': refund_request.registration.user.email,
                    }
                },
                'status': refund_request.status,
                'reason': refund_request.reason,
                'amount_paid': float(refund_request.amount_paid),
                'refund_percentage': refund_request.refund_percentage,
                'refund_amount': float(refund_request.refund_amount),
                'created_at': refund_request.created_at.isoformat(),
                'processed_at': refund_request.processed_at.isoformat() if refund_request.processed_at else None,
                'processed_by': {
                    'id': refund_request.processed_by.id,
                    'first_name': refund_request.processed_by.first_name,
                    'last_name': refund_request.processed_by.last_name,
                } if refund_request.processed_by else None,
                'stripe_refund_id': refund_request.stripe_refund_id,
                'auto_process_at': refund_request.auto_process_at.isoformat() if refund_request.auto_process_at else None,
                'expires_at': refund_request.expires_at.isoformat(),
            })
        
        return Response(data)

    @action(detail=True, methods=['get'])
    def export_registrations_pdf(self, request, pk=None):
        """Exporter la liste des participants en PDF (organisateur ou staff)."""
        event = self.get_object()
        if event.organizer != request.user and not request.user.is_staff:
            return Response({"error": "Non autorisé"}, status=status.HTTP_403_FORBIDDEN)
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from io import BytesIO
        except Exception:
            return Response({"error": "reportlab non installé"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50
        p.setFont("Helvetica-Bold", 14)
        p.drawString(40, y, f"Participants — {event.title}")
        y -= 30
        p.setFont("Helvetica", 10)
        p.drawString(40, y, f"Date: {event.start_date.strftime('%Y-%m-%d %H:%M')}  —  Lieu: {event.location}")
        y -= 20
        p.line(40, y, width - 40, y)
        y -= 20
        p.setFont("Helvetica-Bold", 10)
        p.drawString(40, y, "Utilisateur")
        p.drawString(220, y, "Email")
        p.drawString(380, y, "Statut")
        p.drawString(450, y, "Billet")
        y -= 15
        p.setFont("Helvetica", 10)

        for reg in event.registrations.select_related('user', 'ticket_type').all():
            if y < 60:
                p.showPage()
                y = height - 50
            p.drawString(40, y, f"{reg.user.username}")
            p.drawString(220, y, f"{reg.user.email}")
            p.drawString(380, y, f"{reg.status}")
            p.drawString(450, y, f"{getattr(reg.ticket_type, 'name', '')}")
            y -= 15

        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=f"participants_{event.id}.pdf")


class EventRegistrationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les inscriptions aux événements"""
    serializer_class = EventRegistrationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'event']
    ordering_fields = ['registered_at', 'updated_at']
    ordering = ['-registered_at']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        registration = serializer.save()

        # S'assurer que le QR est généré si confirmé (cas gratuit)
        try:
            registration.refresh_from_db()
        except Exception:
            pass

        # Envoyer confirmation pour inscriptions gratuites confirmées
        if (registration.price_paid or 0) == 0 and registration.status == 'confirmed':
            try:
                qr_url = None
                if registration.qr_code:
                    qr_url = request.build_absolute_uri(registration.qr_code.url)
                context = {
                    'user': registration.user,
                    'event': registration.event,
                    'qr_url': qr_url,
                }
                subject = f"Confirmation d'inscription - {registration.event.title}"
                text_body = render_to_string('emails/registration_confirmation.txt', context)
                html_body = render_to_string('emails/registration_confirmation.html', context)
                msg = EmailMultiAlternatives(subject, text_body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [registration.user.email])
                msg.attach_alternative(html_body, 'text/html')
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
            except Exception:
                pass

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        """Filtrer les inscriptions selon l'utilisateur"""
        user = self.request.user
        
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
        
        # 💰 NOUVEAU: Créer automatiquement une demande de remboursement si payée
        refund_request = None
        if registration.payment_status == 'paid' and registration.price_paid > 0:
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
                
                # Vérifier si les remboursements sont autorisés
                if policy.can_refund_now():
                    refund_percentage = policy.get_refund_percentage(0)
                    refund_amount = (registration.price_paid * refund_percentage) / 100
                    
                    now = timezone.now()
                    auto_process_at = None
                    if policy.mode in ['auto', 'mixed']:
                        auto_process_at = now + timezone.timedelta(hours=policy.auto_refund_delay_hours)
                    
                    expires_at = event.start_date - timezone.timedelta(hours=policy.cutoff_hours_before_event)
                    
                    # Créer la demande de remboursement
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
            context = { 'user': registration.user, 'event': event }
            text_body = render_to_string('emails/registration_cancelled.txt', context)
            html_body = render_to_string('emails/registration_cancelled.html', context)
            msg = EmailMultiAlternatives(subject, text_body, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [registration.user.email])
            msg.attach_alternative(html_body, 'text/html')
            msg.send(fail_silently=True)
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
                
                subject = f"Inscription approuvée - {event.title}"
                context = {
                    'user': registration.user,
                    'event': event,
                    'qr_url': qr_url,
                }
                message = render_to_string('emails/registration_approved.txt', context)
                html_message = render_to_string('emails/registration_approved.html', context)

                msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [registration.user.email])
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
                print(f"Email d'approbation envoyé à {registration.user.email}")
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
            context = {
                'user': registration.user,
                'event': event,
                'reason': reason,
            }
            message = render_to_string('emails/registration_rejected.txt', context)
            html_message = render_to_string('emails/registration_rejected.html', context)

            msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [registration.user.email])
            msg.attach_alternative(html_message, 'text/html')
            msg.send(fail_silently=False)  # Ne pas ignorer les erreurs
            print(f"Email de rejet envoyé à {registration.user.email}")
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
        
        action = request.data.get('action')  # 'approve' ou 'reject'
        
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
            context = {
                'user': registration.user,
                'event': event,
                'refund_request': refund_request,
                'refund_amount': refund_request.refund_amount,
            }
            
            from django.template.loader import render_to_string
            from django.core.mail import EmailMultiAlternatives
            from django.conf import settings
            
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
            context = {
                'user': registration.user,
                'event': event,
                'refund_request': refund_request,
                'reason': reason,
            }
            
            from django.template.loader import render_to_string
            from django.core.mail import EmailMultiAlternatives
            from django.conf import settings
            
            # Créer des templates simples inline car on n'a pas créé de templates spécifiques
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
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response({"error": "Stripe non configuré"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        registration = self.get_object()
        amount = int(float(registration.price_paid or 0) * 100)
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

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """Confirmer côté serveur qu'un PaymentIntent Stripe est payé et mettre à jour l'inscription.

        Body attendu: { payment_intent_id: "pi_..." }
        """
        if not getattr(settings, 'STRIPE_SECRET_KEY', None):
            return Response({"error": "Stripe non configuré"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        stripe.api_key = settings.STRIPE_SECRET_KEY

        registration = self.get_object()
        payment_intent_id = request.data.get('payment_intent_id')
        if not payment_intent_id:
            return Response({"error": "payment_intent_id manquant"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        except Exception as e:
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

        # Confirmer l'inscription si elle n'est pas en liste d'attente
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
                registration.save(update_fields=['payment_status', 'payment_provider', 'payment_reference', 'status', 'updated_at'])
                # Mettre à jour compteurs
                event.current_registrations = (event.current_registrations or 0) + 1
                event.save(update_fields=['current_registrations'])
                if registration.ticket_type:
                    tt = registration.ticket_type
                    tt.sold_count = tt.sold_count + 1
                    tt.save(update_fields=['sold_count'])
            else:
                # Paiement OK mais mettre en liste d'attente si pas de capacité
                registration.status = 'waitlisted'
                registration.save(update_fields=['payment_status', 'payment_provider', 'payment_reference', 'status', 'updated_at'])
        else:
            registration.save(update_fields=['payment_status', 'payment_provider', 'payment_reference', 'updated_at'])

        # Envoyer l'email approprié selon le statut de l'inscription
        try:
            registration.refresh_from_db()
            
            if registration.status == 'waitlisted':
                # Email d'attente de validation pour les inscriptions en liste d'attente
                subject = f"Inscription en attente de validation - {registration.event.title}"
                context = {
                    'user': registration.user,
                    'event': registration.event,
                }
                message = render_to_string('emails/registration_waitlisted.txt', context)
                html_message = render_to_string('emails/registration_waitlisted.html', context)
                
                msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [registration.user.email])
                msg.attach_alternative(html_message, 'text/html')
                msg.send(fail_silently=True)
                
            elif registration.status == 'confirmed':
                # Email de confirmation avec QR code pour les inscriptions confirmées
                qr_url = None
                if registration.qr_code:
                    qr_url = request.build_absolute_uri(registration.qr_code.url)
                subject = f"Confirmation d'inscription - {registration.event.title}"
                context = {
                    'user': registration.user,
                    'event': registration.event,
                    'qr_url': qr_url,
                }
                message = render_to_string('emails/registration_confirmation.txt', context)
                html_message = render_to_string('emails/registration_confirmation.html', context)

                msg = EmailMultiAlternatives(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', None), [registration.user.email])
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
                    except Exception:
                        pass

                msg.send(fail_silently=True)
        except Exception:
            pass

        return Response(self.get_serializer(registration).data)

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

        if mark_attended and registration.status == 'confirmed':
            registration.status = 'attended'
            registration.save()
        return Response({
            "valid": True,
            "registration_id": registration.id,
            "status": registration.status,
            "user": {
                "username": registration.user.username,
                "email": registration.user.email,
            },
            "event": {
                "id": registration.event.id,
                "title": registration.event.title,
            }
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

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    GET: Récupérer les informations de l'utilisateur connecté
    DELETE: Supprimer le compte de l'utilisateur connecté (et données associées selon on_delete)
    """
    try:
        user = request.user
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
            }
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'profile': profile_data
        })
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
        
        action = request.data.get('action')  # 'approve' ou 'reject'
        
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

@api_view(['GET', 'PUT', 'DELETE'])
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
    
    elif request.method == 'PUT':
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
            # Vérifier si la catégorie est utilisée
            if category.events.exists():
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

@api_view(['GET', 'PUT', 'DELETE'])
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
    
    elif request.method == 'PUT':
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
            # Vérifier si le tag est utilisé
            if tag.events.exists():
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
        data = request.data
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=data['username']).exists():
            return Response({'error': 'Ce nom d\'utilisateur existe déjà'}, status=400)
        
        if User.objects.filter(email=data['email']).exists():
            return Response({'error': 'Cet email existe déjà'}, status=400)
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        
        # Créer le profil utilisateur
        UserProfile.objects.create(
            user=user,
            role=data['role'],
            phone=data.get('phone', '')
        )
        
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
        
        return Response(user_data, status=201)
        
    except Exception as e:
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
            'max_participants': event.max_participants,
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
        
        # Notifier tous les participants inscrits
        _notify_participants_event_cancelled(event, reason)
        
        return Response({
            'message': 'Événement rejeté avec succès',
            'event_id': event.id,
            'old_status': old_status,
            'new_status': 'cancelled',
            'reason': reason
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
        
        # Vérifications de sécurité avant suppression
        if event.registrations.exists():
            return Response(
                {'error': 'Impossible de supprimer un événement avec des inscriptions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if event.status == 'published' and event.start_date > timezone.now():
            return Response(
                {'error': 'Impossible de supprimer un événement publié et à venir'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sauvegarder les informations avant suppression
        event_info = {
            'id': event.id,
            'title': event.title,
            'organizer': event.organizer.username,
            'created_at': event.created_at
        }
        
        # Supprimer l'événement
        event.delete()
        
        # Enregistrer l'action dans l'historique (si possible)
        try:
            EventHistory.objects.create(
                event_id=event_id,  # Utiliser l'ID même si l'événement est supprimé
                action='deleted',
                details=f"Événement supprimé définitivement par {request.user.username}",
                user=request.user
            )
        except:
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
                context = {
                    'event': event,
                    'user': registration.user,
                    'reason': reason,
                    'cancellation_date': timezone.now()
                }
                
                subject = f"❌ Événement annulé - {event.title}"
                text_body = render_to_string('emails/event_cancelled_participant.txt', context)
                html_body = render_to_string('emails/event_cancelled_participant.html', context)
                
                msg = EmailMultiAlternatives(
                    subject,
                    text_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [registration.user.email]
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send()
                
                print(f"📧 Email d'annulation envoyé à {registration.user.email}")
                
            except Exception as e:
                print(f"❌ Erreur envoi email d'annulation à {registration.user.email}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Erreur notification participants: {e}")