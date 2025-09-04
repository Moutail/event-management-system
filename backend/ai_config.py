"""
🔑 Configuration des clés API pour les modèles IA
"""

import os
from typing import Optional

# Configuration des clés API
AI_CONFIG = {
    # Claude (Anthropic) - Priorité 1
    'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
    
    # Mistral AI - Priorité 2  
    'MISTRAL_API_KEY': os.getenv('MISTRAL_API_KEY'),
    
    # OpenAI - Priorité 3
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
}

def get_available_models() -> list:
    """Retourne la liste des modèles IA disponibles"""
    available = []
    
    if AI_CONFIG['ANTHROPIC_API_KEY']:
        available.append({
            'name': 'Claude (Anthropic)',
            'priority': 1,
            'model': 'claude-3-sonnet-20240229',
            'description': 'Excellente compréhension du français, très créatif'
        })
    
    if AI_CONFIG['MISTRAL_API_KEY']:
        available.append({
            'name': 'Mistral AI',
            'priority': 2,
            'model': 'mistral-large-latest',
            'description': 'Modèle français natif, très performant'
        })
    
    if AI_CONFIG['OPENAI_API_KEY']:
        available.append({
            'name': 'OpenAI GPT-4',
            'priority': 3,
            'model': 'gpt-4',
            'description': 'Modèle très avancé, excellente créativité'
        })
    
    return sorted(available, key=lambda x: x['priority'])

def get_default_model() -> Optional[str]:
    """Retourne le modèle par défaut disponible"""
    available = get_available_models()
    return available[0]['name'] if available else None

def check_ai_availability() -> dict:
    """Vérifie la disponibilité des modèles IA"""
    available_models = get_available_models()
    
    return {
        'available': len(available_models) > 0,
        'models': available_models,
        'default_model': get_default_model(),
        'total_models': len(available_models)
    }

# Instructions pour configurer les clés API
SETUP_INSTRUCTIONS = """
🚀 CONFIGURATION DES MODÈLES IA :

1. 🌟 CLAUDE (ANTHROPIC) - RECOMMANDÉ :
   - Allez sur https://console.anthropic.com/
   - Créez un compte et obtenez votre clé API
   - Ajoutez dans votre fichier .env :
     ANTHROPIC_API_KEY=votre_clé_ici

2. 🇫🇷 MISTRAL AI - EXCELLENT POUR LE FRANÇAIS :
   - Allez sur https://console.mistral.ai/
   - Créez un compte et obtenez votre clé API
   - Ajoutez dans votre fichier .env :
     MISTRAL_API_KEY=votre_clé_ici

3. 🤖 OPENAI - TRÈS AVANCÉ :
   - Allez sur https://platform.openai.com/
   - Créez un compte et obtenez votre clé API
   - Ajoutez dans votre fichier .env :
     OPENAI_API_KEY=votre_clé_ici

📝 NOTE : Le système utilisera automatiquement le meilleur modèle disponible !
"""

if __name__ == "__main__":
    print("🔍 Vérification de la configuration IA...")
    status = check_ai_availability()
    
    if status['available']:
        print(f"✅ {status['total_models']} modèle(s) IA disponible(s)")
        print(f"🎯 Modèle par défaut : {status['default_model']}")
        print("\n📋 Modèles disponibles :")
        for model in status['models']:
            print(f"   • {model['name']} - {model['description']}")
    else:
        print("❌ Aucun modèle IA configuré")
        print(SETUP_INSTRUCTIONS)













