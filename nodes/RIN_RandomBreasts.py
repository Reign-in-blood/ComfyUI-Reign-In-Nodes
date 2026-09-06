#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons
import os, csv, random
from typing import List

#------------------------------------------------#

CSV_DIR_NAME = "CSV"
BREASTS_CSV_FILENAME = "breasts.csv"  # <addon_root>/CSV/breasts.csv

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

class RIN_RandomBreasts:
    """
    Node dédié au prompt 'breasts' lié à CSV/breasts.csv (séparateur ',').

    Ordre des colonnes attendu (index 0..6) :
      0: size
      1: shape
      2: nipples
      3: areolas
      4: accessories
      5: motion
      6: view angles

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
                "use_size": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'size' (col 0)"}),
                "use_shape": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'shape' (col 1)"}),
                "use_nipples": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'nipples' (col 2)"}),
                "use_areolas": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'areolas' (col 3)"}),
                "use_accessories": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'accessories' (col 4)"}),
                "use_motion": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'motion' (col 5)"}),
                "use_view_angles": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'view angles' (col 6)"}),

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
                 use_size=True,
                 use_shape=True,
                 use_nipples=True,
                 use_areolas=True,
                 use_accessories=True,
                 use_motion=True,
                 use_view_angles=True,
                 seed=-1,
                 ignore_blank=True):

        csv_path = os.path.join(_csv_dir(), BREASTS_CSV_FILENAME)
        if not os.path.isfile(csv_path):
            return (f"[RIN_RandomBreasts] CSV introuvable : {BREASTS_CSV_FILENAME} (attendu dans {CSV_DIR_NAME}/)",)

        all_cols = self._read_all_columns(csv_path, bool(ignore_blank))

        # Map index -> activation
        toggle_by_index = {
            0: bool(use_size),
            1: bool(use_shape),
            2: bool(use_nipples),
            3: bool(use_areolas),
            4: bool(use_accessories),
            5: bool(use_motion),
            6: bool(use_view_angles),
        }

        # Sélectionne les colonnes demandées, dans l'ordre 0..6, si elles existent
        selected_cols: List[List[str]] = []
        for idx in range(7):
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
