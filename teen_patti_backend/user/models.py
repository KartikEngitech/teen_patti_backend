from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser, PermissionsMixin
import uuid
from django.utils import timezone
from .utils import generate_referral_code

class UserAccount(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ROLES = (
        ('admin', 'admin'),
        ('subadmin', 'subadmin'),
        ('user', 'user'),
    )
    email = models.EmailField(null=True, unique=True)
    username = models.CharField(max_length=50, null=True,default="",blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(choices=ROLES, max_length=10)
    verify = models.BooleanField(default=False)
    code = models.CharField(max_length=20,default="",blank=True, null=True)
    otp = models.CharField(max_length=10,blank=True, null=True,default='')
    phone_number = models.CharField(max_length=15,blank=True, null=True)
    user_password = models.CharField(max_length=128, blank=True)  
    email_changed = models.JSONField(default=list, blank=True, null=True, help_text='JSON array of old email addresses and their change timestamps')
    last_email_changed_at = models.DateTimeField(blank=True, null=True, help_text='Date and time of the last email change')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True, null=True, help_text='Last seen timestamp')
    term_and_condition = models.BooleanField(default=False,blank=True, null=True)
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='referrals')
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.referral_code:
            while True:
                code = generate_referral_code()
                if not UserAccount.objects.filter(referral_code=code).exists():
                    self.referral_code = code
                    break
        super().save(*args, **kwargs)





class RevokedToken(models.Model):
    token = models.CharField(max_length=500)
    date_revoked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.token

class Recharge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


