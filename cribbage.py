from itertools import product, combinations, chain
from collections import Counter
from random import choice, shuffle
import numpy as np


class Card:
    def __init__(self, color, type, value) -> None:
        self.color = color
        self.type = type
        self.value = value


colors = ["spades", "hearts", "diamonds", "clubs"]
types = list(range(1, 14))

deck = [Card(c, t, t if t <= 10 else 10) for c, t in product(colors, types)]


def point_paires(hand, cut):
    points_ref = {1: 0, 2: 2, 3: 6, 4: 12}
    cards = [c.type for c in hand]
    cards.append(cut.type)
    points = 0
    for value in Counter(cards).values():
        points += points_ref[value]
    return points


def point_15(hand, cut):
    cards = [c.value for c in hand]
    cards.append(cut.value)

    def powerset(iterable):
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(2, len(s)+1))

    points = 0
    for cards_set in powerset(cards):
        points += 2 if np.sum(cards_set) == 15 else 0
    return points


def point_colors(hand, cut):
    points = 0
    if len(set([c.color for c in hand])) == 1:
        points += 5 if cut.color == hand[0].color else 4
    return points


def point_straight(hand, cut):
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


def point_jack_color(hand, cut):
    jacks = [c for c in hand if c.type == 11]
    for jack in jacks:
        if jack.color == cut.color:
            return 1
    return 0


def score_hand(hand, cut):
    score_methods = [point_straight, point_colors,
                     point_15, point_paires, point_jack_color]
    return np.sum([m(hand, cut) for m in score_methods])


def check_score(hand, s, score):
    for c in hand:
        if c.value + s == score:
            return (c, 2)
    return (None, 0)


def check_15(hand, played_cards, s):
    return check_score(hand, s, 15)


def check_31(hand, played_cards, s):
    return check_score(hand, s, 31)


def check_double(hand, played_cards, s):
    max = 0
    card = None
    for c in hand:
        point = point_paires(played_cards, c)
        if point > max:
            max = point
            card = c
    return (card, max)


def check_straight(hand, played_cards, s):
    if len(played_cards) < 2:
        return (None, 0)
    for c in hand:
        point = point_straight(played_cards, c)
        if point > 0:
            return (c, point)
    return (None, 0)


def check_playable_hand(hand, s):
    return [c for c in hand if c.value + s <= 31]


def check_playable_card(card, s):
    return card.value + s <= 31


def check_cards(hand, played_cards, s):
    if len(hand) == 0:
        return (None, 0)
    playable_hand = check_playable_hand(hand, s)
    if len(playable_hand) == 0:
        return (None, 0)

    check_score_func = check_15 if s <= 15 else check_31
    plays = [check_score_func, check_straight, check_double]
    plays = [play(playable_hand, played_cards, s) for play in plays]
    plays = [play for play in plays if play[0] is not None]
    if len(plays) == 0:
        return choice([(card, 0) for card in playable_hand])
    plays = [(play, score + check_score_func([play], played_cards, s)[1])
             for play, score in plays]
    return max(plays, key=lambda x: x[1])


class Player:
    def __init__(self, team) -> None:
        self.team = team
        self.score = 0
        self.hand = []
        self.play_hand = []


red = Player("red")
blue = Player("blue")
cribbage_player = blue
starting_player = red

while red.score < 121 and blue.score < 121:
    current_deck = deck.copy()
    shuffle(current_deck)

    blue.hand = current_deck[:6]
    red.hand = current_deck[6:12]

    cribbage = blue.hand[:2] + red.hand[:2]

    blue.hand = blue.hand[2:]
    red.hand = red.hand[2:]

    current_deck = current_deck[12:]

    cut = choice(current_deck)

    if cut.type == 11:
        cribbage_player.score += 2
        if cribbage_player.score >= 121:
            break

    blue.play_hand = blue.hand.copy()
    red.play_hand = red.hand.copy()

    players = [starting_player, cribbage_player]

    while len(blue.play_hand) > 0 or len(red.play_hand) > 0:
        played_cards = []
        s = 0
        pass_count = 0
        while s < 31:
            player = players.pop(0)
            card, score = check_cards(player.play_hand, played_cards, s)
            if card is not None:
                s += card.value
                player.score += score
                player.play_hand.remove(card)
            else:
                pass_count += 1

            players.append(player)
            if player.score >= 121:
                break
            if pass_count == 2:
                player.score += 0 if player.score >= 115 else 1
                break

    if red.score >= 121 or blue.score >= 121:
        break

    starting_player.score += score_hand(starting_player.hand, cut)
    if starting_player.score >= 121:
        break
    cribbage_player.score += score_hand(cribbage_player.hand, cut)
    if cribbage_player.score >= 121:
        break
    cribbage_player.score += score_hand(cribbage, cut)
    if cribbage_player.score >= 121:
        break

    print(f"cribbage {cribbage_player.team}")
    print(f"red {red.score}", f"blue {blue.score}")

    tmp = cribbage_player
    cribbage_player = starting_player
    starting_player = tmp

print(f"cribbage {cribbage_player.team}")
print(f"red {red.score}", f"blue {blue.score}")
