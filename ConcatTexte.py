from .Architecture import icons

class RIN_ConcatText:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "text": ("STRING", {"default": "Input_Text", "multiline": False}),
                "extra_text": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("STRING", )
    FUNCTION = "RIN_concat_texts"
    CATEGORY = icons.get("MyNodes/Utils")

    def RIN_concat_texts(self, text, extra_text):
        return (text + extra_text,)