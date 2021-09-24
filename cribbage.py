from game import Game
from player import Player
from team import Team

teams = [Team([Player(i)]) for i in range(2)]

if __name__ == "__main__":
    Game(teams).play_game()
