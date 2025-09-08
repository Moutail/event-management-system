"""
Configuration des URLs principales
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from events.cron_views import trigger_notifications, health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('events.urls')),
    path('cron/notifications/', trigger_notifications, name='cron_notifications'),
    path('health/', health_check, name='health_check'),
]

# 🔍 DEBUG: Logs des URLs
print("🔍 DEBUG: URLs principales configurées:")
for url_pattern in urlpatterns:
    print(f"🔍 DEBUG: - {url_pattern}")

# Ajouter les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 