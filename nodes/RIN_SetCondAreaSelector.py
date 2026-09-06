#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons
from .RIN_AnyType import any_type

#------------------------------------------------#

class RIN_SetCondAreaSelector:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "set_cond_area": (
                    ["default", "mask bounds"],
                    {"default": "default"}
                ),
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("set_cond_area",)
    FUNCTION = "select"
    CATEGORY = icons.get("MyNodes/Utils")

    def select(self, set_cond_area):
        return (set_cond_area,)