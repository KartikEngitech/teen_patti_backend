from django.contrib import admin
from .models import MasterGameTable


@admin.register(MasterGameTable)
class MasterGameTableAdmin(admin.ModelAdmin):
    list_display = ('id', 'boot_price', 'max_bet_value', 'players', 'max_players')
    search_fields = ('id', 'boot_price', 'max_bet_value')
    list_filter = ('boot_price', 'max_players')
