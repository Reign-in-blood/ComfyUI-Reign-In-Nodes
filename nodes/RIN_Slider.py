from ..Architecture import icons


class RIN_Slider_1:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
            },
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "rin_slider_1"
    CATEGORY = icons.get("MyNodes/Sliders")

    def rin_slider_1(self, value):
        return (value,)
    
#------------------------------------------------#

class RIN_Slider_10:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("FLOAT", {
                    "default": 5,
                    "min": 0,
                    "max": 10,
                    "step": 0.5,
                    "display": "slider"
                }),
            },
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "rin_slider_10"
    CATEGORY = icons.get("MyNodes/Sliders")

    def rin_slider_10(self, value):
        return (value,)
    
#------------------------------------------------#

class RIN_Slider_100:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("INT", {
                    "default": 50,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                    "display": "slider"
                }),
            },
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "rin_slider_100"
    CATEGORY = icons.get("MyNodes/Sliders")

    def rin_slider_100(self, value):
        return (value,)
    
#------------------------------------------------# 
 
class RIN_FloatSplitter:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ratio": (
                    "FLOAT",
                    {
                        "default": 0.5,
                        "min": 0.01,
                        "max": 0.99,
                        "step": 0.1
                    }
                ),
            }
        }

    RETURN_TYPES = ("FLOAT", "FLOAT")
    RETURN_NAMES = ("weight_a", "weight_b")
    FUNCTION = "split"
    CATEGORY = icons.get("MyNodes/Sliders")

    def split(self, ratio):
        weight_a = ratio
        weight_b = 1.0 - ratio
        return (weight_a, weight_b)