from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from user.models import *
from .serializers import *
from game.models import *

class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role != 'admin':
                return Response({"detail": "You are not authorized to view this."}, status=status.HTTP_403_FORBIDDEN)

            users = UserAccount.objects.all()
            serializer = GetAllUserAccountSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GetGameTableListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.user.role != 'admin':
                return Response({"detail": "You are not authorized to view this."}, status=status.HTTP_403_FORBIDDEN)
            games = GameTable.objects.all()
            serializer = GameTableSerializer(games, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)