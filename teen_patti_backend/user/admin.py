from django.contrib import admin
from .models import *


class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'role', 'verify', 'created_at')
    list_filter = ('role', 'verify')
    search_fields = ('email', 'username')
    readonly_fields = ('id', 'created_at')

admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(RevokedToken)
admin.site.register(Recharge)
