import random
from .models import Card, Player
from django.db import transaction
from decimal import Decimal
from .models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from uuid import UUID

def distribute_cards(game):
    """Assigns 3 random cards to each player in the game."""
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [{'suit': s, 'rank': r} for s in suits for r in ranks]
    random.shuffle(deck)

    players = game.players.all()
    for player in players:
        for _ in range(3):
            card = deck.pop()
            Card.objects.create(suit=card['suit'], rank=card['rank'], player=player, game=game)


def handle_wallet_transaction(user, game, amount, tx_type,hand_rank=None):
    amount = Decimal(amount)
    with transaction.atomic():
        wallet = UserWallet.objects.select_for_update().get(user=user)
        wallet.balance += amount
        wallet.save()

        Transaction.objects.create(
            user=user,
            game=game,
            transaction_type=tx_type,
            amount=abs(amount)
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{user.id}',
            {
                'type': 'wallet_update',
                'balance': str(wallet.balance)
            }
        )

        if tx_type == 'win' and hand_rank is not None:
            async_to_sync(channel_layer.group_send)(
                f'game_{game.id}',
                {
                    'type': 'winner_announcement',
                    'winner_email': user.email,
                    'amount_won': str(amount),
                    'hand_rank': hand_rank
                }
            )

    return wallet



def convert_uuids(obj):
    if isinstance(obj, dict):
        return {k: convert_uuids(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_uuids(i) for i in obj]
    elif isinstance(obj, UUID):
        return str(obj)
    return obj




def check_auto_win(game):
    """Declare winner if only one active player is left."""
    active_players = list(game.players.filter(has_folded=False, is_active=True))
    if len(active_players) == 1:
        winner = active_players[0]
        winnings = game.current_pot

        game.winner = winner.user
        game.is_active = False
        game.save()

        handle_wallet_transaction(
            user=winner.user,
            game=game,
            amount=winnings,
            tx_type='win',
            hand_rank=(0, [])
        )

        Transaction.objects.create(
            user=winner.user,
            game=game,
            transaction_type='win',
            amount=winnings
        )

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'game_{game.id}',
            {
                'type': 'game_winner',
                'winner': winner.user.email,
                'amount': str(winnings)
            }
        )
        return True
    return False



def get_games_played_count(user):
    return Player.objects.filter(user=user).count()
