from rest_framework import serializers
from .models import *
from user.serializers import UserAccountSerializer

class GameTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameTable
        fields = '__all__'

    def get_online_users(self, obj):
        return obj.players.filter(is_active=True).count()


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'


class UserPlayerSerializer(serializers.ModelSerializer):
    # user_details = UserAccountSerializer(read_only=True)
    # user = serializers.UUIDField(format='hex', source='user.id')
    # game = serializers.UUIDField(format='hex', source='game.id')
    # id = serializers.UUIDField(format='hex')
    email = serializers.CharField(source='user.email', read_only=True)



    class Meta:
        model = Player
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = '__all__'


class BetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = '__all__'


# class MasterCardSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MasterCard
#         fields = ['master_card_id', 'suit', 'rank', 'image']
