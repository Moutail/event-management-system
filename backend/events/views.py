from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
import csv
import stripe
from decimal import Decimal

try:
    from openpyxl import Workbook
except Exception:  # pragma: no cover
    Workbook = None

from .models import Event, Category, Tag, EventRegistration, EventHistory, TicketType
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
        # Empêcher la suppression standard côté API; gérer via statut si besoin
        return Response({"error": "Suppression non autorisée"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
        
        # Statistiques par catégorie
        category_stats = Category.objects.annotate(
            event_count=Count('event', filter=Q(event__organizer=user))
        ).values('name', 'event_count')

        # Revenus générés
        total_revenue = str(sum(
            reg.price_paid for reg in EventRegistration.objects.filter(status__in=['confirmed', 'attended'], event__organizer=user)
        ))
        
        return Response({
            'total_events': total_events,
            'published_events': published_events,
            'upcoming_events': upcoming_events,
            'ongoing_events': ongoing_events,
            'category_stats': category_stats,
            'total_revenue': total_revenue,
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
        
        previous_status = registration.status
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
            currency='eur',
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
                # Paiement OK mais rester en attente si pas de capacité
                registration.save(update_fields=['payment_status', 'payment_provider', 'payment_reference', 'updated_at'])
        else:
            registration.save(update_fields=['payment_status', 'payment_provider', 'payment_reference', 'updated_at'])

        # Envoyer un email de confirmation avec le QR code si disponible
        try:
            registration.refresh_from_db()
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

            try:
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