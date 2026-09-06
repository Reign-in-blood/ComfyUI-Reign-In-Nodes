#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons
import os, csv, random
from typing import List, Tuple

#------------------------------------------------#

CSV_DIR_NAME = "CSV"
ANIMAL_CSV_FILENAME = "animal_features.csv"  # <addon_root>/CSV/animal_features.csv

def _addon_root() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.dirname(here)

def _csv_dir() -> str:
    return os.path.join(_addon_root(), CSV_DIR_NAME)

def _rand_seed(seed: int) -> int:
    if seed is None or seed < 0:
        return int.from_bytes(os.urandom(8), "little")
    return seed

#------------------------------------------------#

class RIN_RandomAnimalFeatures:
    """
    Node 'animal ears / tails' (version 3)
    CSV attendu: CSV/animal_features.csv (séparateur ',')
      col 0 -> ears
      col 1 -> tails
      col 2 -> both

    Options :
      inject_animal_ear_fluff → injecte littéralement 'animal ear fluff'
      use_ears  → pioche col 0
      use_tails → pioche col 1
      use_both  → pioche col 2
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "inject_animal_ear_fluff": ("BOOLEAN", {"default": False, "tooltip": "Injecte littéralement 'animal ear fluff'"}),
                "use_ears": ("BOOLEAN",  {"default": True,  "tooltip": "Inclure col 0 (ears) depuis le CSV"}),
                "use_tails": ("BOOLEAN", {"default": False, "tooltip": "Inclure col 1 (tails) depuis le CSV"}),
                "use_both": ("BOOLEAN",  {"default": False, "tooltip": "Inclure col 2 (both) depuis le CSV"}),
                "seed": ("INT", {
                    "default": -1, "min": -1, "max": 2**31 - 1,
                    "tooltip": "Seed déterministe (>=0). -1 pour hasard à chaque exécution."
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "generate"
    CATEGORY = icons.get("MyNodes/Prompt")

    # ---------- internals ----------

    def _read_cols(self, path: str) -> Tuple[List[str], List[str], List[str]]:
        """Lit 3 colonnes (ears, tails, both). Colonnes manquantes -> []."""
        col0, col1, col2 = [], [], []
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter=",")
            for row in reader:
                if not row:
                    continue
                if len(row) > 0 and row[0].strip():
                    col0.append(row[0].strip())
                if len(row) > 1 and row[1].strip():
                    col1.append(row[1].strip())
                if len(row) > 2 and row[2].strip():
                    col2.append(row[2].strip())
        return col0, col1, col2

    def _pick(self, rng: random.Random, arr: List[str]) -> str:
        return rng.choice(arr) if arr else ""

    # ---------- entrypoint ----------

    def generate(self,
                 inject_animal_ear_fluff=False,
                 use_ears=True,
                 use_tails=False,
                 use_both=False,
                 seed=-1):

        csv_path = os.path.join(_csv_dir(), ANIMAL_CSV_FILENAME)
        parts: List[str] = []

        # Injection indépendante
        if inject_animal_ear_fluff:
            parts.append("animal ear fluff")

        # Si pas de CSV, on renvoie seulement l’injection
        if not os.path.isfile(csv_path):
            text = ", ".join(parts) if parts else f"[RIN_AnimalEarsTails3] CSV introuvable : {ANIMAL_CSV_FILENAME}"
            self._prev_text = text
            self._prev_seed_input = seed
            self.last_text = text
            return (text,)

        ears_list, tails_list, both_list = self._read_cols(csv_path)

        rng = random.Random(_rand_seed(seed))

        if use_ears:
            ear = self._pick(rng, ears_list)
            if ear:
                parts.append(ear)
        if use_tails:
            tail = self._pick(rng, tails_list)
            if tail:
                parts.append(tail)
        if use_both:
            both = self._pick(rng, both_list)
            if both:
                parts.append(both)

        # Supprime doublons tout en gardant l'ordre
        seen, dedup = set(), []
        for p in parts:
            if p not in seen:
                dedup.append(p)
                seen.add(p)

        text = ", ".join(dedup)

        # Anti-répétition si seed change
        prev_text = getattr(self, "_prev_text", None)
        prev_seed_in = getattr(self, "_prev_seed_input", None)
        same_fixed_seed = (seed >= 0 and prev_seed_in == seed)
        avoid_repeat = not same_fixed_seed

        has_alt = (
            (use_ears and len(set(ears_list)) > 1) or
            (use_tails and len(set(tails_list)) > 1) or
            (use_both and len(set(both_list)) > 1)
        )

        if avoid_repeat and prev_text is not None and text == prev_text and has_alt:
            for _ in range(16):
                parts_try = []
                if inject_animal_ear_fluff:
                    parts_try.append("animal ear fluff")
                if use_ears:
                    e = self._pick(rng, ears_list)
                    if e:
                        parts_try.append(e)
                if use_tails:
                    t = self._pick(rng, tails_list)
                    if t:
                        parts_try.append(t)
                if use_both:
                    b = self._pick(rng, both_list)
                    if b:
                        parts_try.append(b)

                seen2, dedup2 = set(), []
                for p in parts_try:
                    if p not in seen2:
                        dedup2.append(p)
                        seen2.add(p)

                text_try = ", ".join(dedup2)
                if text_try != prev_text:
                    text = text_try
                    break

        self._prev_text = text
        self._prev_seed_input = seed
        self.last_text = text
        return (text,)
