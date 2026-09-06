from .Architecture import icons

class RIN_CFGSteps:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "steps": ("INT", {
                    "default": 20, 
                    "min": 1, 
                    "max": 150, 
                    "step": 1,
                }),
                "cfg": ("FLOAT", {
                    "default": 7, 
                    "min": 0.0, 
                    "max": 30.0, 
                    "step": 0.5,
                }),
            }
        }

    RETURN_TYPES = ("INT", "FLOAT")
    RETURN_NAMES = ("Steps", "CFG")
    FUNCTION = "CFG_STEPS_OUT"
    CATEGORY = icons.get("MyNodes/Utils")

    def CFG_STEPS_OUT(self, steps, cfg):
        return (steps, cfg)