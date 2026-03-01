"""
player_db.py - Persistent player hand history database
Saves to player_history.json in the app directory.
"""

import json
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "player_history.json")


def _load():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}


def _save(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_all_players():
    """Return list of all player names."""
    return sorted(_load().keys())


def get_player_history(name):
    """Return list of hand records for a player."""
    db = _load()
    return db.get(name, [])


def log_hand(player_name, hole_cards, board_cards, pot_size=None, notes="", session_label=None):
    """
    Log a hand for a player.
    
    hole_cards: list of card strings like ['As', 'Kd']
    board_cards: list of card strings like ['Th', '7c', '2s', '4d', 'Jh']
    pot_size: float or None
    notes: str
    session_label: str label for the session (e.g. date or custom)
    """
    db = _load()
    if player_name not in db:
        db[player_name] = []

    record = {
        "timestamp": datetime.now().isoformat(),
        "session": session_label or datetime.now().strftime("%Y-%m-%d"),
        "hole_cards": hole_cards,
        "board_cards": board_cards,
        "pot_size": pot_size,
        "notes": notes,
    }
    db[player_name].append(record)
    _save(db)
    return record


def delete_player(name):
    db = _load()
    if name in db:
        del db[name]
        _save(db)


def delete_hand(player_name, hand_index):
    db = _load()
    if player_name in db and 0 <= hand_index < len(db[player_name]):
        db[player_name].pop(hand_index)
        _save(db)


def get_player_stats(name):
    """Compute simple stats from a player's hand history."""
    hands = get_player_history(name)
    if not hands:
        return None

    total = len(hands)
    pot_sizes = [h["pot_size"] for h in hands if h.get("pot_size")]
    avg_pot = round(sum(pot_sizes) / len(pot_sizes), 2) if pot_sizes else None

    # Count hand categories seen (requires evaluating — skipped here, just count hands)
    sessions = {}
    for h in hands:
        s = h.get("session", "Unknown")
        sessions[s] = sessions.get(s, 0) + 1

    return {
        "total_hands": total,
        "avg_pot": avg_pot,
        "sessions": sessions,
    }
