#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons
import os, random

#------------------------------------------------#

def _rand_seed(seed: int) -> int:
    """Retourne une graine exploitable. Si seed < 0 => graine forte aléatoire."""
    if seed is None or seed < 0:
        return int.from_bytes(os.urandom(8), "little")
    return int(seed)

#------------------------------------------------#

class RIN_RandomCFG:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "min_cfg": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 20.0, "step": 0.1}),
                "max_cfg": ("FLOAT", {"default": 12.0, "min": 1.2, "max": 20.0, "step": 0.1}),
            },
            "optional": {
                "decimals": ("INT",   {"default": 1, "min": 0, "max": 6}),
                "seed":     ("INT",   {"default": -1, "min": -1, "max": 2**31 - 1}),
            },
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("cfg",)
    CATEGORY = icons.get("MyNodes/Prompt")
    FUNCTION = "random_cfg"

    def random_cfg(self, min_cfg: float, max_cfg: float, decimals: int = 1, seed: int = -1):
        # Assure min <= max
        if min_cfg > max_cfg:
            min_cfg, max_cfg = max_cfg, min_cfg

        # Graine locale (n'affecte pas le RNG global)
        rng = random.Random(_rand_seed(seed))

        # Tirage uniforme + arrondi
        value = rng.uniform(min_cfg, max_cfg)
        decimals = max(0, min(int(decimals), 6))
        value = round(value, decimals)

        return (float(value),)
