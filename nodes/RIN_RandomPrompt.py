#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons

import os, csv, random
from typing import List

#------------------------------------------------#

CSV_DIR_NAME = "CSV"  # read CSV files from <addon_root>/CSV

def _addon_root() -> str:
    """Return the addon root folder (parent of this 'nodes' folder)."""
    here = os.path.abspath(os.path.dirname(__file__))
    # Common structure is <addon_root>/nodes/this_file.py
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

class RIN_RandomPrompt:

    @classmethod
    def INPUT_TYPES(cls):
        csv_files = _list_csv_files() or ["<place_csv_files_in: ADDON_ROOT/CSV>"]
        return {
            "required": {
                "csv_file": (csv_files, {
                    "tooltip": "CSV file to read (put files under your addon's 'CSV/' folder)."
                }),
                "column_index": ("INT", {
                    "default": 0, "min": 0, "max": 1024, "step": 1,
                    "tooltip": "Zero-based column index (0 = first column)."
                }),
            },
            "optional": {
                "separator": (["comma(,)", "semicolon(;)", "pipe(|)", "tab(\\t)"], {
                    "default": "comma(,)", "tooltip": "CSV delimiter."
                }),
                "has_header": ("BOOLEAN", {
                    "default": True, "tooltip": "Skip the first row as header?"
                }),
                "picks": ("INT", {
                    "default": 1, "min": 1, "max": 64, "step": 1,
                    "tooltip": "How many items to draw and concatenate."
                }),
                "join_with": ("STRING", {
                    "default": " ", "tooltip": "Separator used to join picked items."
                }),
                "seed": ("INT", {
                    "default": -1, "min": -1, "max": 2**31 - 1,
                    "tooltip": "Deterministic seed (>=0). Use -1 for fresh randomness."
                }),
                "strip_items": ("BOOLEAN", {
                    "default": True, "tooltip": "Trim surrounding whitespace from items?"
                }),
                "ignore_blank": ("BOOLEAN", {
                    "default": True, "tooltip": "Ignore empty/blank values in the column?"
                }),
                "unique_picks": ("BOOLEAN", {
                    "default": False, "tooltip": "Pick distinct items when possible."
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

    def _load_column(self, path: str, col: int, sep: str,
                     has_header: bool, strip_items: bool, ignore_blank: bool) -> List[str]:
        items = []
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter=sep)
            first = True
            for row in reader:
                if not row:
                    continue
                if first and has_header:
                    first = False
                    continue
                first = False
                if col >= len(row):
                    continue
                val = row[col]
                if strip_items:
                    val = val.strip()
                if ignore_blank and (val == "" or val.isspace()):
                    continue
                items.append(val)
        return items

    def generate(self,
                 csv_file, column_index,
                 separator="comma(,)", has_header=True,
                 picks=1, join_with=" ",
                 seed=-1, strip_items=True, ignore_blank=True,
                 unique_picks=False):
        csv_dir = _csv_dir()
        csv_path = os.path.join(csv_dir, csv_file)

        if not os.path.isfile(csv_path):
            text = f"[RIN_RandomCSVPrompt] CSV not found: {csv_file} (expected under {CSV_DIR_NAME}/)"
            return (text,)

        sep = self._sep_from_choice(separator)
        pool = self._load_column(csv_path, int(column_index), sep, bool(has_header),
                                 bool(strip_items), bool(ignore_blank))

        if not pool:
            text = f"[RIN_RandomCSVPrompt] Column {column_index} has no usable values."
            return (text,)

        rng = random.Random(_rand_seed(seed))
        n = max(1, int(picks))

        if unique_picks and n <= len(set(pool)):
            # preserve order uniqueness using dict.fromkeys
            chosen = rng.sample(list(dict.fromkeys(pool)), n)
        else:
            chosen = [rng.choice(pool) for _ in range(n)]

        text = join_with.join(chosen)
        self.last_text = text  # shows up in the node's preview
        return (text,)