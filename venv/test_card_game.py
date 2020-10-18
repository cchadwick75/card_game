#tests lets get goingw2
import pytest
from card_game_play import *

def test_shuffle():
    pass
def test_build_deck():
    """
    Tests build_deck returns a list
    Tests list has proper length of items
    :return:
    """
    deck = build_deck()
    assert type(deck) == list
    assert len(deck) == 24


def test_get_random():
    """
    Tests that the random number doesnt exist in list
    :return:
    """
    deck = build_deck()
    test_card = draw_random_card(deck)
    assert test_card not in deck

def test_sort_order():
    ['Green, Blue']
    deck = build_deck()
    sorted = sort_cards(['Green, Blue'])


def test_shuffle():
    


