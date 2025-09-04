#!/usr/bin/env python
"""
🔑 Script de configuration des clés API pour les modèles IA
"""

import os
from pathlib import Path

def setup_ai_keys():
    """Configure les clés API pour les modèles IA"""
    print("🔑 Configuration des clés API pour les modèles IA")
    print("=" * 60)
    
    # Vérifier si le fichier .env existe
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ Fichier .env trouvé")
        print("📝 Vérification des clés API...")
        
        # Vérifier les clés existantes
        keys = {
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
            'MISTRAL_API_KEY': os.getenv('MISTRAL_API_KEY'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')
        }
        
        print("\n🔍 État des clés API :")
        for key_name, key_value in keys.items():
            if key_value:
                print(f"   ✅ {key_name}: {'*' * 10}...{key_value[-4:]}")
            else:
                print(f"   ❌ {key_name}: Non configurée")
        
        # Compter les clés configurées
        configured_keys = sum(1 for key in keys.values() if key)
        print(f"\n📊 Résumé : {configured_keys}/3 clés configurées")
        
        if configured_keys == 0:
            print("\n⚠️ Aucune clé API configurée")
            print("💡 Le système utilisera le mode fallback (templates)")
        elif configured_keys < 3:
            print(f"\n⚠️ {3 - configured_keys} clé(s) manquante(s)")
            print("💡 Le système fonctionnera avec les modèles disponibles")
        else:
            print("\n🎉 Toutes les clés API sont configurées !")
            print("💡 Le système utilisera le meilleur modèle IA disponible")
            
    else:
        print("❌ Fichier .env non trouvé")
        print("\n📝 Création du fichier .env...")
        
        # Créer le fichier .env
        env_content = """# 🔑 CONFIGURATION DES MODÈLES IA
# Copiez ce fichier et ajoutez vos vraies clés API

# 🌟 CLAUDE (ANTHROPIC) - RECOMMANDÉ - Priorité 1
# Allez sur https://console.anthropic.com/
ANTHROPIC_API_KEY=votre_clé_claude_ici

# 🇫🇷 MISTRAL AI - EXCELLENT POUR LE FRANÇAIS - Priorité 2
# Allez sur https://console.mistral.ai/
MISTRAL_API_KEY=votre_clé_mistral_ici

# 🤖 OPENAI - TRÈS AVANCÉ - Priorité 3
# Allez sur https://platform.openai.com/
OPENAI_API_KEY=votre_clé_openai_ici

# 📝 INSTRUCTIONS :
# 1. Remplacez les valeurs par vos vraies clés API
# 2. Le système utilisera automatiquement le meilleur modèle disponible
# 3. Si aucune clé n'est configurée, le système utilisera le mode fallback
"""
        
        try:
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
            print("✅ Fichier .env créé avec succès")
            print("💡 Modifiez-le pour ajouter vos vraies clés API")
        except Exception as e:
            print(f"❌ Erreur lors de la création du fichier .env: {str(e)}")
    
    print("\n🚀 PROCHAINES ÉTAPES :")
    print("1. Obtenez vos clés API sur les plateformes respectives")
    print("2. Ajoutez-les dans le fichier .env")
    print("3. Testez le générateur IA avec : python test_ai_generator.py")
    print("4. Intégrez-le dans votre API avec : python test_content_api.py")

if __name__ == "__main__":
    setup_ai_keys()














