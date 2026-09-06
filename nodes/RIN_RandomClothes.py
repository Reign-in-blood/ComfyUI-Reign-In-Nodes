#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons
import os, csv, random
from typing import List

#------------------------------------------------#

CSV_DIR_NAME = "CSV"
CLOTHES_CSV_FILENAME = "clothes.csv"  # <addon_root>/CSV/clothes.csv

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

class RIN_RandomClothes:
    """
    Node dédié au prompt 'clothes' lié à CSV/clothes.csv (séparateur ',').

    Ordre des colonnes attendu (index 0..11) :
      0: top
      1: bottom
      2: outerwear
      3: onepiece
      4: underwear
      5: lingerie
      6: aesthetic
      7: accessory
      8: hat_crown
      9: gloves
      10: footwear
      11: full_outfit
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "use_top": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'top' (col 0)"}),
                "use_bottom": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'bottom' (col 1)"}),
                "use_outerwear": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'outerwear' (col 2)"}),
                "use_onepiece": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'onepiece' (col 3)"}),
                "use_underwear": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'underwear' (col 4)"}),
                "use_lingerie": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'lingerie' (col 5)"}),
                "use_aesthetic": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'aesthetic' (col 6)"}),
                "use_accessory": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'accessory' (col 7)"}),
                "use_hat_crown": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'hat / crown' (col 8)"}),
                "use_gloves": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'gloves' (col 9)"}),
                "use_footwear": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'footwear' (col 10)"}),
                "use_full_outfit": ("BOOLEAN", {"default": True, "tooltip": "Inclure 'full outfit' (col 11)"}),

                # Options générales
                "seed": ("INT", {
                    "default": -1, "min": -1, "max": 2**31 - 1,
                    "tooltip": "Seed déterministe (>=0). -1 = aléatoire à chaque exécution."
                }),
                "ignore_blank": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "Ignorer les valeurs vides / uniquement espaces ?"
                }),
                "joiner": ("STRING", {
                    "default": ", ",
                    "multiline": False,
                    "tooltip": "Séparateur utilisé entre les éléments assemblés."
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = icons.get("MyNodes/Prompt")

    # ---------- Internes ----------

    def _read_all_columns(self, path: str, ignore_blank: bool):
        cols = []
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

    def _pick_one(self, rng, col):
        valid = [v.strip() for v in col if v and not str(v).isspace()]
        return rng.choice(valid) if valid else ""

    # ---------- Génération ----------

    def generate(self,
                 use_top=True,
                 use_bottom=True,
                 use_outerwear=True,
                 use_onepiece=True,
                 use_underwear=True,
                 use_lingerie=True,
                 use_aesthetic=True,
                 use_accessory=True,
                 use_hat_crown=True,
                 use_gloves=True,
                 use_footwear=True,
                 use_full_outfit=True,
                 seed=-1,
                 ignore_blank=True,
                 joiner=", "):

        csv_path = os.path.join(_csv_dir(), CLOTHES_CSV_FILENAME)
        if not os.path.isfile(csv_path):
            return (f"[RIN_RandomClothes] CSV introuvable : {CLOTHES_CSV_FILENAME} (attendu dans {CSV_DIR_NAME}/)",)

        all_cols = self._read_all_columns(csv_path, bool(ignore_blank))

        toggle_by_index = {
            0: use_top,
            1: use_bottom,
            2: use_outerwear,
            3: use_onepiece,
            4: use_underwear,
            5: use_lingerie,
            6: use_aesthetic,
            7: use_accessory,
            8: use_hat_crown,
            9: use_gloves,
            10: use_footwear,
            11: use_full_outfit,
        }

        selected_cols = [all_cols[i] for i in range(len(all_cols)) if toggle_by_index.get(i, False) and i < len(all_cols)]
        if not selected_cols:
            return ("",)

        rng = random.Random(_rand_seed(seed))
        picks = [self._pick_one(rng, col) for col in selected_cols]
        tokens = [t for t in picks if t]
        text = joiner.join(tokens)

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
                text_try = joiner.join(tokens_try)
                if text_try != prev_text:
                    text = text_try
                    break

        self._prev_text = text
        self._prev_seed_input = seed
        self.last_text = text
        return (text,)
