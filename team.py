from player import Player
from typing import List


class Team:
    def __init__(self, players: List[Player]) -> None:
        self.players = players

    def score(self):
        return sum([player.score for player in self.players])

    def can_pin(self):
        return self.score() <= 115

    def has_won(self):
        return self.score() >= 121
