# cashmastertable/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GameTableViewSet, PlayerViewSet,
    GameRoundViewSet, PlayerActionViewSet
)

router = DefaultRouter()
router.register(r'game-tables', GameTableViewSet, basename='gametable')
router.register(r'players', PlayerViewSet, basename='player')
router.register(r'rounds', GameRoundViewSet, basename='gameround')
router.register(r'actions', PlayerActionViewSet, basename='playeraction')

urlpatterns = [
    path('', include(router.urls)),
]

