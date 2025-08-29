from rest_framework import serializers
from .models import GameTable, Player, GameRound, PlayerAction

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'name', 'balance', 'seat_position', 'is_waiting', 'is_current_turn']

class PlayerActionSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = PlayerAction
        fields = ['id', 'player', 'action', 'timestamp']

class GameRoundSerializer(serializers.ModelSerializer):
    actions = PlayerActionSerializer(many=True, read_only=True)

    class Meta:
        model = GameRound
        fields = ['id', 'round_number', 'game_table', 'started_at', 'ended_at', 'actions']

class GameTableSerializer(serializers.ModelSerializer):
    players_info = PlayerSerializer(many=True, read_only=True, source='player_set')
    rounds = GameRoundSerializer(many=True, read_only=True)

    class Meta:
        model = GameTable
        fields = ['id', 'boot_price', 'max_bet_value', 'players', 'max_players', 'players_info', 'rounds']
