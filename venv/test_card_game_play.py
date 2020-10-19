"""
test_card_game_play - Random Functions tested from the card_game_play.py
Authored by Collin Chadwick
"""
import pytest
from card_game_play import (build_deck, draw_random_card, sort_cards,
                            shuffle_cards
                            )

def test_build_deck():
    """
    Tests build_deck returns a list
    Tests list has proper length of items
    :return:
    """
    deck = build_deck()
    assert isinstance(deck, list)
    assert len(deck) == 24

def test_get_random():
    """
    Tests that the random number doesnt exist in list and no duplicate cards
    :return:
    """
    test_card = []
    deck = build_deck()
    for _ in range(0, 10):
        test_card.append(draw_random_card(deck))
    assert len(set(test_card)) == len(test_card)
    assert test_card not in deck

def test_sort_order():
    """
    This tests the sort order by making sure the deck order doesnt match the sorted order
    :return:
    """
    deck = build_deck()
    sorted_deck = sort_cards(['Green, Blue'], deck)
    assert [a != b for a, b in zip(deck, sorted_deck)]
    assert len(sorted_deck) == len(deck)
    assert 'GREEN' in [x.card_color.name for x in sorted_deck]
    assert 'BLUE' in [x.card_color.name for x in sorted_deck]

def test_shuffle():
    """
    This tests the shuffle cards function and makes sure the cards arent in the same order
    :return:
    """
    deck = build_deck()
    shuffle_deck = shuffle_cards(deck)
    assert shuffle_deck != deck
    assert [a == b for a, b in zip(deck, shuffle_deck)]
