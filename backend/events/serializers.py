from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, Category, Tag, EventRegistration, EventHistory


class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les utilisateurs"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    """Sérialiseur pour les catégories"""
    event_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_event_count(self, obj):
        return obj.event_set.count()


class TagSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les tags"""
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class EventRegistrationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les inscriptions aux événements"""
    user = UserSerializer(read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

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
        return obj.registrations.count()

    def get_confirmed_registration_count(self, obj):
        return obj.registrations.filter(status='confirmed').count()

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
    class Meta:
        model = EventRegistration
        fields = ['event', 'notes', 'special_requirements']
        read_only_fields = ['user', 'status', 'registered_at']

    def validate_event(self, value):
        """Validation de l'événement"""
        user = self.context['request'].user
        
        # Vérifier si l'utilisateur est déjà inscrit
        if EventRegistration.objects.filter(event=value, user=user).exists():
            raise serializers.ValidationError("Vous êtes déjà inscrit à cet événement.")
        
        # Vérifier si l'événement est complet
        if value.is_full:
            raise serializers.ValidationError("Cet événement est complet.")
        
        # Vérifier si l'événement est publié
        if value.status != 'published':
            raise serializers.ValidationError("Cet événement n'est pas encore publié.")
        
        # Vérifier si l'événement n'est pas passé
        if value.is_past:
            raise serializers.ValidationError("Cet événement est déjà terminé.")
        
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data) 