from django.urls import path
from .views import *

urlpatterns = [
    path('chatrooms/', ChatRoomListCreateView.as_view(), name='chatroom-list-create'),
    path('chatrooms/messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('chatrooms/details/', GetDetailsOfRoomAndParticipants.as_view(), name='message-list-create'),
]
