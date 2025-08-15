#!/usr/bin/env python
"""
Test de l'erreur 500 sur global_stats
"""
import requests
import json

def test_global_stats_error():
    """Test de l'endpoint global_stats pour identifier l'erreur 500"""
    print("🔍 TEST DE L'ERREUR 500 SUR GLOBAL_STATS")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    endpoint = "/admin/global_stats/"
    
    print(f"🌐 Test de l'endpoint: {base_url}{endpoint}")
    
    try:
        # Test 1: Sans authentification (devrait retourner 401)
        print("\n1. 🔒 TEST SANS AUTHENTIFICATION")
        print("-" * 40)
        
        response = requests.get(f"{base_url}{endpoint}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 500:
            print("❌ ERREUR 500 DÉTECTÉE!")
            print("🔍 Détails de l'erreur:")
            try:
                error_data = response.json()
                print(f"   - Type: {error_data.get('type', 'N/A')}")
                print(f"   - Message: {error_data.get('message', 'N/A')}")
                print(f"   - Trace: {error_data.get('trace', 'N/A')}")
            except:
                print(f"   - Contenu brut: {response.text}")
        elif response.status_code == 401:
            print("✅ 401 attendu (authentification requise)")
        else:
            print(f"⚠️ Status inattendu: {response.status_code}")
        
        # Test 2: Avec token factice (devrait retourner 401 ou 500)
        print("\n2. 🔑 TEST AVEC TOKEN FACTICE")
        print("-" * 40)
        
        headers = {
            'Authorization': 'Bearer fake_token_123',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{base_url}{endpoint}", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 500:
            print("❌ ERREUR 500 DÉTECTÉE AVEC TOKEN!")
            print("🔍 Détails de l'erreur:")
            try:
                error_data = response.json()
                print(f"   - Type: {error_data.get('type', 'N/A')}")
                print(f"   - Message: {error_data.get('message', 'N/A')}")
                print(f"   - Trace: {error_data.get('trace', 'N/A')}")
            except:
                print(f"   - Contenu brut: {response.text}")
        
        # Test 3: Test des autres endpoints admin
        print("\n3. 🔍 TEST DES AUTRES ENDPOINTS ADMIN")
        print("-" * 40)
        
        other_endpoints = [
            "/admin/all_users/",
            "/admin/all_events/",
            "/admin/moderation/",
            "/admin/analytics_advanced/"
        ]
        
        for ep in other_endpoints:
            try:
                response = requests.get(f"{base_url}{ep}")
                print(f"✅ {ep}: {response.status_code}")
            except Exception as e:
                print(f"❌ {ep}: Erreur - {str(e)}")
        
        print("\n4. 📊 ANALYSE DE L'ERREUR")
        print("-" * 40)
        
        if response.status_code == 500:
            print("🔍 L'erreur 500 persiste sur global_stats")
            print("💡 Causes possibles:")
            print("   - Problème de base de données")
            print("   - Erreur dans le code Python")
            print("   - Problème de configuration")
            print("   - Exception non gérée dans la vue")
            
            print("\n🔧 Actions recommandées:")
            print("   1. Vérifier les logs du serveur Django")
            print("   2. Tester l'endpoint en mode debug")
            print("   3. Vérifier la connectivité base de données")
            print("   4. Tester avec un utilisateur authentifié")
        else:
            print("✅ Aucune erreur 500 détectée")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("💡 Vérifiez que le serveur Django est démarré")
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")

if __name__ == '__main__':
    test_global_stats_error()
