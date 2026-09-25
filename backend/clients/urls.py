from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProvenanceViewSet, ClientViewSet

router = DefaultRouter()
router.register(r'provenances', ProvenanceViewSet, basename='provenance')
router.register(r'', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
]
