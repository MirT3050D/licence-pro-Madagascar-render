from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProduitViewSet, PrixViewSet, ActivationViewSet

router = DefaultRouter()
router.register(r'prix', PrixViewSet, basename='prix')
router.register(r'activations', ActivationViewSet, basename='activation')
router.register(r'', ProduitViewSet, basename='produit')

urlpatterns = [
    path('', include(router.urls)),
]
