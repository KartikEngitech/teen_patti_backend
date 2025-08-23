from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from user.models import *
from django.shortcuts import get_object_or_404
from django.db.models import Count
from uuid import UUID

class ChatRoomListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            chat_rooms = ChatRoom.objects.filter(participants=request.user)
            serializer = GetApiChatRoomSerializer(chat_rooms, many=True, context={'request': request})
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return Response({"error": f"Unexpected error {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            participants_data = request.data.get('participants', [])

            if not participants_data:
                return Response({"error": "Participants are required"}, status=status.HTTP_400_BAD_REQUEST)

            participant_ids = {request.user.id}
            for participant in participants_data:
                participant_ids.add(UUID(participant["id"]))

            possible_chat_rooms = ChatRoom.objects.annotate(participant_count=Count('participants')).filter(
                participant_count=len(participant_ids)
            )

            for chat_room in possible_chat_rooms:
                existing_participant_ids = set(chat_room.participants.values_list('id', flat=True))
                if existing_participant_ids == participant_ids:
                    serializer = ChatRoomSerializer(chat_room)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            
            chat_room = ChatRoom.objects.create(name=request.data.get("name", ""))
            chat_room.participants.add(*participant_ids)
            
            serializer = ChatRoomSerializer(chat_room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return Response({"error": f"Unexpected error {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MessageListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            room_id = request.query_params.get('room_id')
            room = get_object_or_404(ChatRoom, id=room_id)
            messages = Message.objects.filter(room=room)
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return Response({"error": f"Unexpected error {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            room_id = request.query_params.get('room_id')
            room = get_object_or_404(ChatRoom, id=room_id)
            serializer = MessageSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, room=room)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return Response({"error": f"Unexpected error {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetDetailsOfRoomAndParticipants(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            chat_rooms = ChatRoom.objects.filter(participants=request.user)
            serializer = ChatRoomDetailsSerializer(chat_rooms, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return Response({"error": f"Unexpected error {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
