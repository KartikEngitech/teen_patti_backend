import json
from channels.generic.websocket import AsyncWebsocketConsumer
from user.models import *
from user.models import *
from channels.db import database_sync_to_async
from json.decoder import JSONDecodeError
from django.core.files.base import ContentFile
from django.utils.timezone import now
import base64
from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import *
from urllib.parse import parse_qs


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_params = parse_qs(self.scope['query_string'].decode())
        game_id = query_params.get('game_id', [None])[0]

        if not game_id:
            print("[CONNECT] Missing game_id in query params.")
            await self.close()
            return

        self.game_id = game_id
        self.room_group_name = f'game_{self.game_id}'

        print(f"[CONNECT] Joining group: {self.room_group_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        print(f"[DISCONNECT] Leaving group: {self.room_group_name}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"[RECEIVE] Message received: {text_data}")

    async def send_current_turn(self, event):
        print("[CONSUMER] send_current_turn triggered with:", event['player'])
        await self.send(text_data=json.dumps({
            'type': 'current_turn',
            'player': event['player']
        }))

    async def winner_announcement(self, event):
        print("[CONSUMER] winner_announcement triggered:", event)
        await self.send(text_data=json.dumps({
            'type': 'winner_announcement',
            'winner_email': event['winner_email'],
            'amount_won': event['amount_won'],
            'hand_rank': event['hand_rank'],
        }))

    async def game_winner(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_winner',
            'winner_email': event.get('winner_email') or event.get('winner'),
            'amount': event['amount'],
        }))


    async def game_started(self, event):
        await self.send(text_data=json.dumps({
            'message': 'Game has started!',
            'event': event,
        }))
    
    async def player_joined(self, event):
        print("[WalletAndWinnigConsumer] player_joined received but ignored.")




class WalletAndWinnigConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
            return

        self.user_group_name = f'user_{self.user.id}'

        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        game_id = query_params.get('game_id', [None])[0]

        self.game_id = game_id
        self.game_group_name = f'game_{self.game_id}' if self.game_id else None

        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        if self.game_group_name:
            await self.channel_layer.group_add(self.game_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)
        if self.game_group_name:
            await self.channel_layer.group_discard(self.game_group_name, self.channel_name)

    async def wallet_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'wallet_update',
            'balance': event['balance']
        }))

    # async def send_current_turn(self, event):
    #     await self.send(text_data=json.dumps({
    #         'type': 'current_turn',
    #         'player': event['player']
    #     }))

    async def player_joined(self, event):
        print("[GameConsumer] player_joined received but ignored.")

    async def game_started(self, event):
        print(f"[{self.__class__.__name__}] Ignored game_started event.")


    async def winner_announcement(self, event):
        await self.send(text_data=json.dumps({
            'type': 'winner_announcement',
            'winner_email': event['winner_email'],
            'amount_won': event['amount_won'],
            'hand_rank': event['hand_rank'],
        }))

    async def game_winner(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_winner',
            'winner_email': event['winner'],
            'amount_won': event['amount'],
        }))






class PlayerInGameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope["query_string"].decode()
        query_params = parse_qs(query_string)
        self.game_id = query_params.get("game_id", [None])[0]

        if not self.game_id:
            await self.close()
            return

        self.room_group_name = f"game_{self.game_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        pass

    async def player_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'player': event['player']
        }))

    async def game_started(self, event):
        print(f"[{self.__class__.__name__}] Ignored game_started event.")
    
    async def game_winner(self, event):
        print(f"[{self.__class__.__name__}] Ignored game_winner event.")
    
    async def winner_announcement(self, event):
        print(f"[{self.__class__.__name__}] Ignored winner_announcement event.")