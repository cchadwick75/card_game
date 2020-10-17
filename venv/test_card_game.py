#tests lets get goingw2
import pytest
from card_game_play import build_deck

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
    pass
def test_sort_order():
    pass


