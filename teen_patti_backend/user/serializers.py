from rest_framework import serializers
from .models import *
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from candidateapp.models import FCMToken
from game.models import UserWallet



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = UserAccount
        fields = ['id', 'email', 'role','code' ,'password','created_at','phone_number','referred_by']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
            instance.user_password = password
        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['email','id','role','phone_number','term_and_condition','verify']


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        # fields = ['id','email']
        fields = "__all__"   # include all fields from UserAccount



class RevokedTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevokedToken
        fields = ['token', 'date_revoked']


class CompanyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.role != 'company':
            raise AuthenticationFailed("Access denied for non-companies.")
        if self.user.verify != True:
            raise AuthenticationFailed("Access denied for unverified-users.")
        data['role'] = self.user.role
        return data

class CandidateTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.role != 'candidate':
            raise AuthenticationFailed("Access denied for non-student.")
        if self.user.verify != True:
            raise AuthenticationFailed("Access denied for unverified-users")
        data['role'] = self.user.role
        return data
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.verify:
            raise AuthenticationFailed("Access denied for unverified users.")

        requested_role = self.context['request'].data.get('role')
        fcm_token = self.context['request'].data.get('fcm_token')
        if requested_role and requested_role != self.user.role:
            raise AuthenticationFailed(f"Access denied. You are not a {requested_role}.")
        
        # if fcm_token:
        #     FCMToken.objects.update_or_create(user=self.user, defaults={'token': fcm_token})

        # data['role'] = self.user.role
        # return data

        # Add all user data
        user_data = UserAccountSerializer(self.user).data
        data['user'] = user_data   # attach all user model fields
        data['role'] = self.user.role
        return data
    
class UserWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWallet
        fields = "__all__"

