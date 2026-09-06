#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons
import os, csv, random
from typing import List

#------------------------------------------------#

CSV_DIR_NAME = "CSV"  

def _addon_root() -> str:
    """Return the addon root folder (parent of this 'nodes' folder)."""
    here = os.path.abspath(os.path.dirname(__file__))
    parent = os.path.dirname(here)
    return parent

def _csv_dir() -> str:
    """Return the absolute path to <addon_root>/CSV (doesn't create it)."""
    return os.path.join(_addon_root(), CSV_DIR_NAME)

def _list_csv_files() -> List[str]:
    csv_dir = _csv_dir()
    if not os.path.isdir(csv_dir):
        return []
    return sorted([
        f for f in os.listdir(csv_dir)
        if os.path.isfile(os.path.join(csv_dir, f)) and f.lower().endswith(".csv")
    ])

def _rand_seed(seed: int) -> int:
    if seed is None or seed < 0:
        return int.from_bytes(os.urandom(8), "little")
    return seed

#------------------------------------------------#

class RIN_RandomPrompt2:

    @classmethod
    def INPUT_TYPES(cls):
        csv_files = _list_csv_files() or ["<place_csv_files_in: ADDON_ROOT/CSV>"]
        return {
            "required": {
                "csv_file": (csv_files, {
                    "tooltip": "CSV file to read (put files under your addon's 'CSV/' folder)."
                }),
            },
            "optional": {
                "separator": (["comma(,)", "semicolon(;)", "pipe(|)", "tab(\\t)"], {
                    "default": "comma(,)", "tooltip": "CSV delimiter."
                }),
                "join_with": ("STRING", {
                    "default": " ", "tooltip": "Separator used to join the picks (one per detected column)."
                }),
                # élargir le max pour éviter l'erreur de validation UI
                "max_columns": ("INT", {
                    "default": 0, "min": 0, "max": 2**31 - 1, "step": 1,
                    "tooltip": "0 = use all detected columns; otherwise cap to the first N columns."
                }),
                "seed": ("INT", {
                    "default": -1, "min": -1, "max": 2**31 - 1,
                    "tooltip": "Deterministic seed (>=0). Use -1 for fresh randomness."
                }),
                "strip_items": ("BOOLEAN", {
                    "default": True, "tooltip": "Trim surrounding whitespace from items?"
                }),
                "ignore_blank": ("BOOLEAN", {
                    "default": True, "tooltip": "Ignore empty/blank values?"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = icons.get("MyNodes/Prompt")

    @staticmethod
    def _sep_from_choice(choice: str) -> str:
        return {
            "comma(,)": ",",
            "semicolon(;)": ";",
            "pipe(|)": "|",
            "tab(\\t)": "\t",
        }.get(choice, ",")

    def _load_columns_dynamic(self, path: str, sep: str,
                              strip_items: bool, ignore_blank: bool) -> List[List[str]]:
        """
        Lit le CSV et renvoie une liste de colonnes de longueur VARIABLE.
        Chaque élément de la liste représente une colonne et contient les valeurs non-vides rencontrées.
        Les colonnes entièrement vides sont écartées automatiquement.
        """
        cols: List[List[str]] = []
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter=sep)
            for row in reader:
                if not row:
                    continue
                # Étendre cols si la ligne a plus de colonnes que prévu
                if len(row) > len(cols):
                    cols.extend([[] for _ in range(len(row) - len(cols))])
                # Ajouter les valeurs
                for i, val in enumerate(row):
                    if strip_items:
                        val = val.strip()
                    if ignore_blank and (val == "" or val.isspace()):
                        continue
                    cols[i].append(val)
        # Supprimer les colonnes entièrement vides
        cols = [c for c in cols if len(c) > 0]
        return cols

    def _pick_per_column(self, rng: random.Random, cols: List[List[str]]) -> List[str]:
        """Tire un item par colonne; si une colonne est vide (théoriquement non après filtre), renvoie ''."""
        res = []
        for col in cols:
            if col:
                res.append(rng.choice(col))
            else:
                res.append("")
        return res

    def generate(self,
                 csv_file,
                 separator="comma(,)",
                 join_with=" ",
                 max_columns=0,
                 seed=-1, strip_items=True, ignore_blank=True):

        csv_dir = _csv_dir()
        csv_path = os.path.join(csv_dir, csv_file)

        if not os.path.isfile(csv_path):
            text = f"[RIN_RandomCSVPrompt] CSV not found: {csv_file} (expected under {CSV_DIR_NAME}/)"
            return (text,)

        sep = self._sep_from_choice(separator)
        cols_all = self._load_columns_dynamic(csv_path, sep, bool(strip_items), bool(ignore_blank))

        if not cols_all:
            # aucune donnée exploitable
            self._prev_text = ""
            self._prev_seed_input = seed
            self.last_text = ""
            return ("",)

        # -- Sanitize + clamp max_columns --
        try:
            mc = int(max_columns)
        except Exception:
            mc = 0
        if mc < 0:
            mc = 0
        # on limite toujours à la réalité du CSV
        if mc == 0:
            cols = cols_all
        else:
            # clamp dur à la taille réelle
            mc = min(mc, len(cols_all))
            cols = cols_all[:mc]

        rng = random.Random(_rand_seed(seed))

        # Tirage initial: 1 pick par colonne détectée
        chosen = self._pick_per_column(rng, cols)

        # Filtrer les vides pour éviter les séparateurs en trop
        tokens = [t for t in chosen if t and not t.isspace()]
        text = join_with.join(tokens) if tokens else ""

        # --- Anti-répétition UNIQUEMENT si la seed change (ou seed < 0) ---
        prev_text = getattr(self, "_prev_text", None)
        prev_seed_in = getattr(self, "_prev_seed_input", None)
        same_fixed_seed = (seed >= 0 and prev_seed_in == seed)
        avoid_repeat = not same_fixed_seed  # seed différente ou -1 → éviter répétition

        # Alternative possible si AU MOINS une colonne a ≥ 2 valeurs distinctes
        has_alternative = any(len(set(col)) > 1 for col in cols)

        if avoid_repeat and prev_text is not None and text == prev_text and has_alternative:
            for _ in range(16):
                chosen_try = self._pick_per_column(rng, cols)
                tokens_try = [t for t in chosen_try if t and not t.isspace()]
                text_try = join_with.join(tokens_try) if tokens_try else ""
                if text_try != prev_text:
                    text = text_try
                    break

        # Mémorisation pour l'appel suivant
        self._prev_text = text
        self._prev_seed_input = seed
        self.last_text = text
        return (text,)
