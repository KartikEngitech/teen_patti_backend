from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import GameTable, Player, GameRound, PlayerAction
from .serializers import GameTableSerializer, PlayerSerializer, GameRoundSerializer, PlayerActionSerializer

class GameTableViewSet(viewsets.ModelViewSet):
    queryset = GameTable.objects.all()
    serializer_class = GameTableSerializer
    permission_classes = [permissions.IsAuthenticated]

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only players belonging to the same table as the requesting user
        auth_user = self.request.user
        return Player.objects.filter(user=auth_user)

class GameRoundViewSet(viewsets.ModelViewSet):
    queryset = GameRound.objects.all()
    serializer_class = GameRoundSerializer
    permission_classes = [permissions.IsAuthenticated]

class PlayerActionViewSet(viewsets.ModelViewSet):
    queryset = PlayerAction.objects.all()
    serializer_class = PlayerActionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)

        # Assign authenticated user's Player object
        try:
            player = Player.objects.get(user=request.user)
        except Player.DoesNotExist:
            return Response({"error": "Player not found for user"}, status=400)

        request.data['player'] = player.id
        return super().create(request, *args, **kwargs)
