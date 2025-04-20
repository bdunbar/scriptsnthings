# Big‑Five “Drift Engine”

A tiny command‑line tool that lets fictional characters **take a 10‑item
Big‑Five (OCEAN) questionnaire once,** then **drift** their personality scores
slightly at each chapter break—exactly the way you might nudge
characters’ arcs over time.  
Optionally, threshold crossings (> 70 or < 30) trigger customizable story‑event
prompts (think of them as lightweight “plot oracles”).

---

## Features

* **TIPI baseline interview**  
  Uses the Ten‑Item Personality Inventory (TIPI), license‑free,
  to capture starting traits.

* **Cumulative drift**  
  Each `next NAME` command adds a –2…+2 random “nudge” to all
  ten raw answers, then rescales to a 0‑100 Big‑Five profile.

* **Threshold event hooks**  
  If a trait rises above 70 (“High‑Extraversion”) or falls below
  30 (“Low‑Conscientiousness”), the script prints story prompts you define
  in a single `EVENTS` dict.

* **Persistent state**  
  All raw TIPI answers live in `personality_state.csv` so drift is permanent
  across writing sessions.

* **No external dependencies** beyond `pandas` (Python 3.8+).

---

## Quick‑start

```bash
git clone
cd your‑repo
pip install pandas   # inside a venv is best
python personality_engine.py```

---
