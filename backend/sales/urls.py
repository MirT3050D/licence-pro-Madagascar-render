from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MethodePaiementViewSet, VenteViewSet, DashboardView, MediaBuyerCommissionConfigView

router = DefaultRouter()
router.register(r'methodes-paiement', MethodePaiementViewSet, basename='methode-paiement')
router.register(r'', VenteViewSet, basename='vente')

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard-stats'),
    path('commission-media-buyer/', MediaBuyerCommissionConfigView.as_view(), name='commission-media-buyer-config'),
    path('media-buyer-commission/', MediaBuyerCommissionConfigView.as_view(), name='media-buyer-commission-config'),
    path('', include(router.urls)),
]
