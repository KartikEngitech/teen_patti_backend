from rest_framework import serializers
from .models import *
from user.models import *


class ParticipantSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = UserAccount
        fields = ['id', 'name', 'image']

    def get_name(self, obj):
        if obj.role == 'company':
            return obj.company_profile.company_name if hasattr(obj, 'company_profile') else obj.username
        elif obj.role == 'candidate':
            return f"{obj.candidate_profile.full_name}" if hasattr(obj, 'candidate_profile') else obj.username
        return obj.username

    def get_image(self, obj):
        if obj.role == 'company' and hasattr(obj, 'company_profile'):
            return obj.company_profile.company_logo.url if obj.company_profile.company_logo else None
        elif obj.role == 'candidate' and hasattr(obj, 'candidate_profile'):
            return obj.candidate_profile.profile_picture.url if obj.candidate_profile.profile_picture else None
        return None

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True)

    class Meta:
        model = ChatRoom
        fields = '__all__'

    def create(self, validated_data):
        participants_data = validated_data.pop('participants')
        chat_room = ChatRoom.objects.create(**validated_data)
        for participant_data in participants_data:
            participant_id = participant_data['id']
            participant = UserAccount.objects.get(id=participant_id)
            chat_room.participants.add(participant)
        return chat_room
    
class GetApiChatRoomSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True)
    user_id = serializers.SerializerMethodField()


    class Meta:
        model = ChatRoom
        fields = '__all__'

    def get_user_id(self, obj):
        request = self.context.get('request', None)
        return str(request.user.id) if request and request.user else None


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        request = self.context.get('request', None)
        if request and request.user:
            user_id = str(request.user.id)
            representation['participants'] = [
                participant for participant in representation['participants']
                if participant["id"] != user_id
            ]
        return representation


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


# class ChatRoomDetailsSerializer(serializers.ModelSerializer):
#     participants = serializers.SerializerMethodField()

#     class Meta:
#         model = ChatRoom
#         fields = ['id', 'name', 'participants']

#     def get_participants(self, obj):
#         request_user = self.context['request'].user
#         participants = obj.participants.filter(id=request_user.id)
#         return ParticipantSerializer(participants, many=True).data


class ChatRoomDetailsSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'name', 'participants', 'last_message', 'unread_count', 'created_at']

    def get_participants(self, obj):
        """ Exclude the requesting user from the participants list """
        request_user = self.context['request'].user
        participants = obj.participants.exclude(id=request_user.id)
        return ParticipantSerializer(participants, many=True).data

    def get_last_message(self, obj):
        """ Fetch the last message in the chat room """
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return {
                "id": str(last_message.id),
                "content": last_message.content,
                "image": last_message.image.url if last_message.image else None,
                "audio": last_message.audio.url if last_message.audio else None,
                "timestamp": last_message.timestamp,
                "sender_id": str(last_message.user.id) if last_message.user else None
            }
        return None  # No messages yet

    def get_unread_count(self, obj):
        """ Count the number of unread messages for the requesting user """
        request_user = self.context['request'].user
        return UserMessageStatus.objects.filter(room=obj, user=request_user, unread=True).count()