from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import *
import random
from .serializers import *
from decimal import Decimal
from collections import Counter
from django.db import transaction  
from rest_framework.generics import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import PlayerSerializer
from .utils import  *
from datetime import date


class GameTableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve all game tables."""
        try:
            games = GameTable.objects.all()
            serializer = GameTableSerializer(games, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """Player joins or re-joins a game table."""
        try:
            game_id = request.data.get("game_id")
            if not game_id:
                return Response(
                    {"error": "game_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if requested game exists
            try:
                game = GameTable.objects.get(id=game_id, is_active=True)
            except GameTable.DoesNotExist:
                return Response(
                    {"error": "Game not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            channel_layer = get_channel_layer()

            # --- Rejoin logic ---
            existing_player = Player.objects.filter(user=request.user, game=game).first()
            if existing_player:
                async_to_sync(channel_layer.group_send)(
                    f"game_{game.id}",
                    {
                        "type": "player_joined",
                        "player": {
                            "id": str(existing_player.id),
                            "email": existing_player.user.email,
                            "position": existing_player.position,
                        },
                    },
                )

                return Response({
                    "message": "Re-joined existing game",
                    "game_id": str(game.id),
                    "player_id": str(existing_player.id),
                    "position": existing_player.position,
                }, status=status.HTTP_200_OK)

            # Assign next position
            last_pos = (
                Player.objects.filter(game=game)
                .order_by("-position")
                .values_list("position", flat=True)
                .first()
            )
            position = last_pos + 1 if last_pos is not None else 0

            player = Player.objects.create(
                user=request.user,
                game=game,
                position=position,
                bet_amount=game.boot_amount,
            )

            # Broadcast player join event
            async_to_sync(channel_layer.group_send)(
                f"game_{game.id}",
                {
                    "type": "player_joined",
                    "player": {
                        "id": str(player.id),
                        "email": player.user.email,
                        "position": player.position,
                    },
                },
            )

            # Optional: auto-start when enough players join (example: 3)
            total_players = Player.objects.filter(game=game).count()
            if total_players >= 3:
                async_to_sync(channel_layer.group_send)(
                    f"game_{game.id}",
                    {
                        "type": "game_started",
                        "event": {"game_id": str(game.id), "total_players": total_players},
                    },
                )

            return Response({
                "message": "Joined game successfully",
                "game_id": str(game.id),
                "player_id": str(player.id),
                "position": position,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )






# class GameTableView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         """Retrieve all game tables."""
#         try:
#             games = GameTable.objects.all()
#             serializer = GameTableSerializer(games, many=True)
#             return Response(serializer.data)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     def post(self, request):
#         """Player joins or re-joins a game table."""
#         try:
#             game_id = request.data.get("game_id")
#             if not game_id:
#                 return Response(
#                     {"error": "game_id is required"}, 
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # Check if requested game exists
#             try:
#                 game = GameTable.objects.get(id=game_id, is_active=True)
#             except GameTable.DoesNotExist:
#                 return Response(
#                     {"error": "Game not found"},
#                     status=status.HTTP_404_NOT_FOUND
#                 )

#             # --- Rejoin logic ---
#             existing_player = Player.objects.filter(user=request.user, game=game).first()
#             if existing_player:
#                 return Response({
#                     "message": "Re-joined existing game",
#                     "game_id": str(game.id),
#                     "player_id": str(existing_player.id),
#                     "position": existing_player.position,
#                 }, status=status.HTTP_200_OK)

#             # --- Optional: allow multiple rooms OR force one room ---
#             # If you want to restrict user to ONE game at a time:
#             # Player.objects.filter(user=request.user).update(is_active=False)
#             # Or: delete their old seat from other tables

#             # Assign next position
#             last_pos = (
#                 Player.objects.filter(game=game)
#                 .order_by("-position")
#                 .values_list("position", flat=True)
#                 .first()
#             )
#             position = last_pos + 1 if last_pos is not None else 0

#             player = Player.objects.create(
#                 user=request.user,
#                 game=game,
#                 position=position,
#                 bet_amount=game.boot_amount,
#             )

#             return Response({
#                 "message": "Joined game successfully",
#                 "game_id": str(game.id),
#                 "player_id": str(player.id),
#                 "position": position,
#             }, status=status.HTTP_201_CREATED)

#         except Exception as e:
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


    # def post(self, request):
    #     try:
    #         boot_amount = Decimal(request.data.get("boot_amount", "50.00"))
    #         pot_limit = Decimal(request.data.get("pot_limit", "5000.00"))
    #         max_blind = Decimal(request.data.get("max_blind", '4'))
    #         chaal_limit = Decimal(request.data.get("chaal_limit", '128'))

    #         if pot_limit < boot_amount:
    #             return Response(
    #                 {"error": "Pot limit must be greater than or equal to boot amount."},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #         game = (
    #             GameTable.objects
    #             .annotate(player_count=models.Count('players'))
    #             .filter(
    #                 is_active=True,
    #                 has_started=False,
    #                 boot_amount=boot_amount,
    #                 pot_limit=pot_limit,
    #                 chaal_limit=chaal_limit,
    #                 player_count__lt=3
    #             )
    #             .first()
    #         )

    #         if not game:
    #             game = GameTable.objects.create(
    #                 created_by=request.user,
    #                 boot_amount=boot_amount,
    #                 pot_limit=pot_limit,
    #                 has_started=False,
    #                 max_blind=max_blind,
    #                 chaal_limit=chaal_limit
    #             )

    #         if Player.objects.filter(user=request.user, game=game).exists():
    #             return Response({'error': 'Already in game'}, status=status.HTTP_400_BAD_REQUEST)

    #         last_pos = (
    #             Player.objects.filter(game=game)
    #             .order_by('-position')
    #             .values_list('position', flat=True)
    #             .first()
    #         )
    #         position = last_pos + 1 if last_pos is not None else 0

    #         player = Player.objects.create(
    #             user=request.user,
    #             game=game,
    #             position=position,
    #             bet_amount=boot_amount
    #         )

    #         if Player.objects.filter(game=game).count() == 3:
    #             game.has_started = True
    #             game.save()

    #             channel_layer = get_channel_layer()
    #             async_to_sync(channel_layer.group_send)(
    #                 f'game_{game.id}',
    #                 {'type': 'game_started'}
    #             )

    #         player_data = convert_uuids(PlayerSerializer(player).data)
    #         channel_layer = get_channel_layer()
    #         async_to_sync(channel_layer.group_send)(
    #             f'game_{game.id}',
    #             {'type': 'player_joined', 'player': player_data}
    #         )

    #         return Response({
    #             "message": "Joined game successfully",
    #             "game_id": game.id,
    #             "player": player_data
    #         }, status=status.HTTP_201_CREATED)

    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class PlayerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all players in a game."""
        try:
            game_id = request.query_params.get('game_id')
            players = Player.objects.filter(game_id=game_id)
            print(players)
            serializer = PlayerSerializer(players, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            game_id = request.query_params.get('game_id')

            try:
                game = GameTable.objects.get(id=game_id, is_active=True)
            except GameTable.DoesNotExist:
                return Response({'error': 'Game not found or not active'}, status=status.HTTP_400_BAD_REQUEST)

            if Player.objects.filter(user=request.user, game=game).exists():
                return Response({'error': 'User already in game'}, status=status.HTTP_400_BAD_REQUEST)

            last_position = (
                Player.objects.filter(game=game)
                .order_by('-position')
                .values_list('position', flat=True)
                .first()
            )
            next_position = (last_position + 1) if last_position is not None else 0

            boot_amount = game.boot_amount or 0
            player = Player.objects.create(user=request.user, game=game, is_active=True, position=next_position,bet_amount=boot_amount)
            serializer = PlayerSerializer(player)
            player_data = serializer.data

            def convert_uuids_to_str(data):
                if isinstance(data, dict):
                    return {k: str(v) if isinstance(v, uuid.UUID) else convert_uuids_to_str(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [convert_uuids_to_str(i) for i in data]
                return data

            player_data = convert_uuids_to_str(player_data)

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'game_{game_id}',
                {
                    'type': 'player_joined',
                    'player': player_data
                }
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    # def patch(self, request, *args, **kwargs):
    #     try:
    #         game_id = request.query_params.get('game_id')
    #         if not game_id:
    #             return Response({"error": "game_id is required in query params."},status=status.HTTP_400_BAD_REQUEST)

    #         player = get_object_or_404(Player,user=request.user,game_id=game_id,has_folded=False)

    #         serializer = PlayerSerializer(player, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_200_OK)

    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #     except Player.DoesNotExist:
    #         return Response({"error": "Player not found or has already folded."},status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({"error": "Something went wrong.", "details": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
    def patch(self, request, *args, **kwargs):
        try:
            game_id = request.query_params.get('game_id')
            if not game_id:
                return Response({"error": "game_id is required in query params."}, status=status.HTTP_400_BAD_REQUEST)

            player = get_object_or_404(Player, user=request.user, game_id=game_id, has_folded=False)

            serializer = PlayerSerializer(player, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                if request.data.get("has_folded") is True:
                    game = player.game
                    check_auto_win(game)

                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Player.DoesNotExist:
            return Response({"error": "Player not found or has already folded."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Something went wrong.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DistributeCardsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the cards assigned to the logged-in player for a specific game."""
        try:
            game_id = request.query_params.get('game_id')

            if not game_id:
                return Response({'error': 'Game ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            player = Player.objects.get(user=request.user, game_id=game_id)
            cards = Card.objects.filter(player=player, game_id=game_id)
            
            if not cards.exists():
                return Response({'message': 'No cards found for this player'}, status=status.HTTP_404_NOT_FOUND)

            serializer = CardSerializer(cards, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Player.DoesNotExist:
            return Response({'error': 'Player not found in this game'}, status=status.HTTP_400_BAD_REQUEST)

        except GameTable.DoesNotExist:
            return Response({'error': 'Game not found'}, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        """Distribute 3 random cards to each player in the game."""
        try:
            game_id = request.query_params.get('game_id')
            game = GameTable.objects.get(id=game_id)
            players = game.players.all()

            suits = ['hearts', 'diamonds', 'clubs', 'spades']
            ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
            deck = [{'suit': s, 'rank': r} for s in suits for r in ranks]
            random.shuffle(deck)

            for player in players:
                for _ in range(3):
                    card = deck.pop()
                    Card.objects.create(suit=card['suit'], rank=card['rank'], player=player, game=game)

            return Response({'message': 'Cards distributed successfully'}, status=status.HTTP_200_OK)
        except GameTable.DoesNotExist:
            return Response({'error': 'Game not found'}, status=status.HTTP_400_BAD_REQUEST)



class BetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Place a bet in Teen Patti, deduct from wallet, and create a transaction."""
        try:
            game_id = request.query_params.get('game_id')
            amount = request.query_params.get('amount')
            is_blind = request.query_params.get('is_blind') == "true"

            if not game_id or not amount:
                return Response({'error': 'game_id and amount are required'}, status=status.HTTP_400_BAD_REQUEST)

            game = GameTable.objects.select_related('current_turn').prefetch_related('players').get(id=game_id)
            player = Player.objects.get(user=request.user, game=game)
            wallet = UserWallet.objects.get(user=request.user)

            if player.has_folded:
                return Response({'error': 'You have folded and cannot place a bet'}, status=status.HTTP_400_BAD_REQUEST)

            last_bet = Bet.objects.filter(game=game).order_by('-created_at').first()
            amount = Decimal(amount)

            if not last_bet and player.position == 0 and not game.has_started:
                game.has_started = True
                game.save()
            if last_bet:
                if last_bet.is_blind:
                    current_bet = last_bet.amount
                else:
                    current_bet = last_bet.amount * 2

                if is_blind and not last_bet.is_blind:
                    current_bet = last_bet.amount
            else:
                current_bet = game.boot_amount

            if is_blind:
                min_bet = current_bet
                max_bet = current_bet * 2
            else:
                min_bet = current_bet
                max_bet = current_bet * 4

            if not (min_bet <= amount <= max_bet):
                return Response({'error': f'Invalid bet amount. Must be between {min_bet} and {max_bet}'}, status=status.HTTP_400_BAD_REQUEST)

            if wallet.balance < amount:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                # wallet.balance -= amount
                # wallet.save()
                handle_wallet_transaction(request.user, game, -amount, 'bet')


                game.current_pot += amount
                game.save()
                player.bet_amount += amount
                if is_blind:
                    player.blind_count += 1
                else:
                    player.blind_count = 0

                player.save()

                bet = Bet.objects.create(player=player, game=game, amount=amount, is_blind=is_blind)

                Transaction.objects.create(
                    user=request.user,
                    game=game,
                    transaction_type='bet',
                    amount=amount
                )
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'user_{request.user.id}',
                    {
                        'type': 'wallet_update',
                        'balance': str(wallet.balance)
                    }
                )

                if game.pot_limit and game.current_pot >= game.pot_limit:
                    return self.showdown(game)

                if game.is_active:
                    next_turn = self.get_next_active_player(game, player)
                    if next_turn:
                        game.current_turn = next_turn
                        game.save()

                        serialized_player = UserPlayerSerializer(next_turn).data
                        serialized_player = {
                            key: str(value) if isinstance(value, uuid.UUID) else value
                            for key, value in serialized_player.items()
                        }

                        print("Next turn broadcast:", serialized_player)
                        group_name = f'game_{game.id}'
                        async_to_sync(channel_layer.group_send)(
                            group_name,
                            {
                                'type': 'send_current_turn',
                                'player': serialized_player
                            }
                        )
            return Response({'message': 'Bet placed successfully', 'bet': BetSerializer(bet).data}, status=status.HTTP_201_CREATED)

        except GameTable.DoesNotExist:
            return Response({'error': 'Game not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Player.DoesNotExist:
            return Response({'error': 'Player not found in this game'}, status=status.HTTP_400_BAD_REQUEST)
        except UserWallet.DoesNotExist:
            return Response({'error': 'User wallet not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def showdown(self, game):
        """Handles automatic showdown when the pot limit is reached."""
        players = game.players.filter(has_folded=False)
        player_hands = {player: self.evaluate_hand(player) for player in players}
        winner = max(player_hands, key=player_hands.get)

        game.winner = winner.user
        game.is_active = False
        game.save()

        winnings = game.current_pot
        # winner_wallet = UserWallet.objects.get(user=winner.user)
        # winner_wallet.balance += winnings
        # winner_wallet.save()

        handle_wallet_transaction(
        user=winner.user,
        game=game,
        amount=winnings,
        tx_type='win',
        hand_rank=player_hands[winner]
        )



        Transaction.objects.create(
            user=winner.user,
            game=game,
            transaction_type='win',
            amount=winnings
        )

        return Response({'message': f'Pot limit reached. Winner is {winner.user.email}'}, status=status.HTTP_200_OK)

    def evaluate_hand(self, player):
        """Dummy hand evaluation function (replace with actual logic)."""
        return random.randint(1, 100)

    def get_next_active_player(self, game, current_player):
        """Get the next player in clockwise order, skipping folded/inactive."""
        players = list(Player.objects.filter(game=game, is_active=True, has_folded=False).order_by('position'))
        if not players or len(players) < 2:
            return None

        current_index = next((i for i, p in enumerate(players) if p.id == current_player.id), None)
        if current_index is None:
            return players[0]

        next_index = (current_index + 1) % len(players)
        return players[next_index]



    def get(self, request):
        """Get all bets for a specific game."""
        game_id = request.query_params.get('game_id')
        if not game_id:
            return Response({'error': 'game_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        game = get_object_or_404(GameTable, id=game_id)
        bets = Bet.objects.filter(game=game).select_related('player', 'player__user')
        serializer = BetSerializer(bets, many=True)
        return Response({'bets': serializer.data}, status=status.HTTP_200_OK)



CARD_RANK_ORDER = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
class StartGameView(APIView):
    def post(self, request):
        game_id = request.data.get("game_id")
        if not game_id:
            return Response({"error": "game_id required"}, status=400)

        game = get_object_or_404(GameTable, id=game_id, is_active=True)

        if game.has_started:
            return Response({"error": "Game already started"}, status=400)

        game.has_started = True
        game.save()

        # Broadcast event
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"game_{game_id}",
            {
                "type": "game_started",
                "event": {"game_id": str(game.id), "message": "Game started!"}
            }
        )

        return Response({"message": "Game started successfully", "game_id": str(game.id)}, status=200)


class HandRankingView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        game_id = request.query_params.get('game_id')
        if not game_id:
            return Response({'error': 'game_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            game = GameTable.objects.get(id=game_id)
            players = game.players.filter(has_folded=False)
            
            if not players.exists():
                return Response({'error': 'No active players left'}, status=status.HTTP_400_BAD_REQUEST)
            
            player_hands = {player: evaluate_hand(player) for player in players}
            print(player_hands)
            winner = max(player_hands, key=lambda p: player_hands[p])
            
            winnings = game.current_pot

            with transaction.atomic():
                game.winner = winner.user
                game.is_active = False
                game.save()

                # Credit pot to winner
                handle_wallet_transaction(
                    user=winner.user,
                    game=game,
                    amount=winnings,
                    tx_type='win',
                    hand_rank=player_hands[winner]
                )

            return Response({
                'message': f'Winner is {winner.user.email}',
                'winner': winner.user.email,
                'hand_rank': player_hands[winner],
                'amount_won': str(winnings)
            }, status=status.HTTP_200_OK)

        except GameTable.DoesNotExist:
            return Response({'error': 'Game not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        
def evaluate_hand( player):
    cards = list(player.cards.all())
    if len(cards) != 3:
        return (0, [])  # Invalid hand

    ranks = sorted([CARD_RANK_ORDER[card.rank] for card in cards], reverse=True)
    suits = [card.suit for card in cards]
    rank_counts = Counter(ranks)

    # 1. Trail (Three of a Kind)
    if 3 in rank_counts.values():
        return (6, ranks)
    
    # 2. Pure Sequence (Straight Flush)
    if len(set(suits)) == 1 and ranks[0] - ranks[1] == ranks[1] - ranks[2] == 1:
        return (5, ranks)
    
    # 3. Sequence (Straight)
    if ranks[0] - ranks[1] == ranks[1] - ranks[2] == 1:
        return (4, ranks)
    
    # 4. Color (Flush)
    if len(set(suits)) == 1:
        return (3, ranks)
    
    # 5. Pair
    if 2 in rank_counts.values():
        return (2, ranks)
    
    # 6. High Card
    return (1, ranks)





class SeeCardsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Allow a player to see their cards, switching them from blind to seen."""
        try:
            game_id = request.data.get('game_id')

            if not game_id:
                return Response({'error': 'game_id is required'}, status=status.HTTP_400_BAD_REQUEST)

            player = Player.objects.get(user=request.user, game_id=game_id)

            if player.has_seen:
                return Response({'message': 'You have already seen your cards'}, status=status.HTTP_400_BAD_REQUEST)

            # Mark player as having seen their cards
            player.has_seen = True
            player.save()

            return Response({'message': 'You have now seen your cards'}, status=status.HTTP_200_OK)

        except Player.DoesNotExist:
            return Response({'error': 'Player not found in this game'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class SideShowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handle a side show request between two seen players."""
        try:
            game_id = request.data.get('game_id')
            opponent_id = request.data.get('opponent_id')

            game = GameTable.objects.get(id=game_id)
            player = Player.objects.get(user=request.user, game=game)
            opponent = Player.objects.get(id=opponent_id, game=game)

            # Both must be Seen players
            last_bet_player = Bet.objects.filter(player=player, game=game).order_by('-created_at').first()
            last_bet_opponent = Bet.objects.filter(player=opponent, game=game).order_by('-created_at').first()

            if last_bet_player.is_blind or last_bet_opponent.is_blind:
                return Response({'error': 'Side show is only allowed between Seen players'}, status=status.HTTP_400_BAD_REQUEST)

            # Evaluate hands (Replace with actual comparison logic)
            if evaluate_hand(player) < evaluate_hand(opponent):
                player.has_folded = True
                player.save()
                message = f"{player.user.email} lost the side show and folded."
            else:
                opponent.has_folded = True
                opponent.save()
                message = f"{opponent.user.email} lost the side show and folded."

            return Response({'message': message}, status=status.HTTP_200_OK)

        except GameTable.DoesNotExist:
            return Response({'error': 'Game not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Player.DoesNotExist:
            return Response({'error': 'Invalid player'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SpinWheelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # def get(self, request):
    #     user = request.user
    #     today = date.today()

    #     # Check if user has already spun today
    #     if SpinHistory.objects.filter(user=user, date=today).exists():
    #         return Response({"message": "You have already used your spin for today!"}, status=403)

    #     games_played = Player.objects.filter(user=user).count()

    #     reward_tiers = {
    #         (0, 10): None,
    #         (11, 40): Decimal('10.00'),
    #         (41, 60): Decimal('15.00'),
    #         (61, 100): Decimal('50.00'),
    #         (101, 200): Decimal('100.00'),
    #         (201, float('inf')): Decimal('100.00'),
    #     }

    #     reward = None
    #     for (min_games, max_games), amount in reward_tiers.items():
    #         if min_games <= games_played <= max_games:
    #             reward = amount
    #             break

    #     if reward is None:
    #         SpinHistory.objects.create(user=user)
    #         return Response({"message": "Better luck next time!"}, status=200)

    #     wallet = user.wallet
    #     wallet.balance += reward
    #     wallet.save()

    #     Transaction.objects.create(
    #         user=user,
    #         transaction_type='win',
    #         amount=reward,
    #         game=None,
    #         position=0
    #     )

    #     SpinHistory.objects.create(user=user)

    #     return Response({
    #         "message": f"You won ₹{reward}!",
    #         "reward": float(reward)
    #     }, status=200)


    def get(self, request):
        user = request.user
        today = date.today()

        if SpinHistory.objects.filter(user=user, date=today).exists():
            return Response({"message": "You have already used your spin for today!"}, status=403)

        games_played = Player.objects.filter(user=user).count()

        reward_tiers = {
            (0, 10): None,
            (11, 40): Decimal('10.00'),
            (41, 60): Decimal('15.00'),
            (61, 100): Decimal('50.00'),
            (101, 200): Decimal('100.00'),
            (201, float('inf')): Decimal('100.00'),
        }

        reward = None
        for (min_games, max_games), amount in reward_tiers.items():
            if min_games <= games_played <= max_games:
                reward = amount
                break

        if reward is None:
            SpinHistory.objects.create(user=user)
            return Response({"message": "Better luck next time!"}, status=200)

        bonus_wallet, _ = BonusWallet.objects.get_or_create(user=user)
        bonus_wallet.bonus_balance += reward
        bonus_wallet.save()

        Transaction.objects.create(
            user=user,
            transaction_type='win',
            amount=reward,
            game=None,
            position=0
        )

        SpinHistory.objects.create(user=user)

        return Response({
            "message": f"You won ₹{reward} in Bonus Wallet!",
            "reward": float(reward)
        }, status=200)



class TransferBonusToWalletAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        bonus_wallet = getattr(user, 'bonus_wallet', None)
        main_wallet = getattr(user, 'wallet', None)

        if not bonus_wallet or not main_wallet:
            return Response({"error": "Wallet not found!"}, status=404)

        if bonus_wallet.bonus_balance <= Decimal('0.00'):
            return Response({"message": "No bonus balance to transfer."}, status=400)

        transfer_amount = bonus_wallet.bonus_balance
        main_wallet.balance += transfer_amount
        bonus_wallet.bonus_balance = Decimal('0.00')

        main_wallet.save()
        bonus_wallet.save()

        Transaction.objects.create(
            user=user,
            transaction_type='deposit',
            amount=transfer_amount,
            game=None,
            position=0
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                "type": "wallet_update",
                "balance": float(main_wallet.balance)
            }
        )

        return Response({
            "message": f"₹{transfer_amount} has been transferred from your Bonus Wallet to your main Wallet.",
            "new_main_balance": float(main_wallet.balance),
            "bonus_wallet_balance": float(bonus_wallet.bonus_balance),
        }, status=200)





