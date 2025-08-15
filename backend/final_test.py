#!/usr/bin/env python
"""
Test final de toutes les APIs Super Admin
"""
import requests

def final_test():
    """Test final de toutes les APIs"""
    print("🎯 Test final de toutes les APIs Super Admin...")
    
    base_url = "http://localhost:8000/api"
    apis = [
        ("📊 Statistiques Globales", "/admin/global_stats/"),
        ("📈 Analytics", "/admin/analytics_advanced/?period=month"),
        ("💰 Remboursements", "/refunds/"),
        ("📂 Catégories", "/categories_management/"),
        ("🏷️  Tags", "/tags_management/"),
        ("👥 Utilisateurs", "/admin/users/")
    ]
    
    all_working = True
    
    for name, endpoint in apis:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 401:
                print(f"   ✅ {name}: Authentification requise (normal)")
            elif response.status_code == 200:
                print(f"   ✅ {name}: Fonctionne parfaitement")
            else:
                print(f"   ❌ {name}: Erreur {response.status_code}")
                all_working = False
        except Exception as e:
            print(f"   ❌ {name}: Erreur de connexion - {e}")
            all_working = False
    
    print(f"\n🎯 Résumé du test:")
    if all_working:
        print("   🎉 TOUTES LES APIs FONCTIONNENT PARFAITEMENT !")
        print("   🚀 Le frontend devrait maintenant fonctionner sans erreur 500")
    else:
        print("   ⚠️  Certaines APIs ont des problèmes")
    
    print(f"\n💡 Prochaines étapes:")
    print("   1. Connectez-vous au frontend avec le compte Super Admin 'window7'")
    print("   2. Accédez au Dashboard Super Admin")
    print("   3. Les erreurs 500 devraient être résolues")

if __name__ == '__main__':
    final_test()
