from django.contrib import admin
from .models import *

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    filter_horizontal = ('participants',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'participants')
        }),
    )
    
    readonly_fields = ('id',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'room', 'user', 'content', 'timestamp','image')
    search_fields = ('room__name', 'user__username', 'content')
    list_filter = ('timestamp',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('room', 'user', 'content')
        }),
        ('Timestamp', {
            'fields': ('timestamp',)
        }),
        ('Images and Audio', {
            'fields': ('image','audio',)
        }),
        
    )
    readonly_fields = ('id', 'timestamp')


@admin.register(UserMessageStatus)
class UserMessageStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'room',  'message', 'delivered',)
    search_fields = ('user__username', 'room__name', 'message__content')
    list_filter = ('delivered',)
    fieldsets = (
        ('User and Room', {
            'fields': ('user', 'room')
        }),
        ('Message Read Status', {
            'fields': ('unread',)
        }),
    )
    readonly_fields = ('room',)