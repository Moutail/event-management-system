#!/usr/bin/env python
"""
Script pour ajouter des logs de débogage dans le sérialiseur
"""

def add_debug_logs():
    """Ajoute des logs de débogage dans le sérialiseur"""
    file_path = 'events/serializers.py'
    
    print("🔧 Ajout des logs de débogage...")
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ajouter les logs au début de la méthode validate
    debug_logs = '''    def validate(self, data):
        # 🎯 NOUVEAU : Logs de débogage détaillés
        print(f"🔍 DEBUG: validate() appelé avec data: {data}")
        print(f"🔍 DEBUG: Clés dans data: {list(data.keys())}")
        print(f"🔍 DEBUG: guest_full_name: {data.get('guest_full_name')}")
        print(f"🔍 DEBUG: guest_email: {data.get('guest_email')}")
        print(f"🔍 DEBUG: guest_phone: {data.get('guest_phone')}")
        print(f"🔍 DEBUG: guest_country: {data.get('guest_country')}")
        
        event = data['event']
        request = self.context['request']
        user = getattr(request, 'user', None)
        
        # 🎯 NOUVELLE LOGIQUE : Gérer les utilisateurs connectés ET les invités
        guest_full_name = data.get('guest_full_name')
        guest_email = data.get('guest_email')
        guest_phone = data.get('guest_phone')
        guest_country = data.get('guest_country')
        
        # Déterminer si c'est une inscription d'invité
        is_guest = bool(guest_full_name and guest_email and guest_phone and guest_country)
        print(f"🔍 DEBUG: is_guest = {is_guest}")
        print(f"🔍 DEBUG: guest_full_name: {guest_full_name}")
        print(f"🔍 DEBUG: guest_email: {guest_email}")
        print(f"🔍 DEBUG: guest_phone: {guest_phone}")
        print(f"🔍 DEBUG: guest_country: {guest_country}")
        
        if is_guest:'''
    
    # Remplacer le début de la méthode validate
    import re
    content = re.sub(
        r'def validate\(self, data\):\s*\n\s*event = data\[\'event\'\]',
        debug_logs,
        content,
        flags=re.MULTILINE
    )
    
    # Écrire le fichier modifié
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Logs de débogage ajoutés !")

if __name__ == '__main__':
    add_debug_logs()



