from django.db import models

class GameTable(models.Model):
    boot_price = models.PositiveIntegerField(default=1000)   
    max_bet_value = models.CharField(max_length=20)          
    players = models.PositiveIntegerField(default=0)         
    max_players = models.PositiveIntegerField(default=5)     

    def __str__(self):
        return f"Table {self.id} - Boot: {self.boot_price}"