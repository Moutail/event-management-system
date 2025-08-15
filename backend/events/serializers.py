from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Event, Category, Tag, EventRegistration, EventHistory, TicketType


class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les utilisateurs"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer pour les catégories"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'icon', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    """Serializer pour les tags"""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']


class EventRegistrationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les inscriptions aux événements"""
    user = UserSerializer(read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)
    ticket_type_name = serializers.CharField(source='ticket_type.name', read_only=True)

    class Meta:
        model = EventRegistration
        fields = '__all__'
        read_only_fields = ['id', 'registered_at', 'updated_at', 'confirmed_at', 'cancelled_at']


class EventHistorySerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'historique des événements"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = EventHistory
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']


class EventSerializer(serializers.ModelSerializer):
    """Sérialiseur principal pour les événements"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    organizer = UserSerializer(read_only=True)
    registrations = EventRegistrationSerializer(many=True, read_only=True)
    ticket_types = serializers.SerializerMethodField()
    history = EventHistorySerializer(many=True, read_only=True)
    
    # Propriétés calculées
    is_full = serializers.BooleanField(read_only=True)
    available_places = serializers.IntegerField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    
    # Statistiques
    registration_count = serializers.SerializerMethodField()
    confirmed_registration_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = [
            'id', 'slug', 'created_at', 'updated_at', 'published_at',
            'current_registrations', 'organizer'
        ]

    def get_registration_count(self, obj):
        return obj.registrations.filter(status__in=['confirmed', 'attended']).count()

    def get_confirmed_registration_count(self, obj):
        return obj.registrations.filter(status='confirmed').count()

    def get_ticket_types(self, obj):
        return TicketTypeListSerializer(obj.ticket_types.all(), many=True).data

    def create(self, validated_data):
        print(f"DEBUG: EventSerializer.create - Données validées: {validated_data}")
        print(f"DEBUG: EventSerializer.create - Clés disponibles: {list(validated_data.keys())}")
        
        # Gérer les tags
        tag_ids = validated_data.pop('tag_ids', [])
        
        # Log spécifique pour l'image
        if 'poster' in validated_data:
            poster = validated_data['poster']
            print(f"DEBUG: EventSerializer.create - Image dans validated_data: {poster}")
            print(f"DEBUG: EventSerializer.create - Type d'image: {type(poster)}")
            if hasattr(poster, 'name'):
                print(f"DEBUG: EventSerializer.create - Nom d'image: {poster.name}")
        
        # Créer l'événement
        event = Event.objects.create(**validated_data)
        print(f"DEBUG: EventSerializer.create - Événement créé avec ID: {event.id}")
        print(f"DEBUG: EventSerializer.create - Image sauvegardée: {event.poster}")
        
        # Ajouter les tags
        if tag_ids:
            tags = Tag.objects.filter(id__in=tag_ids)
            event.tags.set(tags)
        
        return event

    def update(self, instance, validated_data):
        # Gérer les tags
        tag_ids = validated_data.pop('tag_ids', None)
        
        # Mettre à jour l'événement
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour les tags si fournis
        if tag_ids is not None:
            tags = Tag.objects.filter(id__in=tag_ids)
            instance.tags.set(tags)
        
        return instance

    def validate_website(self, value):
        """Validation et correction automatique de l'URL du site web"""
        if not value:
            return value
        
        # Si l'URL ne commence pas par http:// ou https://, ajouter https://
        if not value.startswith(('http://', 'https://')):
            value = 'https://' + value
        
        return value

    def validate(self, data):
        """Validation personnalisée"""
        print(f"DEBUG: EventSerializer.validate - Données reçues: {data}")
        print(f"DEBUG: EventSerializer.validate - Clés disponibles: {list(data.keys())}")
        
        # Validation de l'image
        if 'poster' in data:
            poster = data['poster']
            print(f"DEBUG: EventSerializer.validate - Image reçue: {poster}")
            print(f"DEBUG: EventSerializer.validate - Type d'image: {type(poster)}")
            if hasattr(poster, 'content_type'):
                print(f"DEBUG: EventSerializer.validate - Content-Type: {poster.content_type}")
            if hasattr(poster, 'size'):
                print(f"DEBUG: EventSerializer.validate - Taille: {poster.size}")
        
        # Vérifier que la date de fin est après la date de début
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError(
                    "La date de fin doit être postérieure à la date de début."
                )
        
        # Vérifier la cohérence des places
        if 'place_type' in data and 'max_capacity' in data:
            if data['place_type'] == 'limited' and not data['max_capacity']:
                raise serializers.ValidationError(
                    "La capacité maximale est requise pour les événements avec places limitées."
                )
            elif data['place_type'] == 'unlimited' and data['max_capacity']:
                raise serializers.ValidationError(
                    "La capacité maximale ne doit pas être définie pour les événements avec places illimitées."
                )
        
        # Vérifier la cohérence du prix
        if 'is_free' in data and 'price' in data:
            if data['is_free'] and data['price'] > 0:
                raise serializers.ValidationError(
                    "Le prix doit être 0 pour un événement gratuit."
                )
            elif not data['is_free'] and data['price'] <= 0:
                raise serializers.ValidationError(
                    "Le prix doit être supérieur à 0 pour un événement payant."
                )
        
        return data


class EventListSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la liste des événements (version simplifiée)"""
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    organizer = UserSerializer(read_only=True)
    
    # Propriétés calculées
    is_full = serializers.BooleanField(read_only=True)
    available_places = serializers.IntegerField(read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    registration_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'short_description', 'start_date', 'end_date',
            'location', 'price', 'is_free', 'poster', 'category', 'tags',
            'organizer', 'status', 'is_featured', 'is_full', 'available_places',
            'is_upcoming', 'is_ongoing', 'is_past', 'registration_count',
            'created_at', 'published_at'
        ]

    def get_registration_count(self, obj):
        return obj.registrations.count()


class EventDetailSerializer(EventSerializer):
    """Sérialiseur pour les détails d'un événement"""
    # Inclut tous les champs de EventSerializer plus des informations supplémentaires
    pass


class EventRegistrationCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour créer une inscription"""
    ticket_type_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    class Meta:
        model = EventRegistration
        fields = ['id', 'event', 'ticket_type_id', 'notes', 'special_requirements', 'price_paid', 'status']
        read_only_fields = ['id', 'user', 'status', 'registered_at', 'price_paid']

    def validate_event(self, value):
        """Validation de l'événement"""
        user = self.context['request'].user
        
        # Vérifier si l'utilisateur est déjà inscrit
        # Autoriser la réinscription si l'unique inscription existante est annulée
        if EventRegistration.objects.filter(event=value, user=user).exclude(status='cancelled').exists():
            raise serializers.ValidationError("Vous êtes déjà inscrit à cet événement.")
        
        # Interdire inscriptions si événement passé
        if value.end_date <= timezone.now():
            raise serializers.ValidationError("Cet événement est déjà passé.")
        
        # La logique de liste d'attente est gérée au moment de la création
        
        # Vérifier si l'événement est publié
        if value.status != 'published':
            raise serializers.ValidationError("Cet événement n'est pas encore publié.")
        
        # Vérifier si l'événement n'est pas passé
        if value.is_past:
            raise serializers.ValidationError("Cet événement est déjà terminé.")
        
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        ticket_type_id = validated_data.pop('ticket_type_id', None)
        ticket_type = None
        price_paid = 0

        # Réactiver une inscription annulée ou en attente non payée si elle existe (évite le blocage unique_together)
        existing = EventRegistration.objects.filter(event=validated_data['event'], user=user).first()
        if existing and existing.status not in ['cancelled'] and not (existing.status == 'pending' and existing.payment_status == 'unpaid'):
            # Déjà inscrit (actif) ou en attente avec paiement en cours
            raise serializers.ValidationError("Vous êtes déjà inscrit à cet événement.")
        # Marquer l'utilisateur
        validated_data['user'] = user
        if ticket_type_id:
            ticket_type = TicketType.objects.filter(id=ticket_type_id, event=validated_data['event']).first()
            if ticket_type is None:
                raise serializers.ValidationError("Type de billet invalide pour cet événement.")
            # Appliquer le prix effectif (réduction incluse le cas échéant)
            try:
                price_paid = ticket_type.effective_price
            except Exception:
                price_paid = ticket_type.price

            # Capacity check per ticket type
            if ticket_type.quantity is not None and ticket_type.sold_count >= ticket_type.quantity:
                # Put on waitlist
                validated_data['status'] = 'waitlisted'

        # Si une inscription annulée ou en attente non payée existe, la réactiver plutôt que créer une nouvelle
        if existing and (existing.status == 'cancelled' or (existing.status == 'pending' and existing.payment_status == 'unpaid')):
            registration = existing
            # reset champs
            registration.status = validated_data.get('status', 'pending')
            registration.notes = validated_data.get('notes', '')
            registration.special_requirements = validated_data.get('special_requirements', '')
            registration.payment_status = 'unpaid'
            registration.payment_provider = ''
            registration.payment_reference = ''
            registration.ticket_type = None
            registration.price_paid = 0
            registration.save()
        else:
            registration = super().create(validated_data)

        # Lier le type de billet et définir le montant
        if ticket_type:
            registration.ticket_type = ticket_type
            registration.price_paid = price_paid
            registration.save(update_fields=['ticket_type', 'price_paid'])
        else:
            # Si aucun type de billet sélectionné et que l'événement est payant,
            # appliquer le prix de l'événement
            event = registration.event
            if not event.is_free and (event.price or 0) > 0:
                registration.price_paid = event.price
                registration.save(update_fields=['price_paid'])

        # Vérification de la capacité générale de l'événement pour décider du statut final
        event = registration.event
        is_paid_amount = (registration.price_paid or 0) > 0
        
        # Vérifier si l'événement a atteint sa capacité maximale
        if registration.status != 'waitlisted':
            if event.place_type == 'limited' and event.max_capacity is not None:
                current_confirmed = event.registrations.filter(status__in=['confirmed', 'attended']).count()
                if current_confirmed >= event.max_capacity:
                    # Événement complet → mettre en liste d'attente
                    registration.status = 'waitlisted'
                    registration.save(update_fields=['status', 'updated_at'])

        if registration.status != 'waitlisted':
            if not is_paid_amount:
                # Gratuit → confirmer et réserver une place immédiatement
                registration.status = 'confirmed'
                registration.save(update_fields=['status', 'updated_at'])
                if event.place_type == 'limited' and event.max_capacity is not None:
                    if not existing or existing.status == 'cancelled':
                        event.current_registrations = min(event.max_capacity, (event.current_registrations or 0) + 1)
                        event.save(update_fields=['current_registrations'])
                # Incrémenter sold_count pour gratuit si un type de billet existe
                if ticket_type:
                    ticket_type.sold_count = ticket_type.sold_count + 1
                    ticket_type.save(update_fields=['sold_count'])
            else:
                # Payant → rester en pending, ne pas réserver ni incrémenter
                pass

        return registration


