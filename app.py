"""
app.py - Texas Hold'em Poker Odds Analyzer with Player History
Run with: streamlit run app.py
"""

import streamlit as st
import time
from cards import parse_cards, validate_no_duplicates, card_display, SUIT_COLOR, RANK_DISPLAY, SUIT_DISPLAY
from simulator import simulate, HAND_CATEGORIES
from player_db import (
    get_all_players, get_player_history, log_hand,
    delete_player, delete_hand, get_player_stats
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Poker Odds Analyzer",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

  :root {
    --green:  #1a7a4a;
    --green2: #22a060;
    --felt:   #0d3d27;
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

  /* Header */
  .poker-header {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    font-family: 'Bebas Neue', cursive;
    font-size: 3rem;
    letter-spacing: 4px;
    color: var(--gold);
    text-shadow: 0 0 30px rgba(201,168,76,0.4);
  }
  .poker-sub {
    text-align: center;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 2px;
    margin-bottom: 2rem;
  }

  /* Tabs */
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

  /* Cards display */
  .card-chip {
    display: inline-block;
    background: var(--card);
    border-radius: 6px;
    padding: 4px 10px;
    margin: 3px;
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a1a;
    box-shadow: 0 2px 8px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.8);
  }
  .card-chip.red { color: #c0392b; }
  .card-chip.green { color: #1a7a4a; }

  /* Odds display */
  .odds-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    margin: 0.3rem;
  }
  .odds-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 2px;
    color: var(--muted);
    margin-bottom: 0.4rem;
  }
  .odds-value {
    font-family: 'Bebas Neue', cursive;
    font-size: 3rem;
    line-height: 1;
  }
  .odds-win  { color: #2ecc71; }
  .odds-tie  { color: var(--gold); }
  .odds-lose { color: var(--red); }

  /* Section headers */
  .section-head {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 3px;
    color: var(--gold);
    text-transform: uppercase;
    border-bottom: 1px solid rgba(201,168,76,0.2);
    padding-bottom: 0.4rem;
    margin: 1.2rem 0 0.8rem;
  }

  /* Input labels */
  label, .stTextInput label, .stSelectbox label, .stNumberInput label, .stSlider label {
    color: var(--muted) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 1px !important;
  }

  /* Inputs */
  input[type="text"], input[type="number"], .stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    border-radius: 6px !important;
  }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, var(--green), var(--green2)) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    letter-spacing: 1px !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
  }
  .stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(34,160,96,0.4) !important;
  }

  /* Warning / info */
  .stAlert {
    background: rgba(201,168,76,0.1) !important;
    border: 1px solid rgba(201,168,76,0.3) !important;
    border-radius: 8px !important;
  }

  /* Player history card */
  .player-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
  }
  .player-name-big {
    font-family: 'Bebas Neue', cursive;
    font-size: 1.6rem;
    color: var(--gold);
    letter-spacing: 2px;
  }
  .hand-record {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid var(--green);
    border-radius: 0 6px 6px 0;
    padding: 0.6rem 1rem;
    margin: 0.4rem 0;
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
  }

  /* Bar chart for hand distribution */
  .dist-bar-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 4px 0;
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
  }
  .dist-label { width: 110px; color: var(--muted); text-align: right; flex-shrink: 0; }
  .dist-bar-bg { flex: 1; background: rgba(255,255,255,0.05); border-radius: 3px; height: 16px; }
  .dist-bar-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, var(--green), var(--green2)); }
  .dist-pct { width: 45px; color: var(--text); }

  /* Felt texture on main area */
  [data-testid="stMain"] {
    background: radial-gradient(ellipse at 50% 0%, #1a4a30 0%, var(--dark) 70%);
  }

  /* Selectbox */
  [data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: var(--text) !important;
  }

  /* Suppress footer */
  footer { display: none; }
  #MainMenu { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="poker-header">🃏 Poker Odds Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="poker-sub">TEXAS HOLD\'EM · MONTE CARLO SIMULATION · PLAYER TRACKER</div>', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_odds, tab_log, tab_players = st.tabs([
    "  ODDS CALCULATOR  ",
    "  LOG A HAND  ",
    "  PLAYER HISTORY  "
])


