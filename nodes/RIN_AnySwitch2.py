#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons
from .RIN_AnyType import any_type

#------------------------------------------------#

def is_none(value):
    return value is None


class RIN_AnySwitch2:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "any_1": (any_type, {}),
                "any_2": (any_type, {}),
            },
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("*",)
    FUNCTION = "RIN_AnySwitch2"
    CATEGORY = icons.get("MyNodes/Utils")

    def RIN_AnySwitch2(self, any_1=None, any_2=None):
        """Outputs the first non-empty input (any_1 then any_2)."""
        if not is_none(any_1):
            return (any_1,)
        if not is_none(any_2):
            return (any_2,)
        return (None,)
