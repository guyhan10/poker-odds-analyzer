# 🃏 Poker Odds Analyzer

Texas Hold'em equity calculator with player hand history tracking.

## Setup (do this once)

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## How to Use

### Tab 1 — ODDS CALCULATOR
- Enter your 2 hole cards (e.g. `As, Kd`)
- Enter board cards if any are showing (e.g. `Kh, 7d, 2c`)
- Set number of opponents
- Optionally enter known opponent cards (if you can see them)
- Click **CALCULATE ODDS**

### Tab 2 — LOG A HAND
After each hand when cards are revealed at showdown:
- Enter the session name (e.g. "Friday Night")
- Enter the final board
- Enter each player's name + hole cards
- Add notes if you want (e.g. "Dave bluffed with nothing")
- Click **SAVE**

### Tab 3 — PLAYER HISTORY
- Select a player to see all their logged hands
- Shows stats: total hands, average pot, sessions played
- Hands grouped by session, newest first
- Can delete a player's history if needed

---

## Card Format

| Card | How to type |
|------|-------------|
| Ace of Spades | `As` |
| King of Hearts | `Kh` |
| Ten of Diamonds | `Td` |
| 2 of Clubs | `2c` |

Ranks: 2 3 4 5 6 7 8 9 T J Q K A  
Suits: h (hearts) d (diamonds) c (clubs) s (spades)

---

## Data Storage

Player history is saved to `player_history.json` in this folder.
It persists between sessions automatically — no database needed.

---

## Using as a PokerNow Overlay

Keep this app open in a browser window alongside your PokerNow tab.
In Windows you can use **Snap Assist** (Win+Left/Right arrow) to tile them.
On Mac, use Split View or a tool like Magnet to tile windows.

For a true floating overlay, a future Chrome extension version can be built on top of this.
