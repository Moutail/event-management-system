from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings
import uuid
import io
from decimal import Decimal

try:
    import qrcode
    from PIL import Image
except Exception:  # pragma: no cover - handled by requirements
    qrcode = None
    Image = None


class Category(models.Model):
    """Modèle pour les catégories d'événements"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    color = models.CharField(max_length=7, default="#1976d2", verbose_name="Couleur")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icône")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Modèle pour les tags d'événements"""
    name = models.CharField(max_length=50, unique=True, verbose_name="Nom")
    color = models.CharField(max_length=7, default="#666666", verbose_name="Couleur")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    """Modèle principal pour les événements"""
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
        ('cancelled', 'Annulé'),
        ('completed', 'Terminé'),
        ('postponed', 'Reporté'),
    ]

    PLACE_TYPE_CHOICES = [
        ('limited', 'Places limitées'),
        ('unlimited', 'Places illimitées'),
    ]

    # Informations de base
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Description courte")
    
    # Dates et lieu
    start_date = models.DateTimeField(verbose_name="Date de début")
    end_date = models.DateTimeField(verbose_name="Date de fin")
    location = models.CharField(max_length=200, verbose_name="Lieu")
    address = models.TextField(blank=True, verbose_name="Adresse complète")
    
    # Gestion des places
    place_type = models.CharField(max_length=10, choices=PLACE_TYPE_CHOICES, default='unlimited', verbose_name="Type de places")
    max_capacity = models.PositiveIntegerField(null=True, blank=True, verbose_name="Capacité maximale")
    current_registrations = models.PositiveIntegerField(default=0, verbose_name="Inscriptions actuelles")
    
    # Prix
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prix")
    is_free = models.BooleanField(default=True, verbose_name="Gratuit")
    
    # Images et médias
    poster = models.ImageField(upload_to='events/posters/', blank=True, null=True, verbose_name="Affiche")
    banner = models.ImageField(upload_to='events/banners/', blank=True, null=True, verbose_name="Bannière")
    
    # Relations
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Catégorie")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Tags")
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Organisateur")
    
    # Statut et métadonnées
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Statut")
    is_featured = models.BooleanField(default=False, verbose_name="Événement en vedette")
    is_public = models.BooleanField(default=True, verbose_name="Public")
    
    # Informations de contact
    contact_email = models.EmailField(blank=True, verbose_name="Email de contact")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone de contact")
    website = models.URLField(blank=True, verbose_name="Site web")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Slug pour URL
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    
    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{uuid.uuid4().hex[:8]}-{self.title.lower().replace(' ', '-')}"
        
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        # Garder la cohérence prix/gratuité même si l'objet est créé hors serializer
        try:
            self.is_free = (Decimal(self.price or 0) == Decimal('0'))
        except Exception:
            pass
        
        super().save(*args, **kwargs)

    @property
    def is_full(self):
        """Vérifie si l'événement est complet"""
        if self.place_type == 'unlimited' or self.max_capacity is None:
            return False
        return self.current_registrations >= self.max_capacity

    @property
    def available_places(self):
        """Retourne le nombre de places disponibles"""
        if self.place_type == 'unlimited' or self.max_capacity is None:
            return None
        return max(0, self.max_capacity - self.current_registrations)

    @property
    def is_upcoming(self):
        """Vérifie si l'événement est à venir"""
        return self.start_date > timezone.now()

    @property
    def is_ongoing(self):
        """Vérifie si l'événement est en cours"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def is_past(self):
        """Vérifie si l'événement est passé"""
        return self.end_date < timezone.now()