class TicketTypeSerializer(serializers.ModelSerializer):
    has_discount = serializers.BooleanField(read_only=True)
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    available_quantity = serializers.IntegerField(read_only=True, allow_null=True)
    class Meta:
        model = TicketType
        fields = '__all__'
        read_only_fields = ['id', 'sold_count', 'created_at', 'has_discount', 'effective_price', 'available_quantity']

    def validate(self, attrs):
        from decimal import Decimal, ROUND_HALF_UP
        price = attrs.get('price', getattr(self.instance, 'price', None)) or Decimal('0')
        is_active = attrs.get('is_discount_active', getattr(self.instance, 'is_discount_active', False))
        dprice = attrs.get('discount_price', getattr(self.instance, 'discount_price', None))
        dpercent = attrs.get('discount_percent', getattr(self.instance, 'discount_percent', None))

        if not is_active:
            attrs['discount_price'] = None
            attrs['discount_percent'] = None
            return attrs

        # Sanitize
        if dpercent is not None:
            try:
                dpercent = int(dpercent)
            except Exception:
                dpercent = None
        if dprice is not None:
            try:
                dprice = Decimal(str(dprice))
            except Exception:
                dprice = None

        if price <= 0:
            # Pas de réduction pour un prix nul
            attrs['is_discount_active'] = False
            attrs['discount_price'] = None
            attrs['discount_percent'] = None
            return attrs

        # Calcul bidirectionnel
        if dprice is not None and dpercent is None:
            # Calculer le pourcentage
            if dprice >= price:
                raise serializers.ValidationError({'discount_price': 'Le prix remisé doit être inférieur au prix.'})
            ratio = (price - dprice) / price
            dpercent = int((ratio * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        elif dpercent is not None and dprice is None:
            if dpercent <= 0 or dpercent >= 100:
                raise serializers.ValidationError({'discount_percent': 'La réduction (%) doit être entre 1 et 99.'})
            dprice = (price * (Decimal('1') - (Decimal(dpercent) / Decimal('100')))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        elif dpercent is not None and dprice is not None:
            # Vérifier la cohérence, sinon recalculer le pourcentage
            if dprice >= price:
                raise serializers.ValidationError({'discount_price': 'Le prix remisé doit être inférieur au prix.'})
            ratio = (price - dprice) / price
            calc_percent = int((ratio * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            dpercent = calc_percent
        else:
            # Aucun des deux fourni: désactiver la réduction
            attrs['is_discount_active'] = False
            attrs['discount_price'] = None
            attrs['discount_percent'] = None
            return attrs

        attrs['discount_price'] = dprice
        attrs['discount_percent'] = dpercent
        return attrs


class TicketTypeListSerializer(serializers.ModelSerializer):
    has_discount = serializers.BooleanField(read_only=True)
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    available_quantity = serializers.IntegerField(read_only=True, allow_null=True)
    class Meta:
        model = TicketType
        fields = ['id', 'name', 'price', 'discount_price', 'discount_percent', 'is_discount_active', 'effective_price', 'has_discount', 'quantity', 'is_vip', 'available_quantity', 'sale_start', 'sale_end']