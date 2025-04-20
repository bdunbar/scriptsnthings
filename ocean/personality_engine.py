#!/usr/bin/env python3
"""
personality_engine.py
─────────────────────
• Run it at every chapter break to keep your characters’ Big‑Five
  scores evolving.
• Answers live in personality_state.csv so the drift is cumulative.
--------------------------------------------------------------------
"""

import os
import random
import pandas as pd

# ─── CONFIGURABLE CONSTANTS ─────────────────────────────────────────
STATE_FILE = "personality_state.csv"      # where raw TIPI answers are kept
DRIFT_RANGE = (-2, 2)                     # per‑item nudge each chapter
LOW, HIGH = 30, 70                        # threshold flags for events
# -------------------------------------------------------------------

# Ten‑Item Personality Inventory (TIPI) metadata
ITEMS = [
    ("Extraverted, enthusiastic",          "E", False),
    ("Critical, quarrelsome",              "A", True),
    ("Dependable, self‑disciplined",       "C", False),
    ("Anxious, easily upset",              "N", False),
    ("Open to new experiences, complex",   "O", False),
    ("Reserved, quiet",                    "E", True),
    ("Sympathetic, warm",                  "A", False),
    ("Disorganized, careless",             "C", True),
    ("Calm, emotionally stable",           "N", True),
    ("Conventional, uncreative",           "O", True),
]

EVENTS = {
    "High-Extraversion":      "Bill corners an NPC for a long monologue.",
    "Low-Extraversion":       "Bill withdraws—scene shows him alone or terse.",
    "High-Openness":          "Bill proposes an off‑the‑wall solution.",
    "High-Neuroticism":       "Able has a visible panic response.",
    "Low-Conscientiousness":  "Able misplaces a critical dataslate.",
    # …fill in the rest as you think of them
}

FULL_TRAIT = dict(E="Extraversion", A="Agreeableness",
                  C="Conscientiousness", N="Neuroticism", O="Openness")
PAIRS = {t: [i for i, (_, code, _) in enumerate(ITEMS) if code == t]
         for t in FULL_TRAIT}              # two indices per trait
REV_ITEMS = {i for i, (_, _, rev) in enumerate(ITEMS) if rev}

# ─── LOW‑LEVEL LOAD / SAVE ──────────────────────────────────────────
def load_answers(name):
    """Return list[10] raw 1‑7 answers (or None if new character)."""
    try:
        df = pd.read_csv(STATE_FILE, index_col=0)
        return list(map(int, df.loc[name]))
    except (FileNotFoundError, KeyError):
        return None

def save_answers(name, answers):
    """Insert or update the row for *name* in the CSV."""
    try:
        df = pd.read_csv(STATE_FILE, index_col=0)
    except FileNotFoundError:
        df = pd.DataFrame(columns=range(10))
    df.loc[name] = answers
    df.to_csv(STATE_FILE)

# ─── SCORING UTILITIES ──────────────────────────────────────────────
def score_tipi(raw):
    """Convert 10 raw answers to {trait: 0‑100 score} dict."""
    coded = [(8 - a if i in REV_ITEMS else a) for i, a in enumerate(raw)]
    def trait(code):
        j, k = PAIRS[code]
        return (coded[j] + coded[k]) / 2 * 100 / 7          # rescale
    return {FULL_TRAIT[c]: round(trait(c), 1) for c in FULL_TRAIT}

def trait_flags(scores, low=LOW, high=HIGH):
    """Return ['High-Extraversion', 'Low-Agreeableness', ...]"""
    out = []
    for t, v in scores.items():
        if v >= high:
            out.append(f"High-{t}")
        elif v <= low:
            out.append(f"Low-{t}")
    return out

# ─── FRONT‑END ACTIONS ──────────────────────────────────────────────
def interview(name):
    """Ask the 10 TIPI questions once, save, and show scores."""
    print(f"\nInitial TIPI for {name}")
    raw = []
    for i, (text, _, _) in enumerate(ITEMS, 1):
        while True:
            try:
                a = int(input(f"Q{i}: I see myself as {text}  [1‑7] "))
                if 1 <= a <= 7:
                    raw.append(a)
                    break
            except ValueError:
                pass
    save_answers(name, raw)
    scores = score_tipi(raw)
    print("\nSaved. Baseline scores:")
    for trait, val in scores.items():
        print(f"  {trait:16} {val:5.1f}")
    return scores

def drift(name, drift_range=DRIFT_RANGE):
    """Nudge existing answers, rescore, flag threshold events."""
    raw = load_answers(name)
    if raw is None:                        # never interviewed
        return interview(name)             # recurse into first‑time path

    # 1) drift each of the 10 answers
    new = [max(1, min(7, a + random.randint(*drift_range))) for a in raw]
    save_answers(name, new)

    # 2) rescore and check thresholds
    scores = score_tipi(new)
    flags  = trait_flags(scores)

    # 3) print the basic table
    print(f"\n{name} after drift ({drift_range[0]}…{drift_range[1]} per item):")
    for trait, val in scores.items():
        print(f"  {trait:16} {val:5.1f}")

    # 4) if any thresholds crossed, show them and their story prompts
    if flags:
        print("  ⚑ triggers:", ", ".join(flags))
        for f in flags:
            if f in EVENTS:
                print("    →", EVENTS[f])

    return scores

# ─── CLI LOOP ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Big‑Five Drift Engine — type 'help' for commands.")
    while True:
        cmd = input("\n> ").strip().lower()
        if cmd in {"quit", "exit"}:
            break
        elif cmd == "help":
            print("  new NAME      – first‑time TIPI interview")
            print("  next NAME     – apply drift for chapter break")
            print("  list          – show stored characters")
            print("  reset NAME    – delete saved answers")
            print("  quit          – exit program")
        elif cmd.startswith("new "):
            name = cmd[4:].strip()
            interview(name)
        elif cmd.startswith("next "):
            name = cmd[5:].strip()
            drift(name)
        elif cmd == "list":
            if os.path.exists(STATE_FILE):
                df = pd.read_csv(STATE_FILE, index_col=0)
                print("Characters:", ", ".join(df.index))
            else:
                print("No characters yet.")
        elif cmd.startswith("reset "):
            name = cmd[6:].strip()
            try:
                df = pd.read_csv(STATE_FILE, index_col=0)
                df = df.drop(name)
                df.to_csv(STATE_FILE)
                print(f"{name} wiped.")
            except (FileNotFoundError, KeyError):
                print("Name not found.")
        else:
            print("Unknown command. Type 'help'.")
