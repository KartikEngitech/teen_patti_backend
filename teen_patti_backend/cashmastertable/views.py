from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import MasterGameTable, Player, GameRound, PlayerAction
from user.models import UserAccount
from .serializers import GameTableSerializer, PlayerSerializer, GameRoundSerializer, PlayerActionSerializer

# class GameTableViewSet(viewsets.ModelViewSet):
#     queryset = GameTable.objects.all()
#     serializer_class = GameTableSerializer
#     permission_classes = [permissions.IsAuthenticated]
class GameTableView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # require login

    def get(self, request):
        """List all game tables"""
        tables = MasterGameTable.objects.all().order_by("id")
        serializer = GameTableSerializer(tables, many=True)

        # count online users
        online_users_count = UserAccount.objects.filter(is_online=True).count()

        return Response({
                "tables": serializer.data,
                "online_users": online_users_count
            }, status=status.HTTP_200_OK)


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