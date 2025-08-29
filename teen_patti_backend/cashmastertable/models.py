# cashmastertable/models.py----------Aarti

from django.db import models

class GameTable(models.Model):
    boot_price = models.PositiveIntegerField(default=1000)
    max_bet_value = models.CharField(max_length=20)
    players = models.PositiveIntegerField(default=0)
    max_players = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"Table {self.id} - Boot: ₹{self.boot_price}"

class Player(models.Model):
    game_table = models.ForeignKey(GameTable, related_name="players_info", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    seat_position = models.PositiveIntegerField(help_text="Seat around the table")
    is_waiting = models.BooleanField(default=True)
    is_current_turn = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} at seat {self.seat_position}"

class GameRound(models.Model):
    game_table = models.ForeignKey(GameTable, related_name="rounds", on_delete=models.CASCADE)
    round_number = models.PositiveIntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Round {self.round_number} @ Table {self.game_table.id}"

class PlayerAction(models.Model):
    ACTION_TYPES = [
        ('see', 'See'),
        ('pack', 'Pack'),
        ('slide', 'Slide'),
    ]
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    round = models.ForeignKey(GameRound, related_name="actions", on_delete=models.CASCADE)
    action = models.CharField(max_length=10, choices=ACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.name} → {self.action} @ Round {self.round.round_number}"
