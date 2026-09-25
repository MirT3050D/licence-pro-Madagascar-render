from django.urls import path
from .views import AIParsingView

urlpatterns = [
    path('parse/', AIParsingView.as_view(), name='ai-parse'),
]
