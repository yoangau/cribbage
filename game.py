from player import Player
from itertools import product
from random import choice, shuffle
from typing import List
from team import Team
from card import Card
from functools import reduce


class Game:
    colors = ["spades", "hearts", "diamonds", "clubs"]
    types = list(range(1, 14))
    max_score = 121

    def __init__(self, teams: List[Team]) -> None:
        self.teams = teams
        self.deck = [Card(c, t, t if t <= 10 else 10)
                     for c, t in product(self.colors, self.types)]

    def is_game_over(self):
        return any(team.has_won() for team in self.teams)

    def get_shuffled_deck(self):
        shuffled_deck = self.deck.copy()
        shuffle(shuffled_deck)
        return shuffled_deck

    def distribute_cards(self, deck: List[Card], players: List[Player]) -> List[Card]:
        player_card_count = {2: 6, 3: 5, 4: 5, 6: 4}
        cribbage_initial_card_count = {2: 0, 3: 1, 4: 0, 6: 0}

        n = len(players)

        if player_card_count.get(n) is None:
            raise Exception("Number of player invalid")

        for player in players:
            player.assign_hand(deck[:player_card_count[n]])
            deck = deck[player_card_count[n]:]

        cribbage = deck[:cribbage_initial_card_count[n]]
        deck = deck[cribbage_initial_card_count[n]:]

        return cribbage

    def get_players(self) -> List[Player]:
        players = []
        for i in range(len(self.teams[0].players)):
            players.extend([team.players[i] for team in self.teams])
        return players

    def pick_hand(self, players: List[Player], cribbage: List[Card]):
        player_cribbage_card_drop_count = {2: 2, 3: 1, 4: 1, 6: 0}
        n = len(players)
        for player in players:
            cribbage.extend(player.drop(player_cribbage_card_drop_count[n]))

    def play(self, players: List[Player]):
        while any([len(player.play_hand) >= 0 for player in players]) and not self.is_game_over():
            self.play_round(players)

    def play_round(self, players):
        played_cards = []
        count = 0
        passed = set()

        while count < 31 and not self.is_game_over():
            player = players[0]
            self.rotate(players)
            card, score = player.play_card(played_cards, count)
            if card is None:
                passed.add(player)
            else:
                count += card.value
                player.score += score
                played_cards.append(card)
            if all([player in passed for player in players]):
                player.score += 0 if self.teams[player.team].can_pin() else 1
                break

    def rotate(self, players):
        players.append(players.pop(0))
        return players

    def play_game(self):
        state = "prep"
        deck = []
        cribbage = []
        cut = []
        players = []
        counting_index = 0

        while not self.is_game_over():
            if state == "prep":
                counting_index = 0

                deck = self.get_shuffled_deck()

                players = self.get_players()

                cribbage = self.distribute_cards(deck, players)

                self.pick_hand(players, cribbage)
                state = "cut"

            elif state == "cut":
                cut = choice(deck)
                if cut.type == "J":
                    players[0].score += 2
                state = "play"

            elif state == "play":
                self.play(players.copy())
                state = "count"

            elif state == "count":
                players[counting_index].score_hand(cut)
                if counting_index - 1 == len(players):
                    players[counting_index - 1].score_cribbage()
                    state == "end_round"
                counting_index += 1
            elif state == "end_round":
                self.rotate(players)
                state = "prep"
            print([team.score() for team in self.teams], state)

        print([f"end"])
