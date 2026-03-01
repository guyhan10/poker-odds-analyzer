"""
cards.py - Card parsing and validation helpers
"""

VALID_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
VALID_SUITS = ['h', 'd', 'c', 's']

RANK_DISPLAY = {
    '2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
    '7': '7', '8': '8', '9': '9', 'T': '10',
    'J': 'J', 'Q': 'Q', 'K': 'K', 'A': 'A'
}

SUIT_DISPLAY = {
    'h': '♥', 'd': '♦', 'c': '♣', 's': '♠'
}

SUIT_COLOR = {
    'h': '#e74c3c', 'd': '#e74c3c', 'c': '#2ecc71', 's': '#95a5a6'
}

def parse_card(card_str):
    """Parse a card string like 'As' or 'Th'. Returns (rank, suit) or None."""
    card_str = card_str.strip()
    if len(card_str) == 2:
        rank = card_str[0].upper()
        suit = card_str[1].lower()
        if rank in VALID_RANKS and suit in VALID_SUITS:
            return (rank, suit)
    # Handle '10h' style
    if len(card_str) == 3 and card_str[:2] == '10':
        rank = 'T'
        suit = card_str[2].lower()
        if suit in VALID_SUITS:
            return (rank, suit)
    return None

def parse_cards(cards_str):
    """Parse comma-separated card string. Returns (list_of_cards, error_message)."""
    if not cards_str or not cards_str.strip():
        return [], None
    
    parts = [p.strip() for p in cards_str.split(',') if p.strip()]
    cards = []
    for part in parts:
        card = parse_card(part)
        if card is None:
            return None, f"Invalid card: '{part}'. Use format like As, Kh, Td, 2c"
        cards.append(card)
    return cards, None

def card_to_treys(card):
    """Convert (rank, suit) tuple to treys string format."""
    rank, suit = card
    return rank + suit

def cards_to_treys(cards):
    """Convert list of (rank, suit) tuples to treys string list."""
    return [card_to_treys(c) for c in cards]

def validate_no_duplicates(hero_cards, board_cards, opponent_cards_list=None):
    """Check for duplicate cards across all card sets. Returns error string or None."""
    all_cards = list(hero_cards) + list(board_cards)
    if opponent_cards_list:
        for opp_cards in opponent_cards_list:
            all_cards.extend(opp_cards)
    
    seen = set()
    for card in all_cards:
        key = f"{card[0]}{card[1]}"
        if key in seen:
            return f"Duplicate card: {RANK_DISPLAY[card[0]]}{SUIT_DISPLAY[card[1]]}"
        seen.add(key)
    return None

def card_display(card):
    """Return display string for a card tuple."""
    rank, suit = card
    return f"{RANK_DISPLAY[rank]}{SUIT_DISPLAY[suit]}"

def cards_display(cards):
    """Return display string for list of card tuples."""
    return " ".join(card_display(c) for c in cards)

def all_52_cards():
    """Return all 52 cards as (rank, suit) tuples."""
    return [(r, s) for r in VALID_RANKS for s in VALID_SUITS]
