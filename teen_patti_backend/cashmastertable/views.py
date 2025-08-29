# cashmastertable/views.py

from rest_framework import viewsets
from .models import GameTable, Player, GameRound, PlayerAction
from .serializers import (
    GameTableSerializer, PlayerSerializer,
    GameRoundSerializer, PlayerActionSerializer
)
from drf_yasg.utils import swagger_auto_schema

class GameTableViewSet(viewsets.ModelViewSet):
    queryset = GameTable.objects.all()
    serializer_class = GameTableSerializer

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

class GameRoundViewSet(viewsets.ModelViewSet):
    queryset = GameRound.objects.all()
    serializer_class = GameRoundSerializer

class PlayerActionViewSet(viewsets.ModelViewSet):
    queryset = PlayerAction.objects.all()
    serializer_class = PlayerActionSerializer

    @swagger_auto_schema(
        operation_summary="Create a player action (see/pack/slide)",
        operation_description="Log a player's action during a round"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
