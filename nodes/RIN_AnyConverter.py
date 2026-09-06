#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons
from .RIN_AnyType import any_type

#------------------------------------------------#
#Node                                            #
#------------------------------------------------#

class RIN_AnyConverter:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {},
            "optional": {
                "any_type_input": (
                    any_type,
                    {"forceInput": True},
                ),
            },
        }

    RETURN_TYPES = (any_type,)

    RETURN_NAMES = ("ANY_TYPE_OUTPUT",)

    FUNCTION = "AnyConverter"
    CATEGORY = icons.get("MyNodes/Utils")

    def AnyConverter(self, any_type_input: str = ""):
        return (any_type_input,)