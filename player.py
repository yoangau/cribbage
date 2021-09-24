from collections import Counter
from itertools import chain, combinations
from random import choice
from typing import List, Tuple

import numpy as np
from card import Card


class Player:
    points_ref = {1: 0, 2: 2, 3: 6, 4: 12}

    def __init__(self, team) -> None:
        self.score = 0
        self.team = team
        self.hand: List[Card] = []
        self.play_hand: List[Card] = []

    def assign_hand(self, hand):
        self.hand = hand

    def drop(self, n):
        drop = self.hand[:n]
        self.hand = self.hand[n:]
        self.play_hand = self.hand.copy()
        return drop

    def play_card(self, played_cards, count) -> Tuple[Card, int]:
        if len(self.hand) == 0:
            return (None, 0)
        playable_hand = self.__check_playable_hand(count)
        if len(playable_hand) == 0:
            return (None, 0)

        # TODO: NE PAS CALCULER DEUX FOIS LES 15 sinon 4 points
        check_score_func = self.__check_15 if count < 15 else self.__check_31
        plays = [self.__check_straight, self.__check_double]
        plays = [play(playable_hand, played_cards, count)
                 for play in plays]
        plays = [play for play in plays if play[0] is not None]
        if len(plays) == 0:
            c = choice([(card, 0) for card in playable_hand])
            self.play_hand.remove(c[0])
            return c
        plays = [(play, score + check_score_func([play], played_cards, count)[1])
                 for play, score in plays]
        card, score = max(plays, key=lambda x: x[1])
        self.play_hand.remove(card)
        return (card, score)

    def score_hand(self, cut):
        self.score += self.__score_hand(self.hand, cut)

    def score_cribbage(self, cribbage, cut):
        self.score += self.__score_hand(cribbage, cut)

    def __point_paires(self, hand, cut):
        cards = [c.type for c in hand]
        cards.append(cut.type)
        points = 0
        for value in Counter(cards).values():
            points += Player.points_ref[value]
        return points

    def __point_15(self, hand, cut):
        cards = [c.value for c in hand]
        cards.append(cut.value)

        def powerset(iterable):
            s = list(iterable)
            return chain.from_iterable(combinations(s, r) for r in range(2, len(s)+1))

        points = 0
        for cards_set in powerset(cards):
            points += 2 if np.sum(cards_set) == 15 else 0
        return points

    def __point_colors(self, hand, cut):
        points = 0
        if len(set([c.color for c in hand])) == 1:
            points += 5 if cut.color == hand[0].color else 4
        return points

    def __point_straight(self, hand, cut):
        cards = [c.type for c in hand]
        cards.append(cut.type)

        sorted_cards = sorted(Counter(cards).items())

        last = sorted_cards.pop(0)
        l = 1
        mul = last[1]
        for type, count in sorted_cards:
            if type - last[0] > 1 and l < 3:
                l = 1
                mul = count
            else:
                mul *= count
                l += 1
            last = (type, count)
        return l * mul if l >= 3 else 0

    def __point_jack_color(self, hand, cut):
        jacks = [c for c in hand if c.type == 11]
        for jack in jacks:
            if jack.color == cut.color:
                return 1
        return 0

    def __score_hand(self, hand, cut):
        score_methods = [self.__point_straight, self.__point_colors,
                         self.__point_15, self.__point_paires, self.__point_jack_color]
        return np.sum([m(hand, cut) for m in score_methods])

    def __check_score(self, hand, count, score):
        for c in hand:
            if c.value + count == score:
                return (c, 2)
        return (None, 0)

    def __check_15(self, hand, played_cards, count):
        return self.__check_score(hand, count, 15)

    def __check_31(self, hand, played_cards, count):
        return self.__check_score(hand, count, 31)

    def __check_double(self, hand, played_cards, count):
        if len(played_cards) == 0:
            return (None, 0)
        for c in hand:
            qty = 1
            for pc in reversed(played_cards.copy()):
                if pc.type != c.type:
                    break
                else:
                    qty += 1

            if qty > 1:
                return (c, Player.points_ref[qty])

        return (None, 0)

    def __check_straight(self, hand, played_cards, count):
        if len(played_cards) < 2:
            return (None, 0)
        for c in hand:
            l = [c.type]
            for pc in reversed([card.type for card in played_cards]):
                l.append(pc)
                if len(l) < 3:
                    continue
                sl = sorted(l)
                last = sl.pop(0)
                length = 1
                for t in sl:
                    if t - last != 1:
                        break
                    length += 1
                    last = t
                if length >= 3:
                    return(c, length)
        return (None, 0)

    def __check_playable_hand(self, count):
        return [c for c in self.play_hand if c.value + count <= 31]

    def __check_playable_card(self, card, count):
        return card.value + count <= 31
