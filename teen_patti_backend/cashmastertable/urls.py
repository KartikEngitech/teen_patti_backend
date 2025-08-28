from django.urls import path
from .views import GameTableListCreateView, GameTableDetailView

urlpatterns = [
    path('gametables/', GameTableListCreateView.as_view(), name='game-table-list-create'),
    path('gametables/<int:pk>/', GameTableDetailView.as_view(), name='game-table-detail'),
]