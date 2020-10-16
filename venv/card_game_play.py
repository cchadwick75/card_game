"""
Name : card_game_play
Description:  This is a card game that will support three operations
1. Shuffle cards in the deck:
2. Get Card from the top of the deck:
3. Sort Cards from top of the deck
4. 2 - Players draw cards taking turns


"""
from random import choice, shuffle
from enum import IntEnum, Enum

full_deck = []



class CardNum(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class CardSuit(Enum):
    """

    """
    SPADES = 'spades'
    HEARTS = 'hearts'
    DIAMONDS = 'diamonds'
    CLUBS = 'clubs'



class CardPlay:
    def __init__(self, value, suit):
        self.card_value = value
        self.card_suit = suit

fulldecker = [CardPlay(CardNum(num), CardSuit(suit)) for suit in CardSuit for num in CardNum ]

def build_deck() -> list:
    for suit in CardSuit:
        for num in CardNum:
            full_deck.append(CardPlay(CardNum(num), CardSuit(suit)))
    return full_deck

def draw_random_card(deck:list) -> list:
    random_card = deck.randint(0, len(deck)-1)
    return deck.pop(random_card)




