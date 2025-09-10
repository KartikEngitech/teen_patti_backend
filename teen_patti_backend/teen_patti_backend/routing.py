from django.urls import re_path,path
from game.consumers import *

websocket_urlpatterns = [
    re_path(r'ws/game/$', GameConsumer.as_asgi()),
    path('ws/wallet-gaming/', WalletAndWinnigConsumer.as_asgi()),
    path('ws/playerinfo/', PlayerInGameConsumer.as_asgi()),


]