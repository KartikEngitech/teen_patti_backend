from rest_framework import serializers
from user.models import *
from game.models import *

class GetAllUserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id','email','first_name','last_name','role','phone_number','term_and_condition',
                  'verify','created_at','referred_by','is_active','last_login']


class GameTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameTable
        fields = '__all__'