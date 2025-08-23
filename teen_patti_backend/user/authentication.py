from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import RevokedToken,UserAccount
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        access_token = None
        if auth_header and auth_header.startswith('Bearer '):
            access_token = auth_header.split('Bearer ')[1]
        else:
            access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None

        if RevokedToken.objects.filter(token=access_token).exists():
            raise AuthenticationFailed('Unauthorized access token')

        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
        except Exception as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')

        return user, validated_token
    

def prevent_duplicate_users(strategy, details, backend, user=None, *args, **kwargs):
    """
    If a user with the same email exists, authenticate instead of creating a new one.
    """
    email = details.get("email")
    
    if user:
        refresh = RefreshToken.for_user(user)
        return {
            "is_new": False,
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }

    if email:
        existing_user = UserAccount.objects.filter(email=email).first()
        if existing_user:
            refresh = RefreshToken.for_user(existing_user)
            return {
                "is_new": False,
                "user": existing_user,
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
    
    return {}