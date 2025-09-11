"""
Sérialiseurs simplifiés pour éviter les erreurs 500
"""
from rest_framework import serializers
from .models import Event, Category, Tag, EventRegistration


class SimpleEventSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour les événements - évite les erreurs 500"""
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'short_description', 'event_type',
            'start_date', 'end_date', 'location', 'address', 'is_public',
            'status', 'max_capacity', 'current_registrations', 'price',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'current_registrations']


class SimpleCategorySerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour les catégories"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color']


class SimpleTagSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour les tags"""
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color']


class SimpleEventRegistrationSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour les inscriptions"""
    
    class Meta:
        model = EventRegistration
        fields = ['id', 'event', 'user', 'registration_date', 'status']
        read_only_fields = ['id', 'registration_date']
