from django.urls import path
# from rest_framework.routers import DefaultRouter
from .views import GameTableView, PlayerView, GameRoundView, PlayerActionView

# router = DefaultRouter()
# # router.register(r'game-tables', GameTableViewSet, basename='gametable')
# router.register(r'players', PlayerViewSet, basename='player')
# router.register(r'rounds', GameRoundViewSet, basename='gameround')
# router.register(r'actions', PlayerActionViewSet, basename='playeraction')

urlpatterns = [
    # path('', include(router.urls)),
    path('game_tables/', GameTableView.as_view(), name='game-tables'),
    path('players/', PlayerView.as_view(), name="players"),
    path('rounds/', GameRoundView.as_view(), name="rounds"),
    path('actions/', PlayerActionView.as_view(), name="actions"),
]


