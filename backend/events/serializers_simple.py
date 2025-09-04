"""
Sérialiseurs simplifiés pour les tests
"""
from rest_framework import serializers

# Sérialiseurs de base
class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()

class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField()
    color = serializers.CharField()
    icon = serializers.CharField()
    is_active = serializers.BooleanField()

class TagSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    color = serializers.CharField()
    is_active = serializers.BooleanField()

class VirtualEventSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    platform = serializers.CharField()
    meeting_id = serializers.CharField()
    meeting_password = serializers.CharField()
    meeting_url = serializers.URLField()
    auto_record = serializers.BooleanField()
    allow_chat = serializers.BooleanField()
    allow_screen_sharing = serializers.BooleanField()
    waiting_room = serializers.BooleanField()
    recording_url = serializers.URLField()
    recording_available = serializers.BooleanField()
    recording_expires_at = serializers.DateTimeField()
    access_instructions = serializers.CharField()
    technical_requirements = serializers.CharField()

class VirtualEventInteractionSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    event = serializers.IntegerField()
    user = UserSerializer(read_only=True)
    interaction_type = serializers.CharField()
    content = serializers.CharField()
    rating = serializers.IntegerField()
    ip_address = serializers.IPAddressField()
    user_agent = serializers.CharField()

class EventRegistrationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    event = serializers.IntegerField()
    user = UserSerializer(read_only=True)
    status = serializers.CharField()
    ticket_type = serializers.IntegerField()
    price_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_status = serializers.CharField()
    qr_token = serializers.CharField()
    virtual_access_code = serializers.CharField()
    virtual_access_sent = serializers.BooleanField()

class EventSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    description = serializers.CharField()
    event_type = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    location = serializers.CharField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_free = serializers.BooleanField()
    status = serializers.CharField()
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    organizer = UserSerializer(read_only=True)
    registrations = EventRegistrationSerializer(many=True, read_only=True)
