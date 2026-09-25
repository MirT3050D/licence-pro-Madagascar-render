from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MethodePaiementViewSet, VenteViewSet, DashboardView

router = DefaultRouter()
router.register(r'methodes-paiement', MethodePaiementViewSet, basename='methode-paiement')
router.register(r'', VenteViewSet, basename='vente')

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard-stats'),
    path('', include(router.urls)),
]
