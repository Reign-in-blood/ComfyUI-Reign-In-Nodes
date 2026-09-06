#------------------------------------------------#
# Importations                                   #
#------------------------------------------------#

from ..Architecture import icons

#------------------------------------------------#


class RIN_TextAppend:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                # IMPORTANT : fournir un dict d'options (au moins "default")
                "Text": ("STRING", {"forceInput": True}),
                "text_field": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)      # (facultatif mais pratique dans l'UI)
    CATEGORY = icons.get("MyNodes/Prompt")
    FUNCTION = "append_text"

    def append_text(self, text_field, Text=""):

        if Text and text_field:
            result = f"{Text}, {text_field}"
        elif Text:
            result = Text
        else:
            result = text_field
        return (result,)