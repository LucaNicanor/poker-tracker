"""
Opponent Intelligence & Player Profiler
---------------------------------------
Extracts opponent screen names, stack sizes, positions, and tendencies
from ClubWPT captures and poker sessions. Builds persistent opponent profiles
and generates exploitative strategy cheat sheets for GPT-6-Astra.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "hands", "processed")
OPPONENTS_FILE = os.path.join(PROCESSED_DIR, "opponents.json")

# Known opponent observations from ClubWPT session captures
KNOWN_CLUBWPT_PLAYERS = {
    "SneakyLittle..": {
        "platform": "ClubWPT Gold",
        "game_type": "Cash HL3990 ($0.01/$0.02)",
        "typical_stack_bb": 339,
        "style": "Loose-Aggressive (LAG)",
        "observed_actions": [
            "Open-raises 3x from Button with wide steal range",
            "Open-raises 3x from Hijack",
            "Limp-completes Small Blind for 0.50 BB",
        ],
        "exploit_strategy": "Tighten up against their opens out of position. 3-bet them with high-equity linear hands when they open late position. Do not call with weak offsuit holdings.",
    },
    "Sparky Local6": {
        "platform": "ClubWPT Gold",
        "game_type": "Cash HL3990 ($0.01/$0.02)",
        "typical_stack_bb": 222,
        "style": "Aggressive / Sizing Heavy",
        "observed_actions": ["Open-raised 4x (4 BB) from Cutoff"],
        "exploit_strategy": "When they use non-standard large sizing (4x+), tighten defending ranges significantly. Fold dominated offsuit broadways.",
    },
    "58322783": {
        "platform": "ClubWPT Gold",
        "game_type": "Cash HL3990 ($0.01/$0.02)",
        "typical_stack_bb": 196,
        "style": "Tight-Aggressive (TAG)",
        "observed_actions": ["Standard 3x open-raise from UTG", "Defends blinds"],
        "exploit_strategy": "Respect their early-position opens; they hold strong ranges (JJ+, AQs+, AK). Defend in the Big Blind with pocket pairs (e.g. 88) for set-mining deep stacked.",
    },
    "PeoplePleaser": {
        "platform": "ClubWPT Gold",
        "game_type": "Cash HL3990 ($0.01/$0.02)",
        "typical_stack_bb": 180,
        "style": "Passive / Limp-Friendly",
        "observed_actions": [
            "Limping/checking in unraised pots",
            "Taking long decisions on standard actions",
        ],
        "exploit_strategy": "Isolate their limps with aggressive raises when you hold position. Value-bet relentlessly on turns and rivers.",
    },
    "TastelessCalc": {
        "platform": "ClubWPT Gold",
        "game_type": "MTT 100 Chip Freeroll",
        "typical_stack_bb": 22,
        "style": "Limp Punisher / Aggressive",
        "observed_actions": [
            "Made a 5x (5 BB) isolation raise against a 1 BB open-limp"
        ],
        "exploit_strategy": "Never open-limp against them. If you hold premium monsters (AA, KK, QQ), limp-trap to induce their aggressive shove, but fold weak pocket pairs to their 5x raise.",
    },
    "Bartogoon": {
        "platform": "ClubWPT Gold",
        "game_type": "Cash HL3990 ($0.01/$0.02)",
        "typical_stack_bb": 116,
        "style": "Standard / Tight",
        "observed_actions": ["Folds early position to opens"],
        "exploit_strategy": "Steal their blinds with high frequency when they are in SB/BB.",
    },
    "BoulderRider..": {
        "platform": "ClubWPT Gold",
        "game_type": "Cash HL3990 ($0.01/$0.02)",
        "typical_stack_bb": 200,
        "style": "Deep Stack Unknown",
        "observed_actions": ["Deep stack 200 BB sitting table"],
        "exploit_strategy": "Exercise caution in 3-bet pots; position is paramount at 200 BB depth.",
    },
}


def load_or_update_opponents():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    opponents = {}
    if os.path.exists(OPPONENTS_FILE):
        try:
            with open(OPPONENTS_FILE, "r", encoding="utf-8") as f:
                opponents = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[!] Warning reading opponents cache: {exc}")

    # Merge known players
    for name, data in KNOWN_CLUBWPT_PLAYERS.items():
        if name not in opponents:
            opponents[name] = data
        else:
            opponents[name].update(data)

    with open(OPPONENTS_FILE, "w") as f:
        json.dump(opponents, f, indent=2)

    return opponents


if __name__ == "__main__":
    ops = load_or_update_opponents()
    print(
        f"[*] Opponents Database Updated: {len(ops)} players cataloged in {OPPONENTS_FILE}"
    )
    for name, p in ops.items():
        print(f" • {name} ({p['style']}) - Stack: ~{p['typical_stack_bb']} BB")
