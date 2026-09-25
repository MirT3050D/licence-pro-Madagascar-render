from django.urls import path
from .views import AIParsingView, AIChatView, AIStatusView

urlpatterns = [
    path('parse/', AIParsingView.as_view(), name='ai-parse'),
    path('chat/', AIChatView.as_view(), name='ai-chat'),
    path('status/', AIStatusView.as_view(), name='ai-status'),
]
