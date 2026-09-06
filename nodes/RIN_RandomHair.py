#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons
import os, csv, random
from typing import List

#------------------------------------------------#

CSV_DIR_NAME = "CSV"
HAIR_CSV_FILENAME = "hair.csv"  # <addon_root>/CSV/hair.csv

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

class RIN_RandomHair:
    """
    Node dédié aux cheveux, lié à CSV/hair.csv (séparateur ',').

    Ordre des colonnes attendu (index 0..7) :
      0: Color
      1: Color style
      2: length
      3: hair cut
      4: accessories
      5: tail/pony tail
      6: Hat / crown
      7: animal ear

    Options: cases à cocher pour inclure/exclure chaque colonne.
    Assemblage des éléments: ", "
    Anti-répétition si la seed change (ou seed < 0).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                # Switches dans l'ordre exact des colonnes
                "use_color": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'Color' (col 0)"}),
                "use_color_style": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'Color style' (col 1)"}),
                "use_length": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'length' (col 2)"}),
                "use_hair_cut": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'hair cut' (col 3)"}),
                "use_accessories": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'accessories' (col 4)"}),
                "use_tail_pony": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'tail/pony tail' (col 5)"}),
                "use_hat_crown": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'Hat / crown' (col 6)"}),
                "use_animal_ear": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'animal ear' (col 7)"}),

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
        """
        Lit toutes les colonnes du CSV (séparateur ',') et retourne une liste de colonnes (listes de valeurs).
        Les colonnes entièrement vides sont retirées.
        """
        cols: List[List[str]] = []
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                if not row:
                    continue
                if len(row) > len(cols):
                    cols.extend([[] for _ in range(len(row) - len(cols))])
                for i, val in enumerate(row):
                    if ignore_blank and (val == "" or val.isspace()):
                        continue
                    cols[i].append(val)
        return [c for c in cols if len(c) > 0]

    def _pick_one(self, rng: random.Random, col: List[str]) -> str:
        return rng.choice(col) if col else ""

    # ---------- entrypoint ----------

    def generate(self,
                 use_color=True,
                 use_color_style=True,
                 use_length=True,
                 use_hair_cut=True,
                 use_accessories=True,
                 use_tail_pony=True,
                 use_hat_crown=True,
                 use_animal_ear=True,
                 seed=-1,
                 ignore_blank=True):

        csv_path = os.path.join(_csv_dir(), HAIR_CSV_FILENAME)
        if not os.path.isfile(csv_path):
            return (f"[RIN_RandomHair2] CSV introuvable : {HAIR_CSV_FILENAME} (attendu dans {CSV_DIR_NAME}/)",)

        all_cols = self._read_all_columns(csv_path, bool(ignore_blank))

        # Map index -> activation
        toggle_by_index = {
            0: bool(use_color),
            1: bool(use_color_style),
            2: bool(use_length),
            3: bool(use_hair_cut),
            4: bool(use_accessories),
            5: bool(use_tail_pony),
            6: bool(use_hat_crown),
            7: bool(use_animal_ear),
        }

        # Sélectionne les colonnes demandées, dans l'ordre 0..7, si elles existent
        selected_cols: List[List[str]] = []
        for idx in range(8):
            if toggle_by_index.get(idx, False) and idx < len(all_cols):
                selected_cols.append(all_cols[idx])
            # si activée mais absente, on ignore

        if not selected_cols:
            self._prev_text = ""
            self._prev_seed_input = seed
            self.last_text = ""
            return ("",)

        rng = random.Random(_rand_seed(seed))
        picks = [self._pick_one(rng, col) for col in selected_cols]

        # Nettoyage + jonction ", "
        tokens = [t for t in picks if t and not t.isspace()]
        text = ", ".join(tokens) if tokens else ""

        # Anti-répétition si seed change
        prev_text = getattr(self, "_prev_text", None)
        prev_seed_in = getattr(self, "_prev_seed_input", None)
        same_fixed_seed = (seed >= 0 and prev_seed_in == seed)
        avoid_repeat = not same_fixed_seed
        has_alternative = any(len(set(col)) > 1 for col in selected_cols)

        if avoid_repeat and prev_text is not None and text == prev_text and has_alternative:
            for _ in range(16):
                picks_try = [self._pick_one(rng, col) for col in selected_cols]
                tokens_try = [t for t in picks_try if t and not t.isspace()]
                text_try = ", ".join(tokens_try) if tokens_try else ""
                if text_try != prev_text:
                    text = text_try
                    break

        self._prev_text = text
        self._prev_seed_input = seed
        self.last_text = text
        return (text,)
