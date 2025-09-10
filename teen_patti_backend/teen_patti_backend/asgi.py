# """
# ASGI config for teen_patti_backend project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teen_patti_backend.settings')

# application = get_asgi_application()



import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teen_patti_backend.settings')

django_asgi_app = get_asgi_application()

import teen_patti_backend.routing  # 👈 move this AFTER settings are configured

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket":URLRouter(
            teen_patti_backend.routing.websocket_urlpatterns
        ),
})

