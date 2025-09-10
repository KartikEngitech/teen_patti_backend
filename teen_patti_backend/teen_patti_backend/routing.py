from django.urls import re_path,path
from game.consumers import *

websocket_urlpatterns = [
    path('ws/game/', GameConsumer.as_asgi()),
    path('ws/wallet-gaming/', WalletAndWinnigConsumer.as_asgi()),
    path('ws/playerinfo/', PlayerInGameConsumer.as_asgi()),


]