from .Architecture import icons

class AnyType(str):
    #A special type that can be connected to any other types. Credit to pythongosssss

    def __ne__(self, __value: object) -> bool:
        return False

any_type = AnyType("*")

class MyTextReplace:

    @ classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),            
                },
            "optional": {
                "find": ("STRING", {"multiline": False, "default": "character"}),
                "replace": ("STRING", {"multiline": False, "default": ""}),   
            },
        }

    RETURN_TYPES = (any_type, )
    RETURN_NAMES = ("prompt_text", )
    FUNCTION = "replacing_text"
    CATEGORY = icons.get("MyNodes/Prompt")

    def replacing_text(self, text, find="", replace=""):
        text = text.replace(find, replace)

        return (text, )