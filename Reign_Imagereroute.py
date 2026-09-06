from .Architecture import icons

class Reign_Imagereroute:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")
    FUNCTION = "pass_through"
    CATEGORY = icons.get("MyNodes/Utils")

    def pass_through(self, image, mask):
        return (image, mask)