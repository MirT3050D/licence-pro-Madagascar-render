from django.urls import path
from .views import AIParsingView, AIChatView

urlpatterns = [
    path('parse/', AIParsingView.as_view(), name='ai-parse'),
    path('chat/', AIChatView.as_view(), name='ai-chat'),
]
