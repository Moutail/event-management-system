#!/usr/bin/env python
"""
Script de diagnostic pour l'API utilisateur
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_management.settings')
django.setup()

from django.contrib.auth.models import User
from events.models import UserProfile
from events.serializers import UserProfileSerializer
from rest_framework.test import APIClient
import json

def debug_user_api():
    print("🔍 DIAGNOSTIC API UTILISATEUR")
    print("=" * 50)
    
    # 1. Vérifier l'utilisateur admin
    try:
        admin_user = User.objects.get(username='admin')
        print(f"✅ Utilisateur admin trouvé: {admin_user.username}")
        print(f"   - ID: {admin_user.id}")
        print(f"   - Email: {admin_user.email}")
        print(f"   - is_superuser: {admin_user.is_superuser}")
        print(f"   - is_staff: {admin_user.is_staff}")
        print(f"   - is_active: {admin_user.is_active}")
    except User.DoesNotExist:
        print("❌ Utilisateur admin non trouvé")
        return
    
    # 2. Vérifier le profil admin
    try:
        admin_profile = UserProfile.objects.get(user=admin_user)
        print(f"✅ Profil admin trouvé: {admin_profile}")
        print(f"   - ID: {admin_profile.id}")
        print(f"   - Role: {admin_profile.role}")
        print(f"   - Phone: {admin_profile.phone}")
        print(f"   - Country: {admin_profile.country}")
        print(f"   - Status: {admin_profile.status_approval}")
    except UserProfile.DoesNotExist:
        print("❌ Profil admin non trouvé")
        return
    
    # 3. Tester le sérialiseur
    print("\n🔍 TEST DU SÉRIALISEUR")
    print("-" * 30)
    serializer = UserProfileSerializer(admin_profile)
    serialized_data = serializer.data
    print("Données sérialisées:")
    print(json.dumps(serialized_data, indent=2, ensure_ascii=False))
    
    # 4. Tester l'API directement
    print("\n🔍 TEST DE L'API /auth/user/")
    print("-" * 30)
    
    # Créer un token pour l'utilisateur admin
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)
    
    print(f"Token généré: {access_token[:50]}...")
    
    # Tester l'API
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    response = client.get('/api/auth/user/')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("Réponse API:")
        print(json.dumps(response.data, indent=2, ensure_ascii=False))
    else:
        print(f"Erreur API: {response.data}")
    
    # 5. Vérifier la structure attendue par le frontend
    print("\n🔍 STRUCTURE ATTENDUE PAR LE FRONTEND")
    print("-" * 40)
    print("Le frontend s'attend à recevoir:")
    print("- user.username")
    print("- user.email") 
    print("- user.is_superuser")
    print("- user.is_staff")
    print("- user.profile.role")
    print("- user.profile.phone")
    print("- user.profile.country")
    
    # 6. Problème identifié
    print("\n❌ PROBLÈME IDENTIFIÉ")
    print("-" * 25)
    print("L'API /auth/user/ retourne seulement le UserProfile")
    print("Mais le frontend s'attend à recevoir l'objet User complet")
    print("avec les champs user.* et profile.*")

if __name__ == "__main__":
    debug_user_api()
