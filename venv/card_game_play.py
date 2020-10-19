"""
Name : card_game_play
Description:  This is a card game that will support three operations
1. Shuffle cards in the deck:
2. Get Card from the top of the deck:
3. Sort Cards from top of the deck
4. 2 - Players draw cards taking turns


"""
from random import (random,randint)
from enum import Enum
import sys
import operator
import time


FULL_DECK = []
PARTIAL_DECK = []
SHUFFLE_DECK = []
SORT_DECK = []
COLORLIST = []
DECK_COPY = []

class Player:
    """
    Player object sets the player attributes needed
    """
    name = ''
    hand = []
    totals = 0

class CardNum(Enum):
    """
    Sets the card number for the deck of cards
    """
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7

class CardColor(Enum):
    """
    Sets color and card amount associated of card deck
    """
    BLUE = 4
    RED = 3
    YELLOW = 2
    GREEN = 1


class CardPlay:
    """
    CardPlay sets the value and color of object.
    """
    def __init__(self, value, color):
        self.card_value = value
        self.card_color = color

def build_deck() -> list:
    """
    This build the deck by using the CardPlay object and appending to the deck
    :return: full_deck list.  This is the original list
    """
    for color in CardColor:
        for num in CardNum:
            FULL_DECK.append(CardPlay(CardNum(num), CardColor(color)))

    return FULL_DECK

def draw_random_card(deck:list) -> object:
    """
    Picks and removes random card from deck and returns that card
    :param deck: This passes a copy of the deck so we dont lose original deck
    :return: random card object
    """
    try:
        rand_card = randint(0, len(deck) -1)
        return deck.pop(rand_card)
    except Exception as deck_error:
        return [f"Error: {deck_error}"]

def shuffle_cards(deck:list) -> list:
    """
    shuffles deck at random and returns the shuffled list.
    :param deck:
    :return: shuffled deck
    """
    
    return sorted(deck, key=lambda k: random())

def sort_cards(sorter:list, sort_list:list) -> list:
    """
    sort_cards takes 2 parameters and sort criteria and the list to be sorted.
    :param sort_by:
    :param sort_list:
    :return: list sorted by criteria
    """
    result = [obj for x in sorter for obj in sort_list if obj.card_color.name == x.strip()]
    result_sorted = sorted(result, key=operator.attrgetter('card_color.name','card_value.value'))
    for obj in sort_list:
        if obj not in result_sorted:
            result_sorted.append(obj)
    return result_sorted

def calculate_totals(player1, player2):
    """
    This takes 2 player objects and calculates the totals of the players cards and displays winner
    :param player1:
    :param player2:
    :return:
    """
    print("Game Is Over")
    player1.totals = sum([x.card_color.value * x.card_value.value for x in player1.hand])
    player2.totals = sum([x.card_color.value * x.card_value.value for x in player2.hand])
    print(f"{player1.name}: {player1.totals}")
    print('')
    print('')
    print(f"{player2.name}: {player2.totals}")
    print('')
    print('')
    if player1.totals > player2.totals:
        print(f"{player1.name} Wins")
    elif player1.totals < player2.totals:
        print(f"{player2.name} Wins")
    else:
        print(f"YOU TIED!")

def play(DECK_COPY):
    """
    play performs the actual interactive game logic

    :param number_of_players:
    :return: None
    """
    player1 = Player()
    player1.name = input("Player 1 Enter Your Name:  ")
    player1.hand = []
    number_of_players = input(f"Select 1 Player or 2 Players : type 1 or 2 ")
    #this loop handles bad SELECTION.
    while number_of_players:

        if number_of_players == '2':
            player2 = Player()
            player2.name = input("Player 2 Enter Your Name:  ")
            print("2 Player:  EACH player will need to select card from deck")
            break
        elif number_of_players == '1':
            player2 = Player()
            player2.name = 'Windows 95'
            player2.hand = []
            break
        else:
            number_of_players = input(f"Try AGAIN:  type 1 or 2 ")
    print('')
    print('')
    print(f"Player 1: {player1.name} vs Player 2: {player2.name}")

    while len(player1.hand) < 3 and len(player2.hand) < 3:
        print('')
        print('')
        player1_draw = input(f"{player1.name}, select a card.  Type Y to Draw from Deck:  ")

        while player1_draw.upper() not in ['Y', 'N']:
            player1_draw = input(f"Invalid Selection {player1.name}: Type Y to Draw or N to Quit: ")

        if player1_draw.upper() == 'Y':
            player1.hand.append(draw_random_card(DECK_COPY))
            time.sleep(1)
            player1_detail = [(card.card_color.name, card.card_value.value) for card in player1.hand]
            print(f"{player1.name}'s hand:")
            print(f"{player1_detail}")
        elif player1_draw.upper() == 'N':
            print('')
            print('')
            print('Game is exiting')
            time.sleep(2)
            sys.exit()
        else:
            print('')
        if number_of_players == '2':
            player2_draw = input(f"{player2.name}, select a card.  Type Y to Draw from Deck:  ")
            while player1_draw.upper() not in ['Y', 'N']:
                player2_draw = input(f"Invalid Selection {player2.name}: Type Y to Draw or N to Quit: ")
        else:
            player2_draw = 'Y'

        if player2_draw.upper() == 'Y':
            player2.hand.append(draw_random_card(DECK_COPY))
            time.sleep(1)
            player2_detail = [(card.card_color.name, card.card_value.value) for card in player2.hand]
            print(f"{player2.name}'s hand:")
            print(f"{player2_detail}")
        elif player2_draw.upper() == 'N':
            print('')
            print('')
            print('Game is exiting')
            time.sleep(2)
            sys.exit()
    else:
        calculate_totals(player1, player2)



def main():
    """
    This is the main function that will run the game process
    :return:
    """
    play_game = input("PLay Color Cards?  : (y/n) : ")

    if play_game.upper() == 'Y':
        build_deck()
        PARTIAL_DECK = shuffle_cards(FULL_DECK)
        sort_list = input("Sort deck by color specific colors : Y/N")
        if sort_list.upper() == 'Y':
            COLORLIST = input("Type Colors:  Choices(BLUE GREEN RED YELLOW): separate by comma ")
            COLORLIST = list(COLORLIST.upper().split(","))
            SORT_DECK = sort_cards(COLORLIST, PARTIAL_DECK)
            print(f"here is your sorted deck: {[(card.card_color.name, card.card_value.value) for card in SORT_DECK]}")
            DECK_COPY = list(SORT_DECK)
        else:    
            DECK_COPY = list(FULL_DECK)
        play(DECK_COPY)
    elif play_game.upper() == 'N':
        print("Comeback when you are ready to play!  Game will end in 5 seconds.")
        time.sleep(5)
        sys.exit()
    else:
        print(f"You entered {play_game.upper()}!  It seems you arent that serious about playing. "
              f" Game will end in 5 seconds.")
        time.sleep(5)
        sys.exit()

if __name__ == '__main__':
    main()
