"""
app.py - Texas Hold'em Poker Odds Analyzer with Live Hand Tracker
Run with: streamlit run app.py
"""

import streamlit as st
import time
from cards import parse_cards, validate_no_duplicates, RANK_DISPLAY, SUIT_DISPLAY
from simulator import simulate, HAND_CATEGORIES
from player_db import (
    get_all_players, get_player_history, log_hand,
    delete_player, get_player_stats,
    export_json, import_json
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Poker Odds Analyzer",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

  :root {
    --green:  #1a7a4a;
    --green2: #22a060;
    --gold:   #c9a84c;
    --red:    #c0392b;
    --dark:   #0a1f14;
    --card:   #f5f0e8;
    --text:   #e8f0eb;
    --muted:  #7a9e87;
  }

  html, body, [data-testid="stAppViewContainer"] {
    background: var(--dark);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
  }
  [data-testid="stMain"] {
    background: radial-gradient(ellipse at 50% 0%, #1a4a30 0%, var(--dark) 70%);
  }

  .poker-header {
    text-align: center;
    padding: 1.2rem 0 0.3rem;
    font-family: 'Bebas Neue', cursive;
    font-size: 2.6rem;
    letter-spacing: 4px;
    color: var(--gold);
    text-shadow: 0 0 30px rgba(201,168,76,0.4);
  }
  .poker-sub {
    text-align: center;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 2px;
    margin-bottom: 1.5rem;
  }

  [data-testid="stTabs"] button {
    font-family: 'DM Mono', monospace !important;
    letter-spacing: 1px;
    color: var(--muted) !important;
    border-bottom: 2px solid transparent !important;
  }
  [data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
  }

  .card-chip {
    display: inline-block;
    background: var(--card);
    border-radius: 6px;
    padding: 4px 10px;
    margin: 2px;
    font-family: 'DM Mono', monospace;
    font-size: 1.05rem;
    font-weight: 700;
    color: #1a1a1a;
    box-shadow: 0 2px 8px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.8);
  }
  .card-chip.red  { color: #c0392b; }
  .card-chip.back { background: #1a4a30; color: #7a9e87; border: 1px dashed #3a6a50; font-size: 0.9rem; }

  .street-badge {
    display: inline-block;
    font-family: 'Bebas Neue', cursive;
    font-size: 0.85rem;
    letter-spacing: 3px;
    padding: 3px 14px;
    border-radius: 20px;
    margin-bottom: 0.8rem;
  }
  .street-preflop { background: rgba(201,168,76,0.15); color: var(--gold);   border: 1px solid rgba(201,168,76,0.3); }
  .street-flop    { background: rgba(34,160,96,0.15);  color: #2ecc71;       border: 1px solid rgba(34,160,96,0.3); }
  .street-turn    { background: rgba(52,152,219,0.15); color: #5dade2;       border: 1px solid rgba(52,152,219,0.3); }
  .street-river   { background: rgba(192,57,43,0.15);  color: #e74c3c;       border: 1px solid rgba(192,57,43,0.3); }

  .odds-row { display: flex; gap: 0.5rem; margin: 0.8rem 0; }
  .odds-box {
    flex: 1;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
  }
  .odds-label { font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 2px; color: var(--muted); margin-bottom: 0.3rem; }
  .odds-value { font-family: 'Bebas Neue', cursive; font-size: 2.6rem; line-height: 1; }
  .odds-win  { color: #2ecc71; }
  .odds-tie  { color: var(--gold); }
  .odds-lose { color: var(--red); }

  .pot-display {
    background: rgba(201,168,76,0.08);
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    text-align: center;
    margin: 0.5rem 0;
  }
  .pot-label { font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 2px; color: var(--muted); }
  .pot-value { font-family: 'Bebas Neue', cursive; font-size: 2rem; color: var(--gold); }

  .action-log {
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    line-height: 1.9;
    max-height: 160px;
    overflow-y: auto;
  }
  .action-fold  { color: var(--red); }
  .action-call  { color: #5dade2; }
  .action-raise { color: var(--gold); }

  .player-row {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    padding: 0.5rem 0.8rem;
    margin: 4px 0;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
  }
  .player-row.folded { opacity: 0.35; }
  .player-name { flex: 1; color: var(--text); }

  .section-head {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 3px;
    color: var(--gold);
    text-transform: uppercase;
    border-bottom: 1px solid rgba(201,168,76,0.2);
    padding-bottom: 0.3rem;
    margin: 1rem 0 0.6rem;
  }

  .dist-bar-wrap { display: flex; align-items: center; gap: 10px; margin: 3px 0; font-family: 'DM Mono', monospace; font-size: 0.72rem; }
  .dist-label { width: 100px; color: var(--muted); text-align: right; flex-shrink: 0; }
  .dist-bar-bg { flex: 1; background: rgba(255,255,255,0.05); border-radius: 3px; height: 14px; }
  .dist-bar-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, var(--green), var(--green2)); }
  .dist-pct { width: 40px; color: var(--text); }

  .hand-record {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid var(--green);
    border-radius: 0 6px 6px 0;
    padding: 0.5rem 0.8rem;
    margin: 0.3rem 0;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
  }

  label { color: var(--muted) !important; font-family: 'DM Mono', monospace !important; font-size: 0.72rem !important; letter-spacing: 1px !important; }
  input[type="text"], input[type="number"] { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: var(--text) !important; font-family: 'DM Mono', monospace !important; border-radius: 6px !important; }
  [data-testid="stSelectbox"] > div > div { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; color: var(--text) !important; }

  .stButton > button {
    background: linear-gradient(135deg, var(--green), var(--green2)) !important;
    color: white !important; border: none !important; border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important; letter-spacing: 1px !important;
    font-weight: 500 !important; transition: all 0.2s !important;
  }
  .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 15px rgba(34,160,96,0.4) !important; }

  footer { display: none; }
  #MainMenu { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def card_chip(card_str):
    if not card_str or card_str == "??":
        return '<span class="card-chip back">??</span>'
    rank = card_str[0].upper()
    suit = card_str[1].lower()
    color = "red" if suit in ('h', 'd') else ""
    r = RANK_DISPLAY.get(rank, rank)
    s = SUIT_DISPLAY.get(suit, suit)
    return f'<span class="card-chip {color}">{r}{s}</span>'

def chips_html(card_list):
    return " ".join(card_chip(c) for c in card_list)

def street_badge_html(street):
    labels = {"preflop": ("PRE-FLOP", "preflop"), "flop": ("FLOP", "flop"),
              "turn": ("TURN", "turn"), "river": ("RIVER", "river")}
    text, cls = labels.get(street, ("PRE-FLOP", "preflop"))
    return f'<span class="street-badge street-{cls}">{text}</span>'

def get_street(board_len):
    return {0: "preflop", 3: "flop", 4: "turn", 5: "river"}.get(board_len, "preflop")

def run_simulation(hand_state, iters):
    """Run simulation from current hand state. Returns result dict."""
    active_opps = [o for o in hand_state["opponents"] if not o["folded"]]
    if not active_opps:
        return None
    opp_cards_parsed = []
    for o in active_opps:
        if o["cards"]:
            parsed, _ = parse_cards(", ".join(o["cards"]))
            opp_cards_parsed.append(parsed)
        else:
            opp_cards_parsed.append([])
    hero_p, _ = parse_cards(", ".join(hand_state["hero_cards"]))
    board_p, _ = parse_cards(", ".join(hand_state["board_cards"])) if hand_state["board_cards"] else ([], None)
    return simulate(hero_p, board_p, len(active_opps), iters, opp_cards_parsed)

# ── Session state ─────────────────────────────────────────────────────────────
def init_hand():
    st.session_state.hand = {
        "hero_cards": [],
        "board_cards": [],
        "opponents": [],
        "pot": 0.0,
        "action_log": [],
        "result": None,
        "street": "preflop",
        "session_label": "",
    }
    st.session_state["iters"] = 50000

if "hand" not in st.session_state:
    init_hand()

H = st.session_state.hand

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="poker-header">🃏 Poker Odds Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="poker-sub">LIVE HAND TRACKER · TEXAS HOLD\'EM · MONTE CARLO</div>', unsafe_allow_html=True)

tab_live, tab_log, tab_players = st.tabs([
    "  LIVE HAND  ",
    "  LOG SHOWDOWN  ",
    "  PLAYER HISTORY  ",
])

# ════════════════════════════════════════════════════════════════
# TAB 1 — LIVE HAND TRACKER
# ════════════════════════════════════════════════════════════════
with tab_live:
    left, right = st.columns([1, 1], gap="large")
    hand_started = bool(H["hero_cards"])

    with left:
        # ── SETUP ────────────────────────────────────────────────────────────
        if not hand_started:
            st.markdown('<div class="section-head">NEW HAND — SETUP</div>', unsafe_allow_html=True)
            hero_input    = st.text_input("Your hole cards", placeholder="As, Kd")
            session_input = st.text_input("Session name (optional)", placeholder="Friday Night")

            st.markdown('<div class="section-head">OPPONENTS</div>', unsafe_allow_html=True)
            n_opp = st.number_input("Number of opponents", 1, 8, 3)
            opp_inputs = []
            for i in range(int(n_opp)):
                c1, c2 = st.columns([1, 2])
                with c1:
                    nm = st.text_input(f"Opp {i+1} name", placeholder=f"Player {i+1}", key=f"setup_opp_name_{i}")
                with c2:
                    cd = st.text_input(f"Cards (optional)", placeholder="blank = unknown", key=f"setup_opp_cards_{i}")
                opp_inputs.append((nm.strip() or f"Player {i+1}", cd.strip()))

            st.markdown('<div class="section-head">SIMULATION</div>', unsafe_allow_html=True)
            iters = st.select_slider("Iterations", [5000, 10000, 20000, 50000, 100000], value=50000)
            if iters < 20000:
                st.warning("⚠️ Low iterations — results may vary.")

            if st.button("▶  START HAND", use_container_width=True):
                hero_cards, herr = parse_cards(hero_input)
                if herr or len(hero_cards) != 2:
                    st.error(herr or "Enter exactly 2 hole cards.")
                    st.stop()

                opponents, opp_known = [], []
                err_found = False
                for nm, cd in opp_inputs:
                    if cd:
                        cards, cerr = parse_cards(cd)
                        if cerr or len(cards) != 2:
                            st.error(f"{nm}: {cerr or 'Need exactly 2 cards or leave blank.'}")
                            err_found = True
                            break
                        opp_known.append(cards)
                        opponents.append({"name": nm, "cards": [f"{r}{s}" for r,s in cards], "folded": False})
                    else:
                        opp_known.append([])
                        opponents.append({"name": nm, "cards": [], "folded": False})

                if err_found:
                    st.stop()

                dup_err = validate_no_duplicates(hero_cards, [], opp_known)
                if dup_err:
                    st.error(dup_err)
                    st.stop()

                H["hero_cards"]    = [f"{r}{s}" for r,s in hero_cards]
                H["opponents"]     = opponents
                H["board_cards"]   = []
                H["pot"]           = 0.0
                H["action_log"]    = ["● Hand started — pre-flop"]
                H["street"]        = "preflop"
                H["session_label"] = session_input
                st.session_state["iters"] = iters
                H["result"] = run_simulation(H, iters)
                st.rerun()

        # ── HAND IN PROGRESS ─────────────────────────────────────────────────
        else:
            street   = get_street(len(H["board_cards"]))
            H["street"] = street
            iters    = st.session_state.get("iters", 50000)
            board_len = len(H["board_cards"])

            st.markdown(street_badge_html(street), unsafe_allow_html=True)

            # Deal next street
            if board_len < 5:
                next_map = {0: ("Flop (3 cards)", "Ah, Kd, 7c", 3),
                            3: ("Turn card", "2s", 1),
                            4: ("River card", "Jh", 1)}
                label, placeholder, expected = next_map[board_len]
                new_board_input = st.text_input(f"Deal {label}", placeholder=placeholder, key=f"board_input_{board_len}")

                if st.button(f"▶  DEAL {label.upper()}", use_container_width=True, key=f"btn_deal_{board_len}"):
                    new_cards, cerr = parse_cards(new_board_input)
                    if cerr:
                        st.error(cerr)
                        st.stop()
                    if len(new_cards) != expected:
                        st.error(f"Expected {expected} card(s) here.")
                        st.stop()

                    # Dup check against everything known
                    all_opp_known = []
                    for o in H["opponents"]:
                        if o["cards"]:
                            parsed, _ = parse_cards(", ".join(o["cards"]))
                            all_opp_known.append(parsed)
                    hero_p, _ = parse_cards(", ".join(H["hero_cards"]))
                    board_p, _ = parse_cards(", ".join(H["board_cards"])) if H["board_cards"] else ([], None)
                    dup = validate_no_duplicates(hero_p, (board_p or []) + list(new_cards), all_opp_known)
                    if dup:
                        st.error(dup)
                        st.stop()

                    new_strs = [f"{r}{s}" for r,s in new_cards]
                    H["board_cards"].extend(new_strs)
                    new_street = get_street(len(H["board_cards"]))
                    H["action_log"].append(f"— {new_street.upper()}: {' '.join(new_strs)}")
                    H["result"] = run_simulation(H, iters)
                    st.rerun()

            # Opponent actions
            st.markdown('<div class="section-head">OPPONENT ACTIONS</div>', unsafe_allow_html=True)
            active_opps = [o for o in H["opponents"] if not o["folded"]]

            if active_opps:
                hdr = st.columns([2, 1, 1, 1])
                for col, lbl in zip(hdr, ["PLAYER", "FOLD", "CALL $", "RAISE $"]):
                    col.markdown(f"<span style='font-family:DM Mono,monospace;font-size:0.65rem;color:#7a9e87;'>{lbl}</span>", unsafe_allow_html=True)

                for real_idx, opp in enumerate(H["opponents"]):
                    if opp["folded"]:
                        continue
                    ca, cb, cc, cd_ = st.columns([2, 1, 1, 1])
                    with ca:
                        st.markdown(f"<span style='font-family:DM Mono,monospace;font-size:0.82rem;'>{opp['name']}</span>", unsafe_allow_html=True)
                    with cb:
                        if st.button("✗ Fold", key=f"fold_{real_idx}"):
                            H["opponents"][real_idx]["folded"] = True
                            H["action_log"].append(f"<span class='action-fold'>✗ {opp['name']} folds</span>")
                            H["result"] = run_simulation(H, iters)
                            st.rerun()
                    with cc:
                        call_amt = st.number_input("", min_value=0.0, step=0.5, key=f"call_amt_{real_idx}", label_visibility="collapsed")
                        if st.button("✓ Call", key=f"call_{real_idx}"):
                            if call_amt > 0:
                                H["pot"] += call_amt
                                H["action_log"].append(f"<span class='action-call'>↳ {opp['name']} calls ${call_amt:.0f}</span>")
                                st.rerun()
                    with cd_:
                        raise_amt = st.number_input("", min_value=0.0, step=0.5, key=f"raise_amt_{real_idx}", label_visibility="collapsed")
                        if st.button("↑ Raise", key=f"raise_{real_idx}"):
                            if raise_amt > 0:
                                H["pot"] += raise_amt
                                H["action_log"].append(f"<span class='action-raise'>↑ {opp['name']} raises ${raise_amt:.0f}</span>")
                                st.rerun()
            else:
                st.markdown('<div style="font-family:DM Mono,monospace;font-size:0.78rem;color:#4a7a5a;padding:0.5rem;">All opponents have folded.</div>', unsafe_allow_html=True)

            # My bet
            st.markdown('<div class="section-head">MY BET / CALL</div>', unsafe_allow_html=True)
            bc1, bc2 = st.columns([2, 1])
            with bc1:
                my_bet = st.number_input("Amount I put in ($)", min_value=0.0, step=0.5, key="my_bet_input")
            with bc2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Add to pot", key="btn_my_bet"):
                    if my_bet > 0:
                        H["pot"] += my_bet
                        H["action_log"].append(f"<span class='action-call'>↳ You put in ${my_bet:.0f}</span>")
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄  NEW HAND", use_container_width=True, key="btn_new_hand"):
                init_hand()
                st.rerun()

    # ── RIGHT PANEL ───────────────────────────────────────────────────────────
    with right:
        if not hand_started:
            st.markdown("""
            <div style="text-align:center;padding:5rem 2rem;color:#4a7a5a;">
              <div style="font-size:3.5rem;margin-bottom:1rem;">🃏</div>
              <div style="font-family:'DM Mono',monospace;font-size:0.75rem;letter-spacing:2px;">
                SET UP YOUR HAND ON THE LEFT AND HIT START
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            # Pot
            st.markdown(f"""
            <div class="pot-display">
              <div class="pot-label">POT</div>
              <div class="pot-value">${H['pot']:.2f}</div>
            </div>""", unsafe_allow_html=True)

            # Your hand
            st.markdown('<div class="section-head">YOUR HAND</div>', unsafe_allow_html=True)
            st.markdown(chips_html(H["hero_cards"]), unsafe_allow_html=True)

            # Board
            st.markdown('<div class="section-head">BOARD</div>', unsafe_allow_html=True)
            board_display = H["board_cards"] + ["??" for _ in range(5 - len(H["board_cards"]))]
            st.markdown(chips_html(board_display), unsafe_allow_html=True)

            # Players
            st.markdown('<div class="section-head">PLAYERS</div>', unsafe_allow_html=True)
            for opp in H["opponents"]:
                folded_cls = "folded" if opp["folded"] else ""
                cards_html = chips_html(opp["cards"]) if opp["cards"] else "<span style='color:#4a7a5a;font-family:DM Mono,monospace;font-size:0.75rem;'>unknown</span>"
                fold_tag   = " <span style='color:#c0392b;font-size:0.7rem;'>[FOLDED]</span>" if opp["folded"] else ""
                st.markdown(f"""
                <div class="player-row {folded_cls}">
                  <span class="player-name">{opp['name']}{fold_tag}</span>
                  {cards_html}
                </div>""", unsafe_allow_html=True)

            # Odds
            if H["result"]:
                r = H["result"]
                active_count = sum(1 for o in H["opponents"] if not o["folded"])
                st.markdown('<div class="section-head">ODDS</div>', unsafe_allow_html=True)
                st.markdown(f"""
                <div class="odds-row">
                  <div class="odds-box"><div class="odds-label">WIN</div><div class="odds-value odds-win">{r['win']}%</div></div>
                  <div class="odds-box"><div class="odds-label">TIE</div><div class="odds-value odds-tie">{r['tie']}%</div></div>
                  <div class="odds-box"><div class="odds-label">LOSE</div><div class="odds-value odds-lose">{r['lose']}%</div></div>
                </div>
                <div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#4a7a5a;text-align:right;">
                  vs {active_count} active opponent(s) · {r['iterations']:,} sims
                </div>""", unsafe_allow_html=True)

                # Hand distribution
                st.markdown('<div class="section-head">YOUR HAND AT RIVER</div>', unsafe_allow_html=True)
                bars = ""
                for cat in HAND_CATEGORIES:
                    pct = r["hand_distribution"][cat]
                    bars += f"""
                    <div class="dist-bar-wrap">
                      <div class="dist-label">{cat}</div>
                      <div class="dist-bar-bg"><div class="dist-bar-fill" style="width:{min(pct,100)}%"></div></div>
                      <div class="dist-pct">{pct}%</div>
                    </div>"""
                st.markdown(bars, unsafe_allow_html=True)

            elif sum(1 for o in H["opponents"] if not o["folded"]) == 0:
                st.markdown("""
                <div style="text-align:center;padding:2rem;color:#2ecc71;font-family:'Bebas Neue',cursive;font-size:2rem;letter-spacing:3px;">
                  🏆 ALL OPPONENTS FOLDED
                </div>""", unsafe_allow_html=True)

            # Action log
            if H["action_log"]:
                st.markdown('<div class="section-head">ACTION LOG</div>', unsafe_allow_html=True)
                log_html = "<br>".join(H["action_log"])
                st.markdown(f'<div class="action-log">{log_html}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# TAB 2 — LOG SHOWDOWN
# ════════════════════════════════════════════════════════════════
with tab_log:
    st.markdown('<div style="color:#7a9e87;font-family:DM Mono,monospace;font-size:0.72rem;letter-spacing:1px;margin-bottom:1.2rem;">LOG REVEALED CARDS AFTER SHOWDOWN · BUILDS YOUR PLAYER DATABASE</div>', unsafe_allow_html=True)

    prefill_board   = ", ".join(H.get("board_cards", []))
    prefill_session = H.get("session_label", "")
    prefill_pot     = float(H.get("pot", 0.0))

    with st.form("log_hand_form", clear_on_submit=True):
        st.markdown('<div class="section-head">SESSION</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            session_label = st.text_input("Session name", value=prefill_session, placeholder="Friday Night")
        with col_s2:
            pot_size = st.number_input("Pot size ($)", min_value=0.0, step=0.5, value=prefill_pot)

        st.markdown('<div class="section-head">BOARD</div>', unsafe_allow_html=True)
        log_board = st.text_input("Final board (5 cards)", value=prefill_board, placeholder="Kh, 7d, 2c, 4s, Jh")

        st.markdown('<div class="section-head">REVEALED HANDS</div>', unsafe_allow_html=True)
        st.caption("Enter each player shown at showdown. Leave blank rows to skip.")

        player_entries = []
        for i in range(8):
            prefill_name = H["opponents"][i]["name"] if i < len(H.get("opponents", [])) else ""
            c1, c2 = st.columns([1, 2])
            with c1:
                pname = st.text_input(f"Player {i+1} name", value=prefill_name, placeholder="Name", key=f"log_name_{i}")
            with c2:
                pcards = st.text_input(f"Player {i+1} cards", placeholder="Ah, Kd", key=f"log_cards_{i}")
            if pname.strip() or pcards.strip():
                player_entries.append((pname.strip(), pcards.strip()))

        notes = st.text_area("Notes", placeholder="e.g. Dave slow-played aces pre-flop", height=70)
        submitted = st.form_submit_button("💾  SAVE TO PLAYER HISTORY", use_container_width=True)

    if submitted:
        board_cards_log, berr = parse_cards(log_board)
        if berr:
            st.error(f"Board: {berr}")
            st.stop()
        board_str_list = [f"{r}{s}" for r, s in board_cards_log]
        errors, saved = [], []
        for pname, pcards_str in player_entries:
            if not pname and not pcards_str:
                continue
            if not pname:
                errors.append("A player entry is missing a name.")
                continue
            if not pcards_str:
                errors.append(f"'{pname}' has no cards entered.")
                continue
            p_cards, perr = parse_cards(pcards_str)
            if perr:
                errors.append(f"{pname}: {perr}")
                continue
            if len(p_cards) != 2:
                errors.append(f"{pname}: need exactly 2 cards.")
                continue
            log_hand(
                player_name=pname,
                hole_cards=[f"{r}{s}" for r,s in p_cards],
                board_cards=board_str_list,
                pot_size=pot_size if pot_size > 0 else None,
                notes=notes,
                session_label=session_label or None,
            )
            saved.append(pname)
        for e in errors:
            st.error(e)
        if saved:
            st.success(f"✅ Saved: {', '.join(saved)}")


# ════════════════════════════════════════════════════════════════
# TAB 3 — PLAYER HISTORY
# ════════════════════════════════════════════════════════════════
with tab_players:
    players = get_all_players()

    if not players:
        st.markdown('<div style="text-align:center;padding:4rem;color:#4a7a5a;font-family:DM Mono,monospace;font-size:0.78rem;letter-spacing:2px;">NO PLAYERS LOGGED YET<br><br>USE "LOG SHOWDOWN" AFTER EACH HAND</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="color:#7a9e87;font-family:DM Mono,monospace;font-size:0.72rem;letter-spacing:1px;margin-bottom:1rem;">{len(players)} PLAYER(S) IN DATABASE</div>', unsafe_allow_html=True)
        selected_player = st.selectbox("Select player", players)

        if selected_player:
            history = get_player_history(selected_player)
            stats   = get_player_stats(selected_player)

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Hands Logged", stats["total_hands"])
            col_b.metric("Avg Pot", f"${stats['avg_pot']}" if stats['avg_pot'] else "—")
            col_c.metric("Sessions", len(stats['sessions']))

            st.markdown('<div class="section-head">HAND HISTORY</div>', unsafe_allow_html=True)

            sessions_seen, session_hands = [], {}
            for i, hand in enumerate(reversed(history)):
                sess = hand.get("session", "Unknown")
                if sess not in session_hands:
                    session_hands[sess] = []
                    sessions_seen.append(sess)
                session_hands[sess].append(hand)

            def cchip(cs):
                if len(cs) >= 2:
                    rank, suit = cs[0].upper(), cs[1].lower()
                    color = "red" if suit in ('h','d') else ""
                    return f'<span class="card-chip {color}">{RANK_DISPLAY.get(rank,rank)}{SUIT_DISPLAY.get(suit,suit)}</span>'
                return cs

            for sess in sessions_seen:
                st.markdown(f'<div style="font-family:DM Mono,monospace;font-size:0.62rem;letter-spacing:2px;color:#c9a84c;margin:0.8rem 0 0.3rem;">📅 {sess.upper()}</div>', unsafe_allow_html=True)
                for hand in session_hands[sess]:
                    hole      = hand.get("hole_cards", [])
                    board     = hand.get("board_cards", [])
                    pot       = hand.get("pot_size")
                    notes_txt = hand.get("notes", "")
                    ts        = hand.get("timestamp", "")[:16].replace("T", " ")
                    hole_html  = " ".join(cchip(c) for c in hole)
                    board_html = " ".join(cchip(c) for c in board)
                    pot_str    = f" · 💰 ${pot}" if pot else ""
                    notes_str  = f"<br><span style='color:#7a9e87;'>📝 {notes_txt}</span>" if notes_txt else ""
                    st.markdown(f"""
                    <div class="hand-record">
                      <span style='color:#7a9e87;'>{ts}</span>{pot_str}<br>
                      <span style='color:#c9a84c;'>HOLE:</span> {hole_html} &nbsp;
                      <span style='color:#c9a84c;'>BOARD:</span> {board_html or '<span style="color:#4a7a5a">—</span>'}
                      {notes_str}
                    </div>""", unsafe_allow_html=True)

            st.markdown('<div class="section-head">MANAGE</div>', unsafe_allow_html=True)
            if st.button(f"🗑️ Delete ALL hands for {selected_player}"):
                delete_player(selected_player)
                st.success(f"Deleted {selected_player}.")
                st.rerun()

    st.markdown('<div class="section-head">SAVE & RESTORE YOUR DATA</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#7a9e87;font-family:DM Mono,monospace;font-size:0.68rem;letter-spacing:1px;margin-bottom:0.8rem;line-height:1.8;">⚠️ EXPORT AFTER EACH SESSION · IMPORT NEXT TIME TO RESTORE</div>', unsafe_allow_html=True)
    col_exp, col_imp = st.columns(2)
    with col_exp:
        st.markdown("**📥 Export**")
        st.download_button("⬇️  Download history.json", data=export_json(), file_name="poker_history.json", mime="application/json", use_container_width=True)
    with col_imp:
        st.markdown("**📤 Import**")
        uploaded = st.file_uploader("Upload", type=["json"], label_visibility="collapsed", key="import_uploader")
        if uploaded:
            ok, err = import_json(uploaded.read().decode("utf-8"))
            if ok:
                st.success("✅ Imported!")
                st.rerun()
            else:
                st.error(f"Failed: {err}")
