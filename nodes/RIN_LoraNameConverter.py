#------------------------------------------------#
# Imports                                        #
#------------------------------------------------#

from ..Architecture import icons
from .RIN_AnyType import any_type

#------------------------------------------------#
# Utility functions                              #
#------------------------------------------------#


class RIN_LoraNameConverter:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "lora_data": (any_type,),
            }
        }

    RETURN_TYPES = ("any_type",)
    RETURN_NAMES = ("lora_name",)
    FUNCTION = "RIN_LoraNameConverter"
    CATEGORY = icons.get("MyNodes/Utils")

    def RIN_LoraNameConverter(self, lora_data):
        if not isinstance(lora_data, list):
            return ([],)

        names = []
        for item in lora_data:
            if isinstance(item, (list, tuple)) and len(item) > 0:
                names.append(item[0])

        return (names,)