from rest_framework import serializers
from .models import GameTable

class GameTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameTable
        fields = '__all__'
