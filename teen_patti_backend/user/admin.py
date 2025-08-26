from django.contrib import admin
from .models import *


# class UserAccountAdmin(admin.ModelAdmin):
#     list_display = ('id', 'email', 'username', 'role', 'verify', 'created_at')
#     list_filter = ('role', 'verify')
#     search_fields = ('email', 'username')
#     readonly_fields = ('id', 'created_at')

# admin.site.register(UserAccount, UserAccountAdmin)
# admin.site.register(RevokedToken)
# admin.site.register(Recharge)

from django.contrib import admin
from .models import UserAccount, RevokedToken, Recharge


class UserAccountAdmin(admin.ModelAdmin):
    # Automatically include all model fields
    def get_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    def get_readonly_fields(self, request, obj=None):
        # Keep id and created_at as readonly
        return ('id', 'created_at')

    list_display = [field.name for field in UserAccount._meta.fields]
    search_fields = ('email', 'username', 'phone_number', 'referral_code')
    list_filter = ('role', 'verify', 'is_online', 'term_and_condition')


admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(RevokedToken)
admin.site.register(Recharge)

