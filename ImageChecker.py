from .Architecture import icons

class ImagePresenceChecker:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("image_present",)
    FUNCTION = "check_presence"
    CATEGORY = icons.get("MyNodes/Utils")

    def check_presence(self, image=None):
        BOOLEAN = image is not None
        return (BOOLEAN,)