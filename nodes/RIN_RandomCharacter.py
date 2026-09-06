#------------------------------------------------#
# Imports                                       #
#------------------------------------------------#

from ..Architecture import icons

import os, csv, random
from typing import List

#------------------------------------------------#

CSV_ROOT_DIR_NAME = "CSV"        # <addon_root>/CSV
CHARACTER_DIR_NAME = "character" # <addon_root>/CSV/character

def _addon_root() -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    parent = os.path.dirname(here)
    return parent

def _character_csv_dir() -> str:
    """
    Returns the directory where character CSV files are stored:
    <addon_root>/CSV/character
    """
    return os.path.join(_addon_root(), CSV_ROOT_DIR_NAME, CHARACTER_DIR_NAME)

def _rand_seed(seed: int) -> int:
    """
    If seed is None or negative, generate a random seed from os.urandom.
    Otherwise use the given seed.
    """
    if seed is None or seed < 0:
        return int.from_bytes(os.urandom(8), "little")
    return seed

def _list_character_csv_files() -> List[str]:
    """
    Returns a list of CSV filenames available in the character CSV directory:
    <addon_root>/CSV/character

    Each file corresponds to a character category
    (Nintendo, Pokemon, Zelda, Disney, etc.).
    """
    directory = _character_csv_dir()

    try:
        files = os.listdir(directory)
    except FileNotFoundError:
        return []

    csv_files = []
    for f in files:
        if f.lower().endswith(".csv"):
            csv_files.append(f)
    csv_files.sort()
    return csv_files

def _load_rows(csv_filename: str) -> List[List[str]]:
    """
    Loads all non-empty, non-comment rows from the given CSV file
    located in <addon_root>/CSV/character.

    A row is skipped if:
      - it is empty
      - first non-empty cell starts with '#'
    """
    path = os.path.join(_character_csv_dir(), csv_filename)
    rows: List[List[str]] = []

    if not os.path.isfile(path):
        return rows

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            # Strip whitespace from each cell
            cleaned = [c.strip() for c in row]
            # Skip completely empty rows
            if not any(cleaned):
                continue
            # Skip commented rows (first non-empty cell starts with '#')
            first_non_empty = next((c for c in cleaned if c != ""), None)
            if first_non_empty is not None and first_non_empty.startswith("#"):
                continue
            rows.append(cleaned)

    return rows

#------------------------------------------------#

class RIN_RandomCharacter:
    """
    Node that returns a random known character prompt based on CSV files
    stored in <addon_root>/CSV/character.

    Each CSV file corresponds to a character category (Nintendo, Pokemon,
    Zelda, Disney, etc.) and must follow this column order (indexes 0..4):

      0: character name
      1: hair details
      2: body details
      3: clothing details
      4: background details

    All text should be written in English inside the CSV.
    """

    @classmethod
    def INPUT_TYPES(cls):
        csv_files = _list_character_csv_files()
        if not csv_files:
            # Fallback placeholder if no CSV is found
            csv_files = ["<no character CSV found>"]

        return {
            "required": {
                "category_csv": (
                    csv_files,
                    {
                        "default": csv_files[0],
                        "tooltip": "Choose the CSV file (category) for random characters, from CSV/character."
                    }
                ),
                "use_name": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "label": "Use character name"
                    }
                ),
                "use_hair": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "label": "Use hair details"
                    }
                ),
                "use_body": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "label": "Use body details"
                    }
                ),
                "use_clothing": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "label": "Use clothing details"
                    }
                ),
                "use_background": (
                    "BOOLEAN",
                    {
                        "default": True,
                        "label": "Use background details"
                    }
                ),
                # Seed tout en bas du node
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": -1,
                        "max": 2**31 - 1,
                        "step": 1,
                        "tooltip": "Random seed. Use -1 for a fully random seed."
                    }
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("character_prompt",)
    FUNCTION = "run"
    CATEGORY = "RIN/Prompt"

    ICON = icons.RIN_DICE if hasattr(icons, "RIN_DICE") else "⚄"

    def run(
        self,
        category_csv: str,
        use_name: bool,
        use_hair: bool,
        use_body: bool,
        use_clothing: bool,
        use_background: bool,
        seed: int,
    ):
        # Handle the placeholder case
        if category_csv == "<no character CSV found>":
            return ("",)

        # Prepare RNG
        rnd = random.Random(_rand_seed(seed))

        # Load rows from selected CSV inside CSV/character
        rows = _load_rows(category_csv)
        if not rows:
            # If file is missing or empty, just return an empty string
            return ("",)

        # Pick one random row
        row = rnd.choice(rows)

        # Make sure we have at least 5 columns (fill missing with empty strings)
        while len(row) < 5:
            row.append("")

        character_name   = row[0].strip()
        hair_details     = row[1].strip()
        body_details     = row[2].strip()
        clothing_details = row[3].strip()
        background       = row[4].strip()

        parts: List[str] = []

        if use_name and character_name:
            parts.append(character_name)

        if use_hair and hair_details:
            parts.append(hair_details)

        if use_body and body_details:
            parts.append(body_details)

        if use_clothing and clothing_details:
            parts.append(clothing_details)

        if use_background and background:
            parts.append(background)

        separator = ", "

        prompt = separator.join(parts)

        return (prompt,)
