import uuid
from django.db import models
from django.conf import settings


class GameTable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    # min_entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pot_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    current_pot = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_turn = models.ForeignKey('Player', on_delete=models.SET_NULL, null=True, blank=True, related_name='current_turn')
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='game_winner')
    boot_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    chaal_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_blind = models.IntegerField(null=True, blank=True)
    has_started = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_games',blank=True, null=True)
    # ✅ Link to MasterGameTable inside cashmastertable app
    master_table = models.ForeignKey('cashmastertable.MasterGameTable', on_delete=models.CASCADE, related_name='game_tables',null=True)

    def __str__(self):
        return f"GameTable {self.id}"



class UserWallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=100.00)  # Default wallet balance

    def __str__(self):
        return f"{self.user.email} Wallet Balance: {self.balance}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('bet', 'Bet'),
        ('win', 'Win'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    game = models.ForeignKey(GameTable, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    transaction_type = models.CharField(choices=TRANSACTION_TYPES, max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} {self.transaction_type} {self.amount}"


class SpinHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='spin_history')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} spun on {self.date}"


class BonusWallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bonus_wallet')
    bonus_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.email} Bonus Wallet: ₹{self.bonus_balance}"


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='players')
    game = models.ForeignKey(GameTable, on_delete=models.CASCADE, related_name='players')
    is_active = models.BooleanField(default=True)
    is_turn = models.BooleanField(default=False)
    position = models.IntegerField(blank=True, null=True)
    has_folded = models.BooleanField(default=False)
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    blind_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} in {self.game.id}"


class Card(models.Model):
    SUITS = [('hearts', 'Hearts'), ('diamonds', 'Diamonds'), ('clubs', 'Clubs'), ('spades', 'Spades')]
    RANKS = [
        ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'),
        ('8', '8'), ('9', '9'), ('10', '10'), ('J', 'Jack'), ('Q', 'Queen'),
        ('K', 'King'), ('A', 'Ace')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    suit = models.CharField(choices=SUITS, max_length=10)
    rank = models.CharField(choices=RANKS, max_length=2)
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='cards')
    game = models.ForeignKey(GameTable, on_delete=models.CASCADE, related_name='cards')

    def __str__(self):
        return f"{self.rank} of {self.suit} user :- {self.player.user.email} in {self.game.id}"


class Bet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='bets')
    game = models.ForeignKey(GameTable, on_delete=models.CASCADE, related_name='bets')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_blind = models.BooleanField(default=True)
    is_side_show = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user.email} bet {self.amount} in {self.game.id}"
