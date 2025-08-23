from rest_framework.throttling import SimpleRateThrottle
from rest_framework.response import Response
from rest_framework import status

class PostDetailThrottle(SimpleRateThrottle):
    scope = 'post_detail'

    def get_cache_key(self, request, view):
        try:
            if not request.user.is_authenticated:
                return None
            return self.cache_format % {
                'scope': self.scope,
                'ident': request.user.pk
            }
        except Exception as e:
                return Response({'error': 'Internal Server Error', 'details': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