class TicketType(models.Model):
    """Types de billets pour un événement (Gratuit, Standard, VIP, etc.)"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types', verbose_name="Événement")
    name = models.CharField(max_length=100, verbose_name="Nom du billet")
    description = models.TextField(blank=True, verbose_name="Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Prix")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name="Prix remisé")
    discount_percent = models.PositiveIntegerField(null=True, blank=True, verbose_name="Réduction (%)")
    is_discount_active = models.BooleanField(default=False, verbose_name="Réduction active")
    quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name="Quantité disponible")
    is_vip = models.BooleanField(default=False, verbose_name="Billet VIP")
    sale_start = models.DateTimeField(null=True, blank=True, verbose_name="Début de vente")
    sale_end = models.DateTimeField(null=True, blank=True, verbose_name="Fin de vente")
    sold_count = models.PositiveIntegerField(default=0, verbose_name="Billets vendus")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Type de billet"
        verbose_name_plural = "Types de billets"
        unique_together = ['event', 'name']
        ordering = ['price', 'name']

    def __str__(self) -> str:
        return f"{self.name} - {self.event.title}"

    @property
    def available_quantity(self):
        if self.quantity is None:
            return None
        return max(0, self.quantity - self.sold_count)

    @property
    def has_discount(self) -> bool:
        if not self.is_discount_active:
            return False
        if self.discount_price is not None:
            try:
                return self.discount_price < self.price
            except Exception:
                return False
        if self.discount_percent:
            return self.discount_percent > 0
        return False

    @property
    def effective_price(self):
        if not self.has_discount:
            return self.price
        if self.discount_price is not None:
            return self.discount_price
        if self.discount_percent:
            try:
                return (self.price or 0) * (Decimal('1') - (Decimal(self.discount_percent) / Decimal('100')))
            except Exception:
                return self.price
        return self.price


class EventRegistration(models.Model):
    """Modèle pour les inscriptions aux événements"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
        ('attended', 'Présent'),
        ('no_show', 'Absent'),
        ('waitlisted', 'Liste d\'attente'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations', verbose_name="Événement")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    ticket_type = models.ForeignKey('TicketType', on_delete=models.SET_NULL, null=True, blank=True, related_name='registrations', verbose_name="Type de billet")
    price_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name="Prix payé")
    payment_status = models.CharField(max_length=20, default='unpaid', choices=[
        ('unpaid', 'Non payé'),
        ('pending', 'En attente'),
        ('paid', 'Payé'),
        ('refunded', 'Remboursé')
    ], verbose_name="Statut de paiement")
    payment_provider = models.CharField(max_length=30, blank=True, verbose_name="Fournisseur de paiement")
    payment_reference = models.CharField(max_length=100, blank=True, verbose_name="Référence de paiement")
    qr_token = models.CharField(max_length=64, unique=True, blank=True, null=True)
    qr_code = models.ImageField(upload_to='tickets/qr/', blank=True, null=True, verbose_name="QR Code")
    
    # Informations supplémentaires
    notes = models.TextField(blank=True, verbose_name="Notes")
    special_requirements = models.TextField(blank=True, verbose_name="Besoins spéciaux")
    
    # Timestamps
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = ['event', 'user']
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

    def save(self, *args, **kwargs):
        if self.status == 'confirmed' and not self.confirmed_at:
            self.confirmed_at = timezone.now()
        elif self.status == 'cancelled' and not self.cancelled_at:
            self.cancelled_at = timezone.now()

        # Ensure a token exists
        if not self.qr_token:
            self.qr_token = uuid.uuid4().hex

        super().save(*args, **kwargs)

        # Generate QR after we have an ID and token
        if self.status in ['confirmed', 'attended'] and qrcode is not None and not self.qr_code:
            self._generate_and_store_qr()

    def _generate_and_store_qr(self):
        """Generate and store a QR code image for the registration."""
        qr_payload = {
            'event_id': self.event_id,
            'registration_id': self.id,
            'user_id': self.user_id,
            'token': self.qr_token,
        }
        data = f"EMSv1|{qr_payload['event_id']}|{qr_payload['registration_id']}|{qr_payload['user_id']}|{qr_payload['token']}"

        qr_img = qrcode.make(data)
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)

        from django.core.files.base import ContentFile
        filename = f"qr_{self.qr_token}.png"
        self.qr_code.save(filename, ContentFile(buffer.read()), save=False)
        super().save(update_fields=['qr_code'])


class EventHistory(models.Model):
    """Modèle pour l'historique des changements d'événements"""
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='history', verbose_name="Événement")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Utilisateur")
    action = models.CharField(max_length=100, verbose_name="Action")
    field_name = models.CharField(max_length=100, blank=True, verbose_name="Champ modifié")
    old_value = models.TextField(blank=True, verbose_name="Ancienne valeur")
    new_value = models.TextField(blank=True, verbose_name="Nouvelle valeur")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Historique"
        verbose_name_plural = "Historiques"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.event.title} - {self.action} - {self.timestamp}" 


class NotificationLog(models.Model):
    """Trace des notifications envoyées pour éviter les doublons."""
    TYPE_CHOICES = [
        ('reminder_1d', 'Rappel J-1'),
        ('reminder_day', 'Rappel jour J'),
        ('update', 'Mise à jour'),
        ('thank_you', 'Remerciement'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='notifications')
    registration = models.ForeignKey(EventRegistration, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['event', 'type']),
            models.Index(fields=['registration', 'type']),
        ]
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self) -> str:
        return f"{self.event_id} - {self.type} - {self.created_at:%Y-%m-%d %H:%M}"