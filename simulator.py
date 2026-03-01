"""
simulator.py - Monte Carlo simulation engine for Texas Hold'em
"""

import random
import numpy as np
from treys import Card, Evaluator
from cards import all_52_cards, card_to_treys

evaluator = Evaluator()

HAND_CATEGORIES = [
    "High Card", "Pair", "Two Pair", "Trips",
    "Straight", "Flush", "Full House", "Quads", "Straight Flush"
]

# treys ranks: 1=Straight Flush, 2=Quads, 3=Full House, 4=Flush,
#              5=Straight, 6=Trips, 7=Two Pair, 8=Pair, 9=High Card
def treys_rank_to_category(rank):
    mapping = {
        1: "Straight Flush",
        2: "Quads",
        3: "Full House",
        4: "Flush",
        5: "Straight",
        6: "Trips",
        7: "Two Pair",
        8: "Pair",
        9: "High Card",
    }
    return mapping.get(rank, "High Card")

def simulate(hero_cards, board_cards, num_opponents, iterations=50000, opponent_known_cards=None):
    """
    Run Monte Carlo simulation.
    
    hero_cards: list of (rank, suit) tuples, length 2
    board_cards: list of (rank, suit) tuples, length 0-5
    num_opponents: int 1-8
    iterations: int
    opponent_known_cards: list of lists — known hole cards per opponent (can be empty lists)
    
    Returns dict with win%, tie%, lose%, hand_distribution
    """
    if opponent_known_cards is None:
        opponent_known_cards = [[] for _ in range(num_opponents)]

    # Pad or trim to match num_opponents
    while len(opponent_known_cards) < num_opponents:
        opponent_known_cards.append([])
    opponent_known_cards = opponent_known_cards[:num_opponents]

    wins = 0
    ties = 0
    losses = 0
    hand_counts = {cat: 0 for cat in HAND_CATEGORIES}

    # Pre-build set of fixed cards
    fixed_cards = set()
    for c in hero_cards:
        fixed_cards.add(f"{c[0]}{c[1]}")
    for c in board_cards:
        fixed_cards.add(f"{c[0]}{c[1]}")
    for opp_cards in opponent_known_cards:
        for c in opp_cards:
            fixed_cards.add(f"{c[0]}{c[1]}")

    all_cards = all_52_cards()
    deck_pool = [c for c in all_cards if f"{c[0]}{c[1]}" not in fixed_cards]

    hero_treys = [Card.new(card_to_treys(c)) for c in hero_cards]

    for _ in range(iterations):
        random.shuffle(deck_pool)
        draw_idx = 0

        # Fill board to 5
        sim_board = list(board_cards)
        while len(sim_board) < 5:
            sim_board.append(deck_pool[draw_idx])
            draw_idx += 1

        board_treys = [Card.new(card_to_treys(c)) for c in sim_board]

        # Deal opponents
        opp_hands_treys = []
        for opp_known in opponent_known_cards:
            hand = list(opp_known)
            while len(hand) < 2:
                hand.append(deck_pool[draw_idx])
                draw_idx += 1
            opp_hands_treys.append([Card.new(card_to_treys(c)) for c in hand])

        # Evaluate
        hero_score = evaluator.evaluate(board_treys, hero_treys)
        hero_rank = evaluator.get_rank_class(hero_score)
        hand_counts[treys_rank_to_category(hero_rank)] += 1

        # Lower score = better hand in treys
        best_opp_score = min(evaluator.evaluate(board_treys, opp) for opp in opp_hands_treys)

        if hero_score < best_opp_score:
            wins += 1
        elif hero_score == best_opp_score:
            ties += 1
        else:
            losses += 1

    total = iterations
    hand_distribution = {cat: round(hand_counts[cat] / total * 100, 1) for cat in HAND_CATEGORIES}

    return {
        "win": round(wins / total * 100, 1),
        "tie": round(ties / total * 100, 1),
        "lose": round(losses / total * 100, 1),
        "hand_distribution": hand_distribution,
        "iterations": total,
    }