# ════════════════════════════════════════════════════════════════
# TAB 1 — ODDS CALCULATOR
# ════════════════════════════════════════════════════════════════
def render_card_chips(cards):
    """Render cards as styled HTML chips."""
    html = ""
    for card in cards:
        rank, suit = card
        color_cls = "red" if suit in ('h', 'd') else ""
        html += f'<span class="card-chip {color_cls}">{RANK_DISPLAY[rank]}{SUIT_DISPLAY[suit]}</span>'
    return html

with tab_odds:
    col_inputs, col_results = st.columns([1, 1], gap="large")

    with col_inputs:
        st.markdown('<div class="section-head">YOUR HAND</div>', unsafe_allow_html=True)
        hero_input = st.text_input(
            "Hole cards",
            placeholder="As, Ad",
            help="Your two hole cards. Example: As, Kd",
            key="hero_input"
        )

        st.markdown('<div class="section-head">BOARD</div>', unsafe_allow_html=True)
        board_input = st.text_input(
            "Community cards (0–5)",
            placeholder="Kh, 7d, 2c",
            help="Leave blank for pre-flop. Add cards as they're revealed.",
            key="board_input"
        )

        st.markdown('<div class="section-head">OPPONENTS</div>', unsafe_allow_html=True)

        num_opponents = st.number_input("Number of opponents", min_value=1, max_value=8, value=2, step=1)

        # Known opponent cards
        opp_known_inputs = []
        if num_opponents > 0:
            with st.expander("Enter known opponent hole cards (optional)", expanded=False):
                st.caption("Leave blank for unknown opponents — they'll be simulated randomly.")
                for i in range(int(num_opponents)):
                    opp_known_inputs.append(
                        st.text_input(
                            f"Opponent {i+1} hole cards",
                            placeholder="e.g. Qh, Jh",
                            key=f"opp_{i}"
                        )
                    )

        st.markdown('<div class="section-head">SIMULATION</div>', unsafe_allow_html=True)
        iterations = st.select_slider(
            "Iterations",
            options=[5000, 10000, 20000, 50000, 100000, 200000],
            value=50000,
            help="More iterations = more accurate but slower."
        )
        if iterations < 20000:
            st.warning("⚠️ Low iteration count — results may be inaccurate.")

        run_btn = st.button("▶  CALCULATE ODDS", use_container_width=True)

    with col_results:
        st.markdown('<div class="section-head">RESULTS</div>', unsafe_allow_html=True)

        if run_btn:
            # Parse hero
            hero_cards, hero_err = parse_cards(hero_input)
            if hero_err:
                st.error(f"Hero cards: {hero_err}")
                st.stop()
            if len(hero_cards) != 2:
                st.error("Please enter exactly 2 hole cards.")
                st.stop()

            # Parse board
            board_cards, board_err = parse_cards(board_input)
            if board_err:
                st.error(f"Board: {board_err}")
                st.stop()
            if len(board_cards) not in [0, 3, 4, 5]:
                st.error("Board must have 0, 3, 4, or 5 cards.")
                st.stop()

            # Parse opponent known cards
            opp_known_list = []
            for inp in opp_known_inputs:
                if inp and inp.strip():
                    cards, err = parse_cards(inp)
                    if err:
                        st.error(f"Opponent cards: {err}")
                        st.stop()
                    if len(cards) != 2:
                        st.error("Each opponent needs exactly 2 cards (or leave blank).")
                        st.stop()
                    opp_known_list.append(cards)
                else:
                    opp_known_list.append([])

            # Validate no duplicates
            all_known = [c for opp in opp_known_list for c in opp]
            dup_err = validate_no_duplicates(hero_cards, board_cards, opp_known_list)
            if dup_err:
                st.error(dup_err)
                st.stop()

            # Preview cards
            st.markdown("**Your hand:** " + render_card_chips(hero_cards), unsafe_allow_html=True)
            if board_cards:
                st.markdown("**Board:** " + render_card_chips(board_cards), unsafe_allow_html=True)

            # Run simulation
            with st.spinner(f"Running {iterations:,} simulations..."):
                t0 = time.time()
                result = simulate(hero_cards, board_cards, int(num_opponents), iterations, opp_known_list)
                elapsed = time.time() - t0

            # Odds display
            st.markdown(f"""
            <div style="display:flex; gap:0.5rem; margin: 1rem 0;">
              <div class="odds-box" style="flex:1">
                <div class="odds-label">WIN</div>
                <div class="odds-value odds-win">{result['win']}%</div>
              </div>
              <div class="odds-box" style="flex:1">
                <div class="odds-label">TIE</div>
                <div class="odds-value odds-tie">{result['tie']}%</div>
              </div>
              <div class="odds-box" style="flex:1">
                <div class="odds-label">LOSE</div>
                <div class="odds-value odds-lose">{result['lose']}%</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.caption(f"Computed in {elapsed:.1f}s · {iterations:,} iterations · {num_opponents} opponent(s)")

            # Hand distribution
            st.markdown('<div class="section-head">HAND DISTRIBUTION AT RIVER</div>', unsafe_allow_html=True)
            dist = result['hand_distribution']
            bars_html = ""
            for cat in HAND_CATEGORIES:
                pct = dist[cat]
                bars_html += f"""
                <div class="dist-bar-wrap">
                  <div class="dist-label">{cat}</div>
                  <div class="dist-bar-bg">
                    <div class="dist-bar-fill" style="width:{min(pct,100)}%"></div>
                  </div>
                  <div class="dist-pct">{pct}%</div>
                </div>"""
            st.markdown(bars_html, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div style="text-align:center; padding: 4rem 2rem; color: #4a7a5a;">
              <div style="font-size:4rem; margin-bottom:1rem;">🃏</div>
              <div style="font-family:'DM Mono',monospace; font-size:0.8rem; letter-spacing:2px;">
                ENTER YOUR CARDS AND CLICK CALCULATE
              </div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# TAB 2 — LOG A HAND
# ════════════════════════════════════════════════════════════════
with tab_log:
    st.markdown("""
    <div style="color:#7a9e87; font-family:'DM Mono',monospace; font-size:0.75rem; 
                letter-spacing:1px; margin-bottom:1.5rem;">
    LOG REVEALED CARDS AT END OF HAND · BUILDS PLAYER DATABASE OVER TIME
    </div>
    """, unsafe_allow_html=True)

    with st.form("log_hand_form", clear_on_submit=True):
        st.markdown('<div class="section-head">SESSION</div>', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            session_label = st.text_input("Session name", placeholder="e.g. Friday Night, 2024-01-05")
        with col_s2:
            pot_size = st.number_input("Pot size ($)", min_value=0.0, step=0.5, value=0.0)

        st.markdown('<div class="section-head">BOARD CARDS</div>', unsafe_allow_html=True)
        log_board = st.text_input("Final board (5 cards)", placeholder="Kh, 7d, 2c, 4s, Jh")

        st.markdown('<div class="section-head">PLAYER HANDS</div>', unsafe_allow_html=True)
        st.caption("Add as many players as were revealed at showdown. Leave blank rows to skip.")

        # Allow up to 8 players
        player_entries = []
        for i in range(8):
            c1, c2 = st.columns([1, 2])
            with c1:
                pname = st.text_input(f"Player {i+1} name", placeholder="e.g. Dave", key=f"log_name_{i}")
            with c2:
                pcards = st.text_input(f"Player {i+1} cards", placeholder="e.g. Ah, Kd", key=f"log_cards_{i}")
            if pname.strip() or pcards.strip():
                player_entries.append((pname.strip(), pcards.strip()))

        notes = st.text_area("Notes (optional)", placeholder="e.g. Dave slow-played aces preflop", height=80)

        submitted = st.form_submit_button("💾  SAVE HAND TO HISTORY", use_container_width=True)

    if submitted:
        # Validate board
        board_cards_log, berr = parse_cards(log_board)
        if berr:
            st.error(f"Board: {berr}")
            st.stop()

        board_str_list = [f"{r}{s}" for r, s in board_cards_log]
        errors = []
        saved = []

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

            cards_str_list = [f"{r}{s}" for r, s in p_cards]
            log_hand(
                player_name=pname,
                hole_cards=cards_str_list,
                board_cards=board_str_list,
                pot_size=pot_size if pot_size > 0 else None,
                notes=notes,
                session_label=session_label if session_label else None,
            )
            saved.append(pname)

        if errors:
            for e in errors:
                st.error(e)
        if saved:
            st.success(f"✅ Saved hand for: {', '.join(saved)}")


# ════════════════════════════════════════════════════════════════
# TAB 3 — PLAYER HISTORY
# ════════════════════════════════════════════════════════════════
with tab_players:
    players = get_all_players()

    if not players:
        st.markdown("""
        <div style="text-align:center; padding:4rem; color:#4a7a5a; font-family:'DM Mono',monospace; font-size:0.8rem; letter-spacing:2px;">
          NO PLAYERS LOGGED YET<br><br>
          USE THE "LOG A HAND" TAB AFTER EACH HAND TO BUILD YOUR DATABASE
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="color:#7a9e87; font-family:'DM Mono',monospace; font-size:0.75rem; letter-spacing:1px; margin-bottom:1.5rem;">
        {len(players)} PLAYER(S) IN DATABASE
        </div>
        """, unsafe_allow_html=True)

        selected_player = st.selectbox("Select player to view", players)

        if selected_player:
            history = get_player_history(selected_player)
            stats = get_player_stats(selected_player)

            # Stats bar
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Hands Logged", stats["total_hands"])
            with col_b:
                st.metric("Avg Pot", f"${stats['avg_pot']}" if stats['avg_pot'] else "—")
            with col_c:
                st.metric("Sessions", len(stats['sessions']))

            st.markdown('<div class="section-head">HAND HISTORY</div>', unsafe_allow_html=True)

            # Group by session
            sessions_seen = []
            session_hands = {}
            for i, hand in enumerate(reversed(history)):
                orig_idx = len(history) - 1 - i
                sess = hand.get("session", "Unknown")
                if sess not in session_hands:
                    session_hands[sess] = []
                    sessions_seen.append(sess)
                session_hands[sess].append((orig_idx, hand))

            for sess in sessions_seen:
                st.markdown(f"""
                <div style="font-family:'DM Mono',monospace; font-size:0.65rem; 
                            letter-spacing:2px; color:#c9a84c; margin: 1rem 0 0.4rem;">
                  📅 {sess.upper()}
                </div>
                """, unsafe_allow_html=True)

                for orig_idx, hand in session_hands[sess]:
                    hole = hand.get("hole_cards", [])
                    board = hand.get("board_cards", [])
                    pot = hand.get("pot_size")
                    notes_txt = hand.get("notes", "")
                    ts = hand.get("timestamp", "")[:16].replace("T", " ")

                    # Render cards as chips
                    def card_chip_html(card_str):
                        if len(card_str) == 2:
                            rank, suit = card_str[0].upper(), card_str[1].lower()
                            color = "red" if suit in ('h','d') else ""
                            r_disp = RANK_DISPLAY.get(rank, rank)
                            s_disp = SUIT_DISPLAY.get(suit, suit)
                            return f'<span class="card-chip {color}">{r_disp}{s_disp}</span>'
                        return card_str

                    hole_html = " ".join(card_chip_html(c) for c in hole)
                    board_html = " ".join(card_chip_html(c) for c in board)

                    pot_str = f" · 💰 ${pot}" if pot else ""
                    notes_str = f"<br><span style='color:#7a9e87;'>📝 {notes_txt}</span>" if notes_txt else ""

                    st.markdown(f"""
                    <div class="hand-record">
                      <span style='color:#7a9e87;'>{ts}</span>{pot_str}<br>
                      <span style='color:#c9a84c;'>HOLE:</span> {hole_html} &nbsp;&nbsp;
                      <span style='color:#c9a84c;'>BOARD:</span> {board_html if board_html else '<span style="color:#4a7a5a">not recorded</span>'}
                      {notes_str}
                    </div>
                    """, unsafe_allow_html=True)

            # Delete options
            st.markdown('<div class="section-head">MANAGE</div>', unsafe_allow_html=True)
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                if st.button(f"🗑️ Delete ALL hands for {selected_player}", key="del_player"):
                    delete_player(selected_player)
                    st.success(f"Deleted all data for {selected_player}.")
                    st.rerun()
