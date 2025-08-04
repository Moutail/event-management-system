#!/usr/bin/env python
"""
Script de test pour vérifier l'upload d'image
"""
import os
import sys
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth.models import User

# Configuration Django
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from events.models import Event, Category

def test_image_upload():
    """Test simple d'upload d'image"""
    print("=== Test d'upload d'image ===")
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    
    # Créer une catégorie de test
    category, created = Category.objects.get_or_create(
        name='Test Category',
        defaults={'description': 'Category for testing'}
    )
    
    # Créer un fichier image de test
    image_content = b'fake-image-content'
    image_file = SimpleUploadedFile(
        name='test_image.jpg',
        content=image_content,
        content_type='image/jpeg'
    )
    
    print(f"Fichier créé: {image_file.name}")
    print(f"Type: {image_file.content_type}")
    print(f"Taille: {image_file.size}")
    
    try:
        # Créer un événement avec l'image
        event = Event.objects.create(
            title='Test Event with Image',
            description='Test description',
            start_date='2025-01-01T10:00:00Z',
            end_date='2025-01-01T12:00:00Z',
            location='Test Location',
            organizer=user,
            category=category,
            poster=image_file
        )
        
        print(f"✅ Événement créé avec succès: {event.title}")
        print(f"✅ Image sauvegardée: {event.poster}")
        print(f"✅ Chemin de l'image: {event.poster.path if event.poster else 'Aucune'}")
        
        # Vérifier si le fichier existe
        if event.poster and os.path.exists(event.poster.path):
            print(f"✅ Fichier existe sur le disque: {event.poster.path}")
        else:
            print("❌ Fichier n'existe pas sur le disque")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        return False

if __name__ == '__main__':
    test_image_upload() 