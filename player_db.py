"""
player_db.py - Player hand history with JSON export/import for persistence.

On Streamlit Cloud, data lives in session. Use the Export button to save
your history as a JSON file, and Import to reload it next session.

For local use, also saves to player_history.json automatically.
"""

import streamlit as st
import json
import os
from datetime import datetime

LOCAL_FILE = "player_history.json"


def _init():
    """Initialize the in-memory store, loading from file if available locally."""
    if "_player_db" not in st.session_state:
        # Try local file first (works when running locally)
        if os.path.exists(LOCAL_FILE):
            try:
                with open(LOCAL_FILE, "r") as f:
                    st.session_state["_player_db"] = json.load(f)
                return
            except Exception:
                pass
        st.session_state["_player_db"] = {}


def _load():
    _init()
    return st.session_state["_player_db"]


def _save(data):
    st.session_state["_player_db"] = data
    # Also try writing to local file (works when running locally)
    try:
        with open(LOCAL_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass  # On Streamlit Cloud this is expected to fail silently


def get_all_players():
    return sorted(_load().keys())


def get_player_history(name):
    return _load().get(name, [])


def log_hand(player_name, hole_cards, board_cards, pot_size=None, notes="", session_label=None):
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
    hands = get_player_history(name)
    if not hands:
        return None

    total = len(hands)
    pot_sizes = [h["pot_size"] for h in hands if h.get("pot_size")]
    avg_pot = round(sum(pot_sizes) / len(pot_sizes), 2) if pot_sizes else None

    sessions = {}
    for h in hands:
        s = h.get("session", "Unknown")
        sessions[s] = sessions.get(s, 0) + 1

    return {
        "total_hands": total,
        "avg_pot": avg_pot,
        "sessions": sessions,
    }


def export_json():
    """Return the full database as a JSON string for download."""
    return json.dumps(_load(), indent=2)


def import_json(json_str):
    """Load database from a JSON string. Returns (success, error_message)."""
    try:
        data = json.loads(json_str)
        if not isinstance(data, dict):
            return False, "Invalid format — expected a JSON object."
        _save(data)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
