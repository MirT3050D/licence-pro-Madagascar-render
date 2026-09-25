"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.http import JsonResponse

def home_view(request):
    return JsonResponse({
        "status": "online",
        "app": "Licence Pro Madagascar API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/api/auth/",
            "produits": "/api/produits/",
            "clients": "/api/clients/",
            "ventes": "/api/ventes/",
            "ai": "/api/ai/",
            "admin": "/admin/"
        }
    })

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/produits/', include('catalog.urls')),
    path('api/ventes/', include('sales.urls')),
    path('api/ai/', include('ai_assistant.urls')),
]

# Media files serving
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
