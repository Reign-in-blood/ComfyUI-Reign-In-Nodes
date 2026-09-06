#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons
import os, csv, random
from typing import List

#------------------------------------------------#

CSV_DIR_NAME = "CSV"
BACKGROUND_CSV_FILENAME = "background.csv"  # <addon_root>/CSV/background.csv

def _addon_root() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    parent = os.path.dirname(here)
    return parent

def _csv_dir() -> str:
    return os.path.join(_addon_root(), CSV_DIR_NAME)

def _rand_seed(seed: int) -> int:
    if seed is None or seed < 0:
        return int.from_bytes(os.urandom(8), "little")
    return seed

#------------------------------------------------#

class RIN_RandomBackground:
    """
    Node dédié au prompt 'background' lié à CSV/background.csv (séparateur ',').

    Colonnes attendues dans le CSV (index 0..7) :
      0: setting
      1: location
      2: time
      3: weather
      4: mood
      5: lighting
      6: style
      7: simple

    Le champ 'indoor/outdoor' est géré directement dans le node.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                # Sélecteur interne (hors CSV)
                "indoor_mode": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "Indoor scene? (otherwise outdoor)"
                }),

                # Cases à cocher pour colonnes CSV
                "use_setting": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'setting' (col 0)"}),
                "use_location": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'location' (col 1)"}),
                "use_time": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'time' (col 2)"}),
                "use_weather": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'weather' (col 3)"}),
                "use_mood": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'mood' (col 4)"}),
                "use_lighting": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'lighting' (col 5)"}),
                "use_style": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'style' (col 6)"}),
                "use_simple": ("BOOLEAN", {"default": False, "tooltip": "Inclure 'simple' (col 7)"}),

                # Contrôles généraux
                "seed": ("INT", {
                    "default": -1, "min": -1, "max": 2**31 - 1,
                    "tooltip": "Seed déterministe (>=0). -1 pour hasard à chaque exécution."
                }),
                "ignore_blank": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Ignorer les valeurs vides / uniquement espaces ?"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = icons.get("MyNodes/Prompt")

    # ---------- internals ----------

    def _read_all_columns(self, path: str, ignore_blank: bool) -> List[List[str]]:
        cols: List[List[str]] = []
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                if not row:
                    continue
                if len(row) > len(cols):
                    cols.extend([[] for _ in range(len(row) - len(cols))])
                for i, val in enumerate(row):
                    if ignore_blank and (val == "" or str(val).isspace()):
                        continue
                    cols[i].append(val)
        return cols

    def _pick_one(self, rng: random.Random, col: List[str]) -> str:
        valid = [v.strip() for v in col if v and not str(v).isspace()]
        return rng.choice(valid) if valid else ""

    # ---------- main ----------

    def generate(self,
                 indoor_mode=False,
                 use_setting=True,
                 use_location=True,
                 use_time=True,
                 use_weather=True,
                 use_mood=True,
                 use_lighting=True,
                 use_style=True,
                 use_simple=False,
                 seed=-1,
                 ignore_blank=True):

        csv_path = os.path.join(_csv_dir(), BACKGROUND_CSV_FILENAME)
        if not os.path.isfile(csv_path):
            return (f"[RIN_RandomBackground] CSV introuvable : {BACKGROUND_CSV_FILENAME} (attendu dans {CSV_DIR_NAME}/)",)

        all_cols = self._read_all_columns(csv_path, bool(ignore_blank))

        toggle_by_index = {
            0: use_setting,
            1: use_location,
            2: use_time,
            3: use_weather,
            4: use_mood,
            5: use_lighting,
            6: use_style,
            7: use_simple,
        }

        selected_cols = [
            all_cols[i] for i in range(len(all_cols))
            if toggle_by_index.get(i, False) and i < len(all_cols)
        ]

        if not selected_cols:
            return ("",)

        rng = random.Random(_rand_seed(seed))
        picks = [self._pick_one(rng, col) for col in selected_cols]
        tokens = [t for t in picks if t]

        # indoor / outdoor interne
        environment = "indoor" if indoor_mode else "outdoor"
        tokens.insert(0, environment)

        # Séparateur fixe : ", "
        text = ", ".join(tokens)

        # Anti-répétition si seed change
        prev_text = getattr(self, "_prev_text", None)
        prev_seed_in = getattr(self, "_prev_seed_input", None)
        same_fixed_seed = (seed >= 0 and prev_seed_in == seed)
        avoid_repeat = not same_fixed_seed
        has_alternative = any(len(set([v for v in col if v and not str(v).isspace()])) > 1 for col in selected_cols)

        if avoid_repeat and prev_text == text and has_alternative:
            for _ in range(16):
                picks_try = [self._pick_one(rng, col) for col in selected_cols]
                tokens_try = [t for t in picks_try if t]
                tokens_try.insert(0, environment)
                text_try = ", ".join(tokens_try)
                if text_try != prev_text:
                    text = text_try
                    break

        self._prev_text = text
        self._prev_seed_input = seed
        self.last_text = text
        return (text,)
