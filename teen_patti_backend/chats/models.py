from django.db import models
from django.conf import settings
import uuid

class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255,blank=True, null=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_rooms',blank=True)
    created_at = models.DateField(auto_now_add=True,blank=True, null=True)
    def __str__(self):
        return self.name

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE,blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages', on_delete=models.CASCADE,blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True)
    audio = models.FileField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True,blank=True, null=True)


class UserMessageStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,blank=True, null=True)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE,blank=True, null=True)
    message = models.ForeignKey(Message, related_name='deliveries', on_delete=models.CASCADE,blank=True, null=True)
    delivered = models.BooleanField(default=False)
    unread = models.BooleanField(default=True)

