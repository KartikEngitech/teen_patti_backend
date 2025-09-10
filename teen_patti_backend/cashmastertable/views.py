from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import MasterGameTable, Player, GameRound, PlayerAction
from user.models import UserAccount
from game.models import Player
from .serializers import GameTableSerializer, PlayerSerializer, GameRoundSerializer, PlayerActionSerializer

# class GameTableViewSet(viewsets.ModelViewSet):
#     queryset = GameTable.objects.all()
#     serializer_class = GameTableSerializer
#     permission_classes = [permissions.IsAuthenticated]
# class GameTableView(APIView):
#     permission_classes = [permissions.IsAuthenticated]  # require login

#     def get(self, request):
#         """List all game tables"""
#         tables = MasterGameTable.objects.all().order_by("id")
#         serializer = GameTableSerializer(tables, many=True)

#         # count online users
#         online_users_count = UserAccount.objects.filter(is_online=True).count()

#         return Response({
#                 "tables": serializer.data,
#                 "online_users": online_users_count
#             }, status=status.HTTP_200_OK)



class GameTableView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # require login

    def get(self, request):
        """List all game tables with online users"""
        tables = MasterGameTable.objects.all().order_by("id")

        response_data = []
        for table in tables:
            # count how many players are online in this table
            online_users_count = Player.objects.filter(
                is_active=True, # assumes Player model has FK to MasterGameTable
            ).count()

            response_data.append({
                "id": table.id,
                "boot_price": table.boot_price,
                "max_bet_value": table.max_bet_value,
                "players": table.players,
                "max_players": table.max_players,
                "online_users": online_users_count
            })

        return Response(response_data, status=status.HTTP_200_OK)

class CreateGameView(APIView):
    def post(self, request):
        try:
            # Create a new game
            game = GameTable.objects.create(
                id=uuid.uuid4(),  # generate unique game id
                is_active=True
            )
            return Response(
                {"game_id": str(game.id), "message": "Game created successfully"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)        


class PlayerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        players = Player.objects.all().order_by("id")
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameRoundView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rounds = GameRound.objects.all().order_by("id")
        serializer = GameRoundSerializer(rounds, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GameRoundSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        actions = PlayerAction.objects.all().order_by("id")
        serializer = PlayerActionSerializer(actions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PlayerActionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)