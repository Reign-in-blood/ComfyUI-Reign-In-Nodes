from .Architecture import icons

class SimpleStringNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
               "input_text": (
                    "STRING", {
                    "multiline" : True,   
                    "default": "",
                    }
                )
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output_text",)
    FUNCTION = "process_text"
    CATEGORY = icons.get("MyNodes/Prompt")

    def process_text(self, input_text):
        return (input_text,)