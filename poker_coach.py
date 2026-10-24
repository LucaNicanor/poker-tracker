"""
Poker Coach & Instant Feedback Engine
-------------------------------------
Analyzes captured hands, identifies hole cards and position,
and provides instant GTO strategic feedback in the console.
"""

# Preflop GTO Range Tiers (for 6-max & 9-max Cash/MTT 40-100bb)
PREFLOP_GTO_RANGES = {
    "PREMIUM_OPEN_ALL": [
        "AA",
        "KK",
        "QQ",
        "JJ",
        "TT",
        "99",
        "88",
        "77",
        "AKs",
        "AQs",
        "AJs",
        "ATs",
        "A5s",
        "A4s",
        "AKo",
        "AQo",
        "AJo",
        "KQs",
        "KJs",
        "KTs",
        "QJs",
        "QTs",
        "JTs",
        "T9s",
        "98s",
        "87s",
        "76s",
    ],
    "LATE_POS_EXPANSION": [
        "66",
        "55",
        "44",
        "33",
        "22",
        "A9s",
        "A8s",
        "A7s",
        "A6s",
        "A3s",
        "A2s",
        "ATo",
        "KTo",
        "QTo",
        "JTo",
        "K9s",
        "Q9s",
        "J9s",
        "T8s",
        "97s",
        "86s",
        "75s",
        "65s",
        "54s",
    ],
    "PURE_FOLDS": [
        "T3o",
        "T2o",
        "93o",
        "92o",
        "83o",
        "82o",
        "73o",
        "72o",
        "62o",
        "52o",
        "42o",
        "32o",
        "J3o",
        "J2o",
        "Q3o",
        "Q2o",
        "K3o",
        "K2o",
    ],
}


def evaluate_preflop_hand(hero_cards_str, position="MP", stack_bb=80):
    """
    Evaluates a preflop hand against GTO baselines and returns coaching advice.
    """
    cards = hero_cards_str.upper().replace(" ", "").replace("10", "T")

    # Identify canonical format e.g. "T3o", "AKs", "QQ"
    is_pair = len(cards) >= 2 and cards[0] == cards[1]
    is_suited = "S" in cards or (len(cards) == 4 and cards[1] == cards[3])

    if is_pair:
        hand_key = cards[:2]
    else:
        rank1 = cards[0] if len(cards) > 0 else "?"
        rank2 = cards[1] if len(cards) > 1 else "?"
        suffix = "s" if is_suited else "o"
        hand_key = f"{rank1}{rank2}{suffix}"

    feedback = {
        "hand": hand_key,
        "recommendation": "FOLD",
        "gto_action": "Pure Fold (100%)",
        "ev_impact": "Neutral / Avoids negative EV",
        "tip": "Default fold. Do not limp or call raises.",
        "grade": "Good",
    }

    if any(
        hand_key == h or hand_key.startswith(h)
        for h in PREFLOP_GTO_RANGES["PREMIUM_OPEN_ALL"]
    ):
        feedback["recommendation"] = "RAISE / OPEN"
        feedback["gto_action"] = "Pure Open-Raise (2.0x - 2.5x)"
        feedback["ev_impact"] = "+EV High Equity"
        feedback["tip"] = (
            "Raise first in. Never open-limp. If facing a 3-bet, evaluate continuation based on position."
        )
        feedback["grade"] = "Premium"
    elif any(
        hand_key == h or hand_key.startswith(h)
        for h in PREFLOP_GTO_RANGES["LATE_POS_EXPANSION"]
    ):
        if position in ["CO", "BTN", "SB"]:
            feedback["recommendation"] = "RAISE / STEAL"
            feedback["gto_action"] = "Open-Raise in Late Position"
            feedback["ev_impact"] = "+EV Exploitative Steal"
            feedback["tip"] = (
                "Profitable open from Cutoff, Button, or SB. Fold if facing heavy action ahead."
            )
            feedback["grade"] = "Situational"
        else:
            feedback["recommendation"] = "FOLD"
            feedback["gto_action"] = "Fold in Early/Middle Position"
            feedback["ev_impact"] = "-EV out of position"
            feedback["tip"] = (
                "Marginal hand. Fold from early/middle position to avoid getting dominated postflop."
            )
            feedback["grade"] = "Marginal Fold"
    else:
        feedback["recommendation"] = "FOLD"
        feedback["gto_action"] = "Pure Fold (100% GTO)"
        feedback["ev_impact"] = "-0.20 to -0.50 BB loss if played"
        feedback["tip"] = (
            "Unplayable trash. Open-folding immediately saves long-term EV."
        )
        feedback["grade"] = "Trash"

    return feedback


def print_feedback_card(hand_summary):
    """Prints a beautiful coaching card in the terminal."""
    h = hand_summary.get("hand", "Unknown")
    rec = hand_summary.get("recommendation", "FOLD")
    action = hand_summary.get("gto_action", "")
    tip = hand_summary.get("tip", "")
    ev = hand_summary.get("ev_impact", "")
    player_action = hand_summary.get("player_action", "Observed")

    color_border = "\033[92m" if "RAISE" in rec else "\033[94m"
    reset = "\033[0m"

    print("\n" + color_border + "=" * 62)
    print(f" 🎯 POKER COACH FEEDBACK | Hand: {h}")
    print("=" * 62)
    print(f" • GTO Action:       {rec} ({action})")
    print(f" • EV Assessment:   {ev}")
    if player_action:
        print(f" • Your Action:     {player_action}")
    print(f" • Strategy Tip:    {tip}")
    print("-" * 62)
    print(" (Review against your profile: close the limp gap & fold junk!)")
    print("=" * 62 + reset + "\n")


if __name__ == "__main__":
    # Test sample with the captured hand
    res = evaluate_preflop_hand("T3o", position="MP", stack_bb=79.2)
    res["player_action"] = "FOLD (+0.00 EV - GTO Approved)"
    print_feedback_card(res)
