#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons
import os, csv, random
from typing import List

#------------------------------------------------#

CSV_DIR_NAME = "CSV"
EYES_CSV_FILENAME = "eyes.csv"  # <addon_root>/CSV/eyes.csv

def _addon_root() -> str:
    """Return the addon root folder (parent of this 'nodes' folder)."""
    here = os.path.abspath(os.path.dirname(__file__))
    parent = os.path.dirname(here)
    return parent

def _csv_dir() -> str:
    """Return the absolute path to <addon_root>/CSV (doesn't create it)."""
    return os.path.join(_addon_root(), CSV_DIR_NAME)

def _rand_seed(seed: int) -> int:
    if seed is None or seed < 0:
        return int.from_bytes(os.urandom(8), "little")
    return seed

#------------------------------------------------#

class RIN_RandomPrompt3:
    
    """
    Node dédié aux yeux :
    - lit toujours CSV/eyes.csv
    - séparateur CSV fixe: ','
    - assemble les tokens avec ', ' (virgule + espace)
    - pas de strip; 'ignore_blank' filtre les valeurs vides ou uniquement espaces
    """

    @classmethod
    def INPUT_TYPES(cls):
        # Plus de choix de fichier: c'est toujours eyes.csv
        return {
            "required": {},
            "optional": {
                "max_columns": ("INT", {
                    "default": 0, "min": 0, "max": 2**31 - 1, "step": 1,
                    "tooltip": "0 = utiliser toutes les colonnes détectées; sinon limite aux N premières."
                }),
                "seed": ("INT", {
                    "default": -1, "min": -1, "max": 2**31 - 1,
                    "tooltip": "Seed déterministe (>=0). Utiliser -1 pour du hasard frais."
                }),
                "ignore_blank": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Ignorer les valeurs vides / composées uniquement d'espaces ?"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = icons.get("MyNodes/Prompt")

    # ---------- internals ----------

    def _load_columns_dynamic(self, path: str, ignore_blank: bool) -> List[List[str]]:
        """
        Lit le CSV (séparateur ',') et renvoie une liste de colonnes de longueur VARIABLE.
        Écarte les colonnes entièrement vides.
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

    def _pick_per_column(self, rng: random.Random, cols: List[List[str]]) -> List[str]:
        """Tire 1 item par colonne; si une colonne est vide, renvoie ''."""
        return [rng.choice(col) if col else "" for col in cols]

    # ---------- entrypoint ----------

    def generate(self,
                 max_columns=0,
                 seed=-1,
                 ignore_blank=True):

        csv_dir = _csv_dir()
        csv_path = os.path.join(csv_dir, EYES_CSV_FILENAME)

        if not os.path.isfile(csv_path):
            # Message clair si le fichier n'existe pas
            return (f"[RIN_RandomEyes] CSV introuvable : {EYES_CSV_FILENAME} (attendu dans {CSV_DIR_NAME}/)",)

        cols_all = self._load_columns_dynamic(csv_path, bool(ignore_blank))
        if not cols_all:
            self._prev_text = ""
            self._prev_seed_input = seed
            self.last_text = ""
            return ("",)

        # clamp max_columns
        try:
            mc = int(max_columns)
        except Exception:
            mc = 0
        if mc < 0:
            mc = 0
        cols = cols_all if mc == 0 else cols_all[:min(mc, len(cols_all))]

        rng = random.Random(_rand_seed(seed))
        chosen = self._pick_per_column(rng, cols)

        # jonction fixe: ", "
        tokens = [t for t in chosen if t and not t.isspace()]
        text = ", ".join(tokens) if tokens else ""

        # anti-répétition si seed change
        prev_text = getattr(self, "_prev_text", None)
        prev_seed_in = getattr(self, "_prev_seed_input", None)
        same_fixed_seed = (seed >= 0 and prev_seed_in == seed)
        avoid_repeat = not same_fixed_seed
        has_alternative = any(len(set(col)) > 1 for col in cols)

        if avoid_repeat and prev_text is not None and text == prev_text and has_alternative:
            for _ in range(16):
                chosen_try = self._pick_per_column(rng, cols)
                tokens_try = [t for t in chosen_try if t and not t.isspace()]
                text_try = ", ".join(tokens_try) if tokens_try else ""
                if text_try != prev_text:
                    text = text_try
                    break

        self._prev_text = text
        self._prev_seed_input = seed
        self.last_text = text
        return (text,)
