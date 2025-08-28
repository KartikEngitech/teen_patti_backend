from rest_framework import generics
from .models import GameTable
from .serializers import GameTableSerializer

# CREATE & LIST
class GameTableListCreateView(generics.ListCreateAPIView):
    queryset = GameTable.objects.all()
    serializer_class = GameTableSerializer

# READ, UPDATE, DELETE by ID
class GameTableDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GameTable.objects.all()
    serializer_class = GameTableSerializer
