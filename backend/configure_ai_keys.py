#!/usr/bin/env python
"""
🔑 Script de configuration automatique des clés API pour les modèles IA
"""

import os
from pathlib import Path

def configure_ai_keys():
    """Configure automatiquement les clés API pour les modèles IA"""
    print("🔑 Configuration automatique des clés API pour les modèles IA")
    print("=" * 70)
    
    # Clés API fournies par l'utilisateur
    ai_keys = {
        'ANTHROPIC_API_KEY': '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',
        'MISTRAL_API_KEY': '9F34hstjd4ul2hi2Sry0v9Of1UsbA1tt',
        'OPENAI_API_KEY': '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'
    }
    
    print("🎯 Clés API détectées :")
    for key_name, key_value in ai_keys.items():
        print(f"   ✅ {key_name}: {'*' * 20}...{key_value[-8:]}")
    
    # Vérifier si le fichier .env existe
    env_file = Path(".env")
    
    if env_file.exists():
        print("\n📝 Fichier .env trouvé - Mise à jour...")
        
        # Lire le contenu existant
        try:
            with open(".env", "r", encoding="utf-8") as f:
                existing_content = f.read()
        except Exception as e:
            print(f"❌ Erreur lecture .env: {str(e)}")
            existing_content = ""
        
        # Mettre à jour ou ajouter les clés
        updated_content = existing_content
        
        for key_name, key_value in ai_keys.items():
            # Chercher si la clé existe déjà
            if key_name in existing_content:
                # Remplacer la ligne existante
                import re
                pattern = rf"^{key_name}=.*$"
                replacement = f"{key_name}={key_value}"
                updated_content = re.sub(pattern, replacement, updated_content, flags=re.MULTILINE)
                print(f"   🔄 {key_name} mise à jour")
            else:
                # Ajouter la nouvelle clé
                updated_content += f"\n{key_name}={key_value}"
                print(f"   ➕ {key_name} ajoutée")
        
        # Écrire le fichier mis à jour
        try:
            with open(".env", "w", encoding="utf-8") as f:
                f.write(updated_content)
            print("✅ Fichier .env mis à jour avec succès")
        except Exception as e:
            print(f"❌ Erreur écriture .env: {str(e)}")
            return False
            
    else:
        print("\n📝 Création du fichier .env...")
        
        # Créer le contenu du fichier .env
        env_content = """# 🔑 CONFIGURATION DES MODÈLES IA
# Clés API configurées pour la vraie IA !

# 🌟 CLAUDE (ANTHROPIC) - RECOMMANDÉ - Priorité 1
ANTHROPIC_API_KEY=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

# 🇫🇷 MISTRAL AI - EXCELLENT POUR LE FRANÇAIS - Priorité 2
MISTRAL_API_KEY=9F34hstjd4ul2hi2Sry0v9Of1UsbA1tt

# 🤖 OPENAI - TRÈS AVANCÉ - Priorité 3
OPENAI_API_KEY=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

# 📝 NOTE : Le système utilisera automatiquement le meilleur modèle disponible !
"""
        
        try:
            with open(".env", "w", encoding="utf-8") as f:
                f.write(env_content)
            print("✅ Fichier .env créé avec succès")
        except Exception as e:
            print(f"❌ Erreur création .env: {str(e)}")
            return False
    
    # Vérifier la configuration
    print("\n🔍 Vérification de la configuration...")
    
    # Charger les variables d'environnement
    from dotenv import load_dotenv
    load_dotenv()
    
    # Vérifier les clés
    configured_keys = {}
    for key_name in ai_keys.keys():
        configured_keys[key_name] = os.getenv(key_name)
    
    print("\n📊 État des clés API :")
    for key_name, key_value in configured_keys.items():
        if key_value:
            print(f"   ✅ {key_name}: {'*' * 20}...{key_value[-8:]}")
        else:
            print(f"   ❌ {key_name}: Non configurée")
    
    # Compter les clés configurées
    configured_count = sum(1 for key in configured_keys.values() if key)
    print(f"\n📊 Résumé : {configured_count}/3 clés configurées")
    
    if configured_count == 3:
        print("\n🎉 TOUTES LES CLÉS API SONT CONFIGURÉES !")
        print("💡 Le système utilisera automatiquement le meilleur modèle IA disponible !")
        print("   Priorité : Claude > Mistral > OpenAI")
        return True
    elif configured_count > 0:
        print(f"\n⚠️ {configured_count} clé(s) configurée(s)")
        print("💡 Le système fonctionnera avec les modèles disponibles")
        return True
    else:
        print("\n❌ Aucune clé API configurée")
        print("💡 Le système utilisera le mode fallback (templates)")
        return False

if __name__ == "__main__":
    success = configure_ai_keys()
    
    if success:
        print("\n🚀 PROCHAINES ÉTAPES :")
        print("1. ✅ Clés API configurées")
        print("2. 🔍 Testez la configuration : python ai_config.py")
        print("3. 🤖 Testez le générateur IA : python test_ai_generator.py")
        print("4. 🎯 Profitez de la vraie IA !")
    else:
        print("\n❌ Configuration échouée")
        print("💡 Vérifiez les permissions et réessayez")














